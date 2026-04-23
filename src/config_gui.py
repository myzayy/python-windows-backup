import customtkinter as ctk
from tkinter import filedialog, messagebox
import json
import os
import winshell
import re
from win32com.client import Dispatch

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "..", "settings.json")


class ConfigApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Backup System Configurator")
        self.geometry("600x620")

        self.files = []
        self.destination = ""
        self.startup_path = os.path.join(winshell.startup(), "WindowsBackup.lnk")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Title
        self.label_title = ctk.CTkLabel(self.main_frame, text="Backup Configuration",
                                        font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 1. File Selection
        self.file_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.file_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_browse = ctk.CTkButton(self.file_frame, text="Browse Files", command=self.select_files)
        self.btn_browse.pack(side="top", fill="x", pady=5)

        self.btn_clear = ctk.CTkButton(self.file_frame, text="Clear Selected Files", fg_color="#e74c3c",
                                       hover_color="#c0392b", command=self.clear_files)
        self.btn_clear.pack(side="top", fill="x", pady=5)

        # 2. Destination Type
        self.dest_type_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.dest_type_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.backup_to_drive = ctk.BooleanVar(value=False)
        self.radio_local = ctk.CTkRadioButton(self.dest_type_frame, text="Local Drive", variable=self.backup_to_drive,
                                              value=False, command=self.toggle_input)
        self.radio_local.pack(side="left", padx=20)
        self.radio_cloud = ctk.CTkRadioButton(self.dest_type_frame, text="Google Drive", variable=self.backup_to_drive,
                                              value=True, command=self.toggle_input)
        self.radio_cloud.pack(side="left", padx=20)

        # 3. Inputs
        self.dynamic_frame = ctk.CTkFrame(self.main_frame)
        self.dynamic_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.dynamic_frame.grid_columnconfigure(0, weight=1)

        self.gdrive_id_var = ctk.StringVar()
        self.entry_gdrive = ctk.CTkEntry(self.dynamic_frame, placeholder_text="Enter Google Drive Folder ID or Link",
                                         textvariable=self.gdrive_id_var)
        self.btn_dest = ctk.CTkButton(self.dynamic_frame, text="Select Destination Folder", fg_color="gray",
                                      command=self.select_dest)

        # 4. Startup Switch
        self.run_at_startup = ctk.BooleanVar(value=False)
        self.switch_startup = ctk.CTkSwitch(self.main_frame, text="Run Backup on Windows Startup",
                                            variable=self.run_at_startup)
        self.switch_startup.grid(row=4, column=0, padx=20, pady=10)

        # Status
        self.status_label = ctk.CTkLabel(self.main_frame, text="Ready", text_color="gray")
        self.status_label.grid(row=5, column=0, padx=20, pady=5)

        # Save Button
        self.btn_save = ctk.CTkButton(self.main_frame, text="SAVE CONFIGURATION",
                                      font=ctk.CTkFont(size=16, weight="bold"),
                                      fg_color="#2ecc71", hover_color="#27ae60", height=50, command=self.save)
        self.btn_save.grid(row=6, column=0, padx=20, pady=(10, 20), sticky="ew")

        self.load_settings()
        self.toggle_input()

    def clear_files(self):
        self.files = []
        self.status_label.configure(text="Files cleared", text_color="#e74c3c")

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.gdrive_id_var.set(data.get("gdrive_folder_id", ""))
                    self.backup_to_drive.set(data.get("backup_to_drive", False))
                    self.files = data.get("files", [])
                    self.destination = data.get("destination", "")
                    self.run_at_startup.set(data.get("run_at_startup", False))
                    if self.files:
                        self.status_label.configure(text=f"Loaded {len(self.files)} files from last session")
            except Exception:
                pass

    def toggle_input(self):
        if self.backup_to_drive.get():
            self.btn_dest.grid_forget()
            self.entry_gdrive.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        else:
            self.entry_gdrive.grid_forget()
            self.btn_dest.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

    def select_files(self):
        selected = filedialog.askopenfilenames(title="Choose Files")
        if selected:
            self.files = list(selected)
            self.status_label.configure(text=f"{len(self.files)} new files selected", text_color="#3498db")

    def select_dest(self):
        folder = filedialog.askdirectory(title="Choose Destination Folder")
        if folder:
            self.destination = folder
            self.status_label.configure(text=f"Folder selected", text_color="#3498db")

    def _manage_startup(self):
        """Creates or removes a Windows startup shortcut."""
        runner_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "runner.py"))

        if self.run_at_startup.get():
            # Create shortcut
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(self.startup_path)
            shortcut.Targetpath = "pythonw.exe"
            shortcut.Arguments = f'"{runner_path}"'
            shortcut.WorkingDirectory = os.path.dirname(runner_path)
            shortcut.IconLocation = "pythonw.exe"
            shortcut.save()
        else:
            # Remove shortcut if exists
            if os.path.exists(self.startup_path):
                os.remove(self.startup_path)

    def save(self):
        # Check file existence
        if not self.files:
            messagebox.showwarning("Missing Data", "No files selected for backup.")
            return

        is_cloud = self.backup_to_drive.get()
        g_id = self.gdrive_id_var.get().strip()

        if is_cloud:
            # If its link
            if "drive.google.com" in g_id:
                try:
                    g_id = g_id.split('/')[-1].split('?')[0]
                except Exception:
                    messagebox.showerror("Error", "Invalid Google Drive link format.")
                    return

            # ID folder validation
            id_pattern = r"^[a-zA-Z0-9-_]+$"
            if not re.match(id_pattern, g_id) or len(g_id) < 20:
                messagebox.showwarning("Validation Error",
                                       "Invalid Google Drive ID.\n\n"
                                       "A valid ID should:\n"
                                       "- Only contain English letters and numbers\n"
                                       "- Be at least 20 characters long\n"
                                       "- Not contain Cyrillic characters")
                return
        else:
            # validation of local path
            if not self.destination or not os.path.exists(self.destination):
                messagebox.showwarning("Validation Error", "Please select a valid local folder.")
                return

        # if all validations passed
        try:
            self._manage_startup()

            settings = {
                "files": self.files,
                "backup_to_drive": is_cloud,
                "destination": self.destination if not is_cloud else "",
                "gdrive_folder_id": g_id if is_cloud else "",
                "run_at_startup": self.run_at_startup.get()
            }

            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4)

            messagebox.showinfo("Success", "Configuration saved!")
            self.status_label.configure(text="Settings saved successfully", text_color="#2ecc71")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")


if __name__ == "__main__":
    app = ConfigApp()
    app.mainloop()