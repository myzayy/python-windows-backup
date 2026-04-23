# ProBackup: Desktop Automation & Sync Tool

**ProBackup** is a professional Python-based utility designed for automated data synchronization and security. It provides a seamless way to back up critical files to either **Google Drive** or **local storage** (USB/HDD) with a focus on reliability, automation, and modern User Experience (UX).

## Key Features
- **Hybrid Storage:** Support for both Cloud (Google Drive API) and Local (USB, HDD) backups.
- **Modern Desktop GUI:** A sleek interface built with `CustomTkinter`, featuring native Dark/Light mode support.
- **Smart Versioning:** Automatically creates unique timestamped folders (`Backup_YYYY-MM-DD_HH-MM-SS`) to preserve history and prevent data loss.
- **Windows Integration:** Includes a "Run on Startup" feature that uses `pythonw` for silent background execution.
- **Real-time Notifications:** Uses native Windows Toast notifications (`winotify`) to inform the user about backup status.
- **Intelligent Input Parsing:** Custom Regex-based logic to extract Folder IDs from full Google Drive URLs for ease of use.
- **Detailed Logging:** All operations and errors are recorded in `backup_log.txt` for easy troubleshooting.

## Technical Stack
- **Language:** Python 3.14
- **Libraries:** PyDrive (Google Drive API), CustomTkinter (UI), Winotify (Notifications), Winshell (System integration).
- **Security:** Implements `.gitignore` to protect sensitive API credentials and local logs.

## Installation and Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/myzayy/python-windows-backup](https://github.com/myzayy/python-windows-backup)
   cd python-windows-backup