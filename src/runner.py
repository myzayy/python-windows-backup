import json
import os
import shutil
import logging
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

    def _notify(self, title, message):
        """Displays a modern Windows notification using winotify."""
        try:
            toast = Notification(
                app_id="Windows Backup System",
                title=title,
                msg=message,
                duration="short"
            )
            toast.show()
        except Exception as e:
            logging.error(f"Notification error: {e}")

    def _load_settings(self):
        """Loads configuration from JSON."""
        if not os.path.exists(self.settings_file):
            logging.error(f"Settings file not found.")
            return None
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading settings: {e}")
            return None

    def _upload_to_drive(self, files, folder_id):
        """Uploads files to Google Drive."""
        try:
            gauth = GoogleAuth()
            secrets_path = os.path.join(self.root_dir, "client_secrets.json")
            if not os.path.exists(secrets_path): return 0

            gauth.LoadClientConfigFile(secrets_path)
            gauth.LocalWebserverAuth()
            drive = GoogleDrive(gauth)

            success = 0
            for path in files:
                if os.path.isfile(path):
                    file_name = os.path.basename(path)
                    try:
                        f_drive = drive.CreateFile({
                            'title': file_name,
                            'parents': [{'id': folder_id, "kind": "drive#fileLink"}]
                        })
                        f_drive.SetContentFile(path)
                        f_drive.Upload()
                        logging.info(f"Cloud success: {file_name}")
                        success += 1
                    except Exception as e:
                        logging.error(f"Cloud failed for {file_name}: {e}")
            return success
        except Exception as e:
            logging.error(f"General Cloud error: {e}")
            return 0

    def _copy_locally(self, files, destination):
        """Copies files to a local folder."""
        if not os.path.exists(destination):
            os.makedirs(destination)

        success = 0
        for path in files:
            if os.path.isfile(path):
                file_name = os.path.basename(path)
                try:
                    shutil.copy2(path, os.path.join(destination, file_name))
                    logging.info(f"Local success: {file_name}")
                    success += 1
                except Exception as e:
                    logging.error(f"Local failed for {file_name}: {e}")
        return success

    def run(self):
        """Main process execution."""
        if not self.settings: return

        files = self.settings.get("files", [])
        use_drive = self.settings.get("backup_to_drive", False)
        if not files: return

        self._notify("Backup Started", f"Processing {len(files)} files...")

        count = 0
        if use_drive:
            count = self._upload_to_drive(files, self.settings.get("gdrive_folder_id"))
        else:
            count = self._copy_locally(files, self.settings.get("destination"))

        self._notify("Backup Finished", f"Processed {count} of {len(files)} files successfully.")
        logging.info(f"Cycle complete. Success: {count}")


if __name__ == "__main__":
    manager = BackupManager()
    manager.run()