import customtkinter as ctk
from tkinter import filedialog, messagebox
import json
import os
import re
import winshell
from win32com.client import Dispatch

# Set appearance and theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# Points to the root directory from the src folder
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "..", "settings.json")


class ConfigApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Backup System Configurator")
        self.geometry("600x620")

        self.files = []
        self.destination = ""
        self.startup_path = os.path.join(winshell.startup(), "WindowsBackup.lnk")

        # Layout configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Title
        self.label_title = ctk.CTkLabel(self.main_frame, text="Backup Configuration",
                                        font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 1. File Selection Section
        self.file_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.file_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_browse = ctk.CTkButton(self.file_frame, text="Browse Files", command=self.select_files)
        self.btn_browse.pack(side="top", fill="x", pady=5)

        self.btn_clear = ctk.CTkButton(self.file_frame, text="Clear Selected Files", fg_color="#e74c3c",
                                       hover_color="#c0392b", command=self.clear_files)
        self.btn_clear.pack(side="top", fill="x", pady=5)

        # 2. Destination Type Section
        self.dest_type_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.dest_type_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.backup_to_drive = ctk.BooleanVar(value=False)
        self.radio_local = ctk.CTkRadioButton(self.dest_type_frame, text="Local Drive", variable=self.backup_to_drive,
                                              value=False, command=self.toggle_input)
        self.radio_local.pack(side="left", padx=20)
        self.radio_cloud = ctk.CTkRadioButton(self.dest_type_frame, text="Google Drive", variable=self.backup_to_drive,
                                              value=True, command=self.toggle_input)
        self.radio_cloud.pack(side="left", padx=20)

        # 3. Dynamic Inputs Section
        self.dynamic_frame = ctk.CTkFrame(self.main_frame)
        self.dynamic_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.dynamic_frame.grid_columnconfigure(0, weight=1)

        self.gdrive_id_var = ctk.StringVar()
        # Updated placeholder text
        self.entry_gdrive = ctk.CTkEntry(self.dynamic_frame,
                                         placeholder_text="Paste the link to your Google Drive folder",
                                         placeholder_text_color="gray",
                                         height=35)
        self.btn_dest = ctk.CTkButton(self.dynamic_frame, text="Select Destination Folder", fg_color="gray",
                                      command=self.select_dest)

        # 4. Startup Switch
        self.run_at_startup = ctk.BooleanVar(value=False)
        self.switch_startup = ctk.CTkSwitch(self.main_frame, text="Run Backup on Windows Startup",
                                            variable=self.run_at_startup)
        self.switch_startup.grid(row=4, column=0, padx=20, pady=10)

        # Status Label
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
        """Clears the list of selected files."""
        self.files = []
        self.status_label.configure(text="Files cleared", text_color="#e74c3c")

    def load_settings(self):
        """Loads existing settings from the JSON file."""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    g_id = data.get("gdrive_folder_id", "")
                    if g_id:
                        self.entry_gdrive.delete(0, 'end')  # Очищуємо поле
                        self.entry_gdrive.insert(0, g_id)
                    self.backup_to_drive.set(data.get("backup_to_drive", False))
                    self.files = data.get("files", [])
                    self.destination = data.get("destination", "")
                    self.run_at_startup.set(data.get("run_at_startup", False))
                    if self.files:
                        self.status_label.configure(text=f"Loaded {len(self.files)} files from last session")
            except Exception:
                pass

    def toggle_input(self):
        """Changes UI based on backup type (Local or Cloud)."""
        if self.backup_to_drive.get():
            self.btn_dest.grid_forget()
            self.entry_gdrive.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        else:
            self.entry_gdrive.grid_forget()
            self.btn_dest.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

    def select_files(self):
        """Opens a dialog to select files."""
        selected = filedialog.askopenfilenames(title="Choose Files")
        if selected:
            self.files = list(selected)
            self.status_label.configure(text=f"{len(self.files)} new files selected", text_color="#3498db")

    def select_dest(self):
        """Opens a dialog to select local destination folder."""
        folder = filedialog.askdirectory(title="Choose Destination Folder")
        if folder:
            self.destination = folder
            self.status_label.configure(text=f"Folder selected", text_color="#3498db")

    def _manage_startup(self):
        """Creates or removes a Windows startup shortcut."""
        runner_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "runner.py"))

        if self.run_at_startup.get():
            # Create shortcut in Startup folder
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(self.startup_path)
            shortcut.Targetpath = "pythonw.exe"  # Run without console window
            shortcut.Arguments = f'"{runner_path}"'
            shortcut.WorkingDirectory = os.path.dirname(runner_path)
            shortcut.IconLocation = "pythonw.exe"
            shortcut.save()
        else:
            # Remove shortcut if it exists
            if os.path.exists(self.startup_path):
                os.remove(self.startup_path)

    def save(self):
        """Validates input and saves settings to JSON file."""
        # Check if files are selected
        if not self.files:
            messagebox.showwarning("Missing Data", "No files selected for backup.")
            return

        is_cloud = self.backup_to_drive.get()
        g_id = self.entry_gdrive.get().strip()

        if is_cloud:
            # Extract ID if a link was provided
            if "drive.google.com" in g_id:
                try:
                    g_id = g_id.split('/')[-1].split('?')[0]
                except Exception:
                    messagebox.showerror("Error", "Invalid Google Drive link format.")
                    return

            # Strict validation using regular expressions (only Latin letters, numbers, - and _)
            id_pattern = r"^[a-zA-Z0-9-_]+$"
            if not re.match(id_pattern, g_id) or len(g_id) < 20:
                messagebox.showwarning("Validation Error",
                                       "Please enter a valid Google Drive ID or Link (English letters only).")
                return
        else:
            # Validation of local path existence
            if not self.destination or not os.path.exists(self.destination):
                messagebox.showwarning("Validation Error", "Please select a valid local folder.")
                return

        # Attempt to save data and manage startup
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
            # Error handling for file system or permission issues
            messagebox.showerror("Error", f"Failed to save configuration: {e}")


if __name__ == "__main__":
    app = ConfigApp()
    app.mainloop()