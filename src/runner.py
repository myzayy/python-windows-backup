import json
import os
import shutil
import logging
from datetime import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from winotify import Notification

# Logging setup
logging.basicConfig(
    filename="backup_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


class BackupManager:
    def __init__(self, settings_file="settings.json"):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.settings_file = os.path.join(self.root_dir, settings_file)
        self.settings = self._load_settings()
        # Generate a unique folder name for this run
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.folder_name = f"Backup_{self.timestamp}"

    def _notify(self, title, message):
        """Displays a Windows toast notification."""
        try:
            toast = Notification(app_id="Windows Backup System", title=title, msg=message, duration="short")
            toast.show()
        except Exception as e:
            logging.error(f"Notification error: {e}")

    def _load_settings(self):
        if not os.path.exists(self.settings_file): return None
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading settings: {e}")
            return None

    def _upload_to_drive(self, files, parent_folder_id):
        """Creates a subfolder on Drive and uploads files there."""
        try:
            gauth = GoogleAuth()
            secrets_path = os.path.join(self.root_dir, "client_secrets.json")
            if not os.path.exists(secrets_path): return 0

            gauth.LoadClientConfigFile(secrets_path)
            gauth.LocalWebserverAuth()
            drive = GoogleDrive(gauth)

            # CREATING A SUBFOLDER IN THE CLOUD
            folder_metadata = {
                'title': self.folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [{'id': parent_folder_id}]
            }
            folder = drive.CreateFile(folder_metadata)
            folder.Upload()
            new_folder_id = folder['id']  # Get the ID of the newly created folder

            success = 0
            for path in files:
                if os.path.isfile(path):
                    file_name = os.path.basename(path)
                    try:
                        # Save the file to a new subfolder
                        f_drive = drive.CreateFile({
                            'title': file_name,
                            'parents': [{'id': new_folder_id}]
                        })
                        f_drive.SetContentFile(path)
                        f_drive.Upload()
                        logging.info(f"Cloud success: {file_name} in {self.folder_name}")
                        success += 1
                    except Exception as e:
                        logging.error(f"Cloud failed for {file_name}: {e}")
            return success
        except Exception as e:
            logging.error(f"General Cloud error: {e}")
            return 0

    def _copy_locally(self, files, destination):
        """Creates a local subfolder and copies files there."""
        full_dest_path = os.path.join(destination, self.folder_name)
        if not os.path.exists(full_dest_path):
            os.makedirs(full_dest_path)

        success = 0
        for path in files:
            if os.path.isfile(path):
                file_name = os.path.basename(path)
                try:
                    shutil.copy2(path, os.path.join(full_dest_path, file_name))
                    logging.info(f"Local success: {file_name} in {self.folder_name}")
                    success += 1
                except Exception as e:
                    logging.error(f"Local failed for {file_name}: {e}")
        return success

    def run(self):
        """Main process execution."""
        if not self.settings: return
        files = self.settings.get("files", [])
        if not files: return

        self._notify("Backup Started", f"Creating {self.folder_name}...")

        count = 0
        if self.settings.get("backup_to_drive", False):
            count = self._upload_to_drive(files, self.settings.get("gdrive_folder_id"))
        else:
            count = self._copy_locally(files, self.settings.get("destination"))

        self._notify("Backup Finished", f"Saved {count} files to {self.folder_name}")
        logging.info(f"Cycle complete. Target folder: {self.folder_name}")


if __name__ == "__main__":
    manager = BackupManager()
    manager.run()