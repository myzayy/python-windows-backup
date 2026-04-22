import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "..", "settings.json")


class ConfigApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Backup System Configurator")
        self.root.geometry("550x450")

        self.files = []
        self.destination = ""
        self.backup_to_drive = tk.BooleanVar()
        self.gdrive_folder_id_var = tk.StringVar()

        self.load_settings()

        # UI Elements
        tk.Label(root, text="1. Select Files for Backup", font=("Arial", 10, "bold")).pack(pady=5)
        tk.Button(root, text="Browse Files", command=self.select_files, width=20).pack()

        tk.Label(root, text="2. Choose Destination Type", font=("Arial", 10, "bold")).pack(pady=10)
        tk.Radiobutton(root, text="Local Drive (USB/HDD)", variable=self.backup_to_drive,
                       value=False, command=self.toggle_input).pack()
        tk.Radiobutton(root, text="Cloud (Google Drive)", variable=self.backup_to_drive,
                       value=True, command=self.toggle_input).pack()

        self.gdrive_frame = tk.Frame(root)
        tk.Label(self.gdrive_frame, text="Folder ID:").pack(side=tk.LEFT, padx=5)
        self.entry = tk.Entry(self.gdrive_frame, textvariable=self.gdrive_folder_id_var, width=35)
        self.entry.pack(side=tk.LEFT)
        self.gdrive_frame.pack(pady=10)

        tk.Button(root, text="Select Local Folder", command=self.select_dest).pack()

        tk.Button(root, text="SAVE CONFIGURATION", command=self.save,
                  bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), height=2).pack(pady=20)

        self.status = tk.Label(root, text="Ready", fg="grey")
        self.status.pack()

        self.toggle_input()

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.gdrive_folder_id_var.set(data.get("gdrive_folder_id", ""))
                    self.backup_to_drive.set(data.get("backup_to_drive", False))
                    self.files = data.get("files", [])
                    self.destination = data.get("destination", "")
            except:
                pass

    def toggle_input(self):
        if self.backup_to_drive.get():
            self.gdrive_frame.pack(pady=10)
        else:
            self.gdrive_frame.pack_forget()

    def select_files(self):
        self.files = list(filedialog.askopenfilenames(title="Choose Files"))
        self.status.config(text=f"{len(self.files)} files selected.")

    def select_dest(self):
        self.destination = filedialog.askdirectory(title="Choose Local Folder")
        if self.destination:
            self.status.config(text=f"Dest: {self.destination}")

    def save(self):
        if not self.files:
            messagebox.showwarning("Missing Data", "Please select at least one file.")
            return

        settings = {
            "files": self.files,
            "backup_to_drive": self.backup_to_drive.get(),
            "destination": self.destination if not self.backup_to_drive.get() else "",
            "gdrive_folder_id": self.gdrive_folder_id_var.get().strip()
        }

        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4)
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigApp(root)
    root.mainloop()