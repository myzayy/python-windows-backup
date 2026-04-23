import customtkinter as ctk
from tkinter import filedialog, messagebox
import json
import os

# Set appearance and theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# Points to the root directory from the src folder
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "..", "settings.json")


class ConfigApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Backup System Configurator")
        self.geometry("600x520")

        self.files = []
        self.destination = ""

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

        self.label_files = ctk.CTkLabel(self.file_frame, text="1. Select files to include in backup:",
                                        font=ctk.CTkFont(size=14))
        self.label_files.pack(side="top", anchor="w", pady=5)

        self.btn_browse = ctk.CTkButton(self.file_frame, text="Browse Files", command=self.select_files)
        self.btn_browse.pack(side="top", fill="x", pady=5)

        # 2. Destination Type Section
        self.dest_type_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.dest_type_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.label_dest_type = ctk.CTkLabel(self.dest_type_frame, text="2. Choose backup destination:",
                                            font=ctk.CTkFont(size=14))
        self.label_dest_type.pack(side="top", anchor="w", pady=5)

        self.backup_to_drive = ctk.BooleanVar(value=False)
        self.radio_local = ctk.CTkRadioButton(self.dest_type_frame, text="Local Drive (USB/HDD)",
                                              variable=self.backup_to_drive, value=False, command=self.toggle_input)
        self.radio_local.pack(side="left", padx=20, pady=5)

        self.radio_cloud = ctk.CTkRadioButton(self.dest_type_frame, text="Google Drive",
                                              variable=self.backup_to_drive, value=True, command=self.toggle_input)
        self.radio_cloud.pack(side="left", padx=20, pady=5)

        # 3. Dynamic Inputs Section
        self.dynamic_frame = ctk.CTkFrame(self.main_frame)
        self.dynamic_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.dynamic_frame.grid_columnconfigure(0, weight=1)

        # Google Drive ID Input
        self.gdrive_id_var = ctk.StringVar()
        self.entry_gdrive = ctk.CTkEntry(self.dynamic_frame, placeholder_text="Enter Google Drive Folder ID",
                                         textvariable=self.gdrive_id_var)

        # Local Folder Button
        self.btn_dest = ctk.CTkButton(self.dynamic_frame, text="Select Destination Folder",
                                      fg_color="gray", hover_color="#555555", command=self.select_dest)

        # Status Label
        self.status_label = ctk.CTkLabel(self.main_frame, text="Ready", text_color="gray")
        self.status_label.grid(row=4, column=0, padx=20, pady=5)

        # Save Button
        self.btn_save = ctk.CTkButton(self.main_frame, text="SAVE CONFIGURATION",
                                      font=ctk.CTkFont(size=16, weight="bold"),
                                      fg_color="#2ecc71", hover_color="#27ae60", height=50, command=self.save)
        self.btn_save.grid(row=5, column=0, padx=20, pady=(10, 20), sticky="ew")

        self.load_settings()
        self.toggle_input()

    def load_settings(self):
        """Loads existing settings."""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.gdrive_id_var.set(data.get("gdrive_folder_id", ""))
                    self.backup_to_drive.set(data.get("backup_to_drive", False))
                    self.files = data.get("files", [])
                    self.destination = data.get("destination", "")
                    if self.files:
                        self.status_label.configure(text=f"{len(self.files)} files selected")
            except Exception:
                pass

    def toggle_input(self):
        """Changes UI based on backup type."""
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
            self.status_label.configure(text=f"{len(self.files)} files selected", text_color="#3498db")

    def select_dest(self):
        folder = filedialog.askdirectory(title="Choose Destination Folder")
        if folder:
            self.destination = folder
            self.status_label.configure(text=f"Dest: ...{folder[-30:]}", text_color="#3498db")

    def save(self):
        if not self.files:
            messagebox.showwarning("Missing Data", "Please select files first.")
            return

        is_cloud = self.backup_to_drive.get()
        g_id = self.gdrive_id_var.get().strip()

        if is_cloud and not g_id:
            messagebox.showwarning("Missing Data", "Please enter Google Drive Folder ID.")
            return
        if not is_cloud and not self.destination:
            messagebox.showwarning("Missing Data", "Please select local folder.")
            return

        settings = {
            "files": self.files,
            "backup_to_drive": is_cloud,
            "destination": self.destination if not is_cloud else "",
            "gdrive_folder_id": g_id if is_cloud else ""
        }

        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4)
            messagebox.showinfo("Success", "Configuration saved!")
            self.status_label.configure(text="Settings saved successfully", text_color="#2ecc71")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")


if __name__ == "__main__":
    app = ConfigApp()
    app.mainloop()