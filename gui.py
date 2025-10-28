import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
import pandas as pd
from graph_generator import generate_graph

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("400x400")
        self.resizable(False, False)
        self.parent = parent

        # Load settings
        self.settings = self.load_settings()

        # Build UI
        self.create_path_settings()
        self.create_color_settings()
        self.create_level_settings()
        self.create_save_button()

    def create_path_settings(self):
        path_frame = tk.Frame(self)
        path_frame.pack(pady=10)

        tk.Label(path_frame, text="Save Path:").grid(row=0, column=0, padx=5, pady=5)
        self.path_var = tk.StringVar(value=self.settings.get("save_path", "default"))
        self.path_combobox = ttk.Combobox(
            path_frame, 
            textvariable=self.path_var, 
            values=["default", "desktop"]
        )
        self.path_combobox.grid(row=0, column=1, padx=5, pady=5)

    def create_color_settings(self):
        color_frame = tk.Frame(self)
        color_frame.pack(pady=10)

        tk.Label(color_frame, text="Curve Color:").grid(row=0, column=0, padx=5, pady=5)
        self.curve_color_var = tk.StringVar(value=self.settings.get("curve_color", "#FF0000"))
        self.curve_color_button = tk.Button(
            color_frame, text="Choose Color", 
            command=lambda: self.choose_color(self.curve_color_var)
        )
        self.curve_color_button.grid(row=0, column=1, padx=5, pady=5)

    def create_level_settings(self):
        level_frame = tk.Frame(self)
        level_frame.pack(pady=10)

        self.level_entries = {}
        colors = {"Level 1": "green", "Level 2": "orange", "Level 3": "red"}
        for i, (level, color) in enumerate(colors.items()):
            tk.Label(level_frame, text=f"{level} Min:").grid(row=i, column=0, padx=5, pady=5)
            self.level_entries[level] = tk.Entry(level_frame)
            self.level_entries[level].grid(row=i, column=1, padx=5, pady=5)
            self.level_entries[level].insert(0, self.settings.get(level, "0" if i == 0 else "8"))

    def choose_color(self, color_var):
        color = colorchooser.askcolor()[1]
        if color:
            color_var.set(color)

    def create_save_button(self):
        save_button = tk.Button(self, text="Save", command=self.save_settings)
        save_button.pack(pady=20)

    def save_settings(self):
        self.settings["save_path"] = self.path_var.get()
        self.settings["curve_color"] = self.curve_color_var.get()

        for level, entry in self.level_entries.items():
            self.settings[level] = entry.get()

        with open("_internal/settings.txt", "w") as f:
            for key, value in self.settings.items():
                f.write(f"{key}={value}\n")

        messagebox.showinfo("Settings Saved", "Settings have been saved successfully.")
        self.destroy()

    def load_settings(self):
        settings = {"Level 1": "0", "Level 2": "8", "Level 3": "15"}
        if os.path.exists("_internal/settings.txt"):
            with open("_internal/settings.txt", "r") as f:
                for line in f.readlines():
                    key, value = line.strip().split("=")
                    settings[key] = value
        return settings

class KPIGenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KPI Generator V1.1")
        self.root.geometry("400x400")
        self.root.resizable(False, False)

        # Initial setup
        self.files = []

        # Create _internal directory and log files if they don't exist
        self.create_internal_directory()

        # Build UI
        self.create_menu_bar()
        self.create_main_frame()
        self.create_title_label()
        self.create_dropzone()
        self.create_apply_button()

    def open_settings(self):
        """Open the settings window."""
        SettingsWindow(self.root)  # Passer self.root au lieu de self

    def create_internal_directory(self):
        """Create _internal directory and log files if they don't exist."""
        if not os.path.exists("_internal"):
            os.makedirs("_internal")
        if not os.path.exists("_internal/glog.txt"):
            with open("_internal/glog.txt", "w") as f:
                f.write("Update Log:\n")
        if not os.path.exists("_internal/llog.txt"):
            with open("_internal/llog.txt", "w") as f:
                f.write("Last Log:\n")

    def create_menu_bar(self):
        """Create the menu bar with File and Help sections."""
        menubar = tk.Menu(self.root)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.reset_app)
        file_menu.add_command(label="Settings", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Update Log", command=self.show_update_log)
        help_menu.add_command(label="Last Log", command=self.show_last_log)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def show_update_log(self):
        """Show the update log from glog.txt."""
        try:
            with open("_internal/glog.txt", "r") as f:
                update_log = f.read()
            messagebox.showinfo("Update Log", update_log)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_last_log(self):
        """Show the last log from llog.txt."""
        try:
            with open("_internal/llog.txt", "r") as f:
                last_log = f.read()
            messagebox.showinfo("Last Log", last_log)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_about(self):
        """Show the about information."""
        about_text = "KPI Generator V1.1\n\nA tool to generate KPI graphs from CSV files."
        messagebox.showinfo("About", about_text)

    def create_main_frame(self):
        self.main_frame = tk.Frame(self.root, bg="#1b1c1c")
        self.main_frame.pack(expand=True, fill="both")

    def create_title_label(self):
        self.title_label = tk.Label(
            self.main_frame, 
            text="KPI Generator", 
            fg="white", 
            bg="#1b1c1c", 
            font=("Arial", 16)
        )
        self.title_label.pack(pady=10)

    def create_dropzone(self):
        canvas = tk.Canvas(self.main_frame, width=300, height=100, bg="#2e2e2e", highlightthickness=0)
        canvas.pack(pady=20)
        canvas.create_rounded_rectangle(5, 5, 295, 95, radius=20, fill="#2e2e2e", outline="white")
        self.dropzone_label = tk.Label(
            canvas,
            text="Click to browse CSV files",
            fg="white",
            font=("Arial", 12),
            bg="#2e2e2e"
        )
        self.dropzone_label.place(relx=0.5, rely=0.5, anchor="center")
        self.dropzone_label.bind("<Button-1>", self.browse_files)

    def create_apply_button(self):
        canvas = tk.Canvas(self.main_frame, width=120, height=40, bg="#1b1c1c", highlightthickness=0)
        canvas.pack(pady=10)
        canvas.create_rounded_rectangle(5, 5, 115, 35, radius=15, fill="#007bff", outline="white")
        self.apply_button = tk.Button(
            canvas,
            text="Apply",
            state=tk.DISABLED,
            command=self.apply_changes,
            fg="white",
            font=("Arial", 12),
            bg="#007bff",
            relief="flat",
            borderwidth=0
        )
        self.apply_button.place(relx=0.5, rely=0.5, anchor="center")

    def browse_files(self, event=None):
        self.files = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
        if self.files:
            self.dropzone_label.config(text=f"{len(self.files)} files selected")
            self.apply_button.config(state=tk.NORMAL)

    def apply_changes(self):
        self.apply_button.config(state=tk.DISABLED, text="Processing...")
        self.root.update()

        try:
            for file in self.files:
                df = pd.read_csv(file)
                generate_graph(df, os.path.basename(file).replace('.csv', ''))
            messagebox.showinfo("Success", "All files processed successfully!")
            self.log_application("Files processed successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log_application(f"Error: {str(e)}")
        finally:
            self.apply_button.config(state=tk.NORMAL, text="Apply")
            self.reset_app()

    def log_application(self, log_message):
        """Log the application event to llog.txt."""
        from datetime import datetime
        with open("_internal/llog.txt", "a") as f:
            f.write(f"[{datetime.now()}]: {log_message}\n")

    def reset_app(self):
        self.dropzone_label.config(text="Click to browse CSV files")
        self.files = []
        self.apply_button.config(state=tk.DISABLED)

def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
    points = [x1+radius, y1,
              x2-radius, y1,
              x2, y1,
              x2, y1+radius,
              x2, y2-radius,
              x2, y2,
              x2-radius, y2,
              x1+radius, y2,
              x1, y2,
              x1, y2-radius,
              x1, y1+radius,
              x1, y1]
    return self.create_polygon(points, **kwargs, smooth=True)

tk.Canvas.create_rounded_rectangle = create_rounded_rectangle