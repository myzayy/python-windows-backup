import json
import os
import shutil
import logging
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Logging setup
logging.basicConfig(
    filename="backup_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


class BackupManager:
    def __init__(self, settings_file="settings.json"):
        # Correctly points to the root directory from the src folder
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.settings_file = os.path.join(self.root_dir, settings_file)
        self.settings = self._load_settings()

    def _load_settings(self):
        """Loads backup configuration from the JSON settings file."""
        if not os.path.exists(self.settings_file):
            logging.error(f"Settings file '{self.settings_file}' not found.")
            return None
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logging.error(f"Error: Failed to parse JSON in '{self.settings_file}'.")
            return None
        except Exception as e:
            logging.error(f"Error reading settings: {e}")
            return None

    def _upload_to_drive(self, files, gdrive_folder_id):
        """Handles the logic for uploading files to Google Drive."""
        if not gdrive_folder_id:
            logging.error("Google Drive folder ID missing in settings.")
            return

        try:
            gauth = GoogleAuth()

            # FIXED: Explicitly tell PyDrive where to find the secrets file in the root
            secrets_path = os.path.join(self.root_dir, "client_secrets.json")

            if not os.path.exists(secrets_path):
                logging.error(f"Critical error: Client secrets file not found at {secrets_path}")
                return

            # Loading the config file explicitly before authentication
            gauth.LoadClientConfigFile(secrets_path)

            gauth.LocalWebserverAuth()
            drive = GoogleDrive(gauth)

            success_count = 0
            for path in files:
                if os.path.isfile(path):
                    file_name = os.path.basename(path)
                    try:
                        file_drive = drive.CreateFile({
                            'title': file_name,
                            'parents': [{'id': gdrive_folder_id, "kind": "drive#fileLink"}]
                        })
                        file_drive.SetContentFile(path)
                        file_drive.Upload()
                        logging.info(f"Cloud upload success: {file_name}")
                        success_count += 1
                    except Exception as e_file:
                        logging.error(f"Cloud upload failed for '{file_name}': {e_file}")

            logging.info(f"Summary: {success_count} files uploaded to Drive.")
        except Exception as e:
            logging.error(f"General Cloud error: {e}")

    def _copy_locally(self, files, destination):
        """Handles local file copying logic."""
        if not destination:
            logging.error("Local destination path is empty.")
            return

        if not os.path.exists(destination):
            try:
                os.makedirs(destination)
                logging.info(f"Created new destination folder: {destination}")
            except Exception as e:
                logging.error(f"Folder creation failed '{destination}': {e}")
                return

        success_count = 0
        for path in files:
            if os.path.isfile(path):
                file_name = os.path.basename(path)
                try:
                    shutil.copy2(path, os.path.join(destination, file_name))
                    logging.info(f"Local copy success: {file_name}")
                    success_count += 1
                except Exception as e_file:
                    logging.error(f"Local copy failed for '{file_name}': {e_file}")

        logging.info(f"Summary: {success_count} files copied locally.")

    def run(self):
        """Main entry point to start the backup process."""
        if not self.settings:
            return

        files = self.settings.get("files", [])
        use_drive = self.settings.get("backup_to_drive", False)

        if not files:
            logging.warning("No files found in configuration for backup.")
            return

        if use_drive:
            self._upload_to_drive(files, self.settings.get("gdrive_folder_id"))
        else:
            self._copy_locally(files, self.settings.get("destination"))


if __name__ == "__main__":
    manager = BackupManager()
    manager.run()