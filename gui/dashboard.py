import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import hashlib
import yaml
import threading
import time
import os

# ----------------- Authentication Window -----------------
class LoginWindow(tk.Toplevel):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.title("Admin Login - TRACE-MUSIC")
        self.geometry("400x300")
        self.configure(bg="#1e1e1e")
        self.on_success = on_success

        ttk.Label(self, text="Admin Login", font=("Segoe UI", 18, "bold"), foreground="white", background="#1e1e1e").pack(pady=20)

        form = tk.Frame(self, bg="#1e1e1e")
        form.pack(pady=20)

        ttk.Label(form, text="Username:", foreground="white", background="#1e1e1e").grid(row=0, column=0, pady=5, sticky="w")
        self.username_entry = ttk.Entry(form, width=30)
        self.username_entry.grid(row=0, column=1, pady=5)

        ttk.Label(form, text="Password:", foreground="white", background="#1e1e1e").grid(row=1, column=0, pady=5, sticky="w")
        self.password_entry = ttk.Entry(form, width=30, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)

        ttk.Button(self, text="Login", command=self._attempt_login).pack(pady=10)
        self.bind("<Return>", lambda e: self._attempt_login())

    def _attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        config = load_config()
        admin_user = config.get("admin_user", "admin")
        admin_pass = config.get("admin_pass", "admin123")

        if username == admin_user and password == admin_pass:
            messagebox.showinfo("Success", "Login successful!")
            self.destroy()
            self.on_success()
        else:
            messagebox.showerror("Error", "Invalid username or password!")

# ----------------- Utility Functions -----------------

def compute_hash(file_path, mode="sha256"):
    h = hashlib.sha256() if mode == "sha256" else hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


def load_config():
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except:
        return {}


def save_config(data):
    with open("config.yaml", "w") as f:
        yaml.dump(data, f)


# ----------------- Dashboard Class -----------------
class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TRACE-MUSIC Dashboard")
        self.geometry("1200x700")
        self.configure(bg="#1e1e1e")

        self.style = ttk.Style(self)
        self._apply_styles()

        self.active_panel = None
        self.config_data = load_config()

        self.node_status = {
            "node1": "Online",
            "node2": "Online",
            "node3": "Offline"
        }

        self._build_header()
        self._build_sidebar()
        self._build_main_panel()

        # Start node monitor thread
        threading.Thread(target=self._monitor_nodes, daemon=True).start()

    # ----------------- Styling -----------------

    def _apply_styles(self):
        self.style.theme_use("clam")
        primary = "#FF6A00"
        secondary = "#2b2b2b"
        text_light = "#FFFFFF"

        self.style.configure("TButton", background=primary, foreground=text_light,
                             padding=10, font=("Segoe UI", 10, "bold"))
        self.style.map("TButton", background=[("active", "#FF8C3C")])

        self.style.configure("TLabel", background="#1e1e1e", foreground=text_light)

    # ----------------- Layout -----------------

    def _build_header(self):
        header = tk.Frame(self, bg="#FF6A00", height=60)
        header.pack(fill="x")
        tk.Label(header, text="TRACE-MUSIC Dashboard", font=("Segoe UI", 20, "bold"),
                 bg="#FF6A00", fg="white").pack(pady=10)

    def _build_sidebar(self):
        sidebar = tk.Frame(self, bg="#2b2b2b", width=220)
        sidebar.pack(fill="y", side="left")

        buttons = [
            ("Overview", self.show_overview),
            ("Nodes", self.show_nodes),
            ("Uploads", self.show_uploads),
            ("Downloads", self.show_downloads),
            ("Integrity Check", self.show_integrity),
            ("Settings", self.show_settings)
        ]

        for text, cmd in buttons:
            ttk.Button(sidebar, text=text, command=cmd).pack(pady=8, padx=20, fill="x")

    def _build_main_panel(self):
        self.main_panel = tk.Frame(self, bg="#1e1e1e")
        self.main_panel.pack(expand=True, fill="both", padx=10, pady=10)
        self.show_overview()

    def _clear_panel(self):
        if self.active_panel:
            self.active_panel.destroy()
        self.active_panel = tk.Frame(self.main_panel, bg="#1e1e1e")
        self.active_panel.pack(expand=True, fill="both")

    # ----------------- Node Monitoring Thread -----------------

    def _monitor_nodes(self):
        while True:
            # Simulated monitoring
            self.node_status["node3"] = "Online" if time.time() % 10 < 5 else "Offline"
            time.sleep(2)

    # ----------------- Panels -----------------

    def show_overview(self):
        self._clear_panel()
        ttk.Label(self.active_panel, text="📊 System Overview", font=("Segoe UI", 16, "bold")).pack(pady=20)

    def show_nodes(self):
        self._clear_panel()
        ttk.Label(self.active_panel, text="🖥️ Real-Time Node Monitoring", font=("Segoe UI", 16, "bold")).pack(pady=20)

        tree = ttk.Treeview(self.active_panel, columns=("ID", "Status"), show="headings")
        tree.heading("ID", text="Node ID")
        tree.heading("Status", text="Status")
        tree.pack(fill="both", expand=True)

        def update_tree():
            tree.delete(*tree.get_children())
            for nid, status in self.node_status.items():
                tree.insert("", "end", values=(nid, status))
            self.after(1000, update_tree)

        update_tree()

    def show_uploads(self):
        self._clear_panel()
        ttk.Label(self.active_panel, text="📤 Upload File", font=("Segoe UI", 16, "bold")).pack(pady=20)

        def choose_file():
            path = filedialog.askopenfilename()
            if path:
                try:
                    # Simulate file upload
                    dest = os.path.join("uploaded/", os.path.basename(path))
                    os.makedirs("uploaded", exist_ok=True)
                    with open(path, "rb") as src, open(dest, "wb") as dst:
                        dst.write(src.read())
                    messagebox.showinfo("Success", f"File uploaded: {dest}")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

        ttk.Button(self.active_panel, text="Select File", command=choose_file).pack(pady=10)

    def show_downloads(self):
        self._clear_panel()
        ttk.Label(self.active_panel, text="📥 Download File", font=("Segoe UI", 16, "bold")).pack(pady=20)

        def download_file():
            filename = filedialog.askopenfilename(initialdir="uploaded")
            if not filename:
                return
            dest = filedialog.asksaveasfilename(defaultextension=".bin")
            if dest:
                with open(filename, "rb") as src, open(dest, "wb") as dst:
                    dst.write(src.read())
                messagebox.showinfo("Success", "File downloaded successfully!")

        ttk.Button(self.active_panel, text="Choose File", command=download_file).pack(pady=10)

    def show_integrity(self):
        self._clear_panel()
        ttk.Label(self.active_panel, text="🔐 File Integrity Hashing", font=("Segoe UI", 16, "bold")).pack(pady=20)

        def select_file():
            path = filedialog.askopenfilename()
            if not path:
                return
            sha = compute_hash(path, "sha256")
            md5 = compute_hash(path, "md5")

            ttk.Label(self.active_panel, text=f"SHA-256: {sha}").pack(pady=5)
            ttk.Label(self.active_panel, text=f"MD5: {md5}").pack(pady=5)

        ttk.Button(self.active_panel, text="Select File", command=select_file).pack(pady=10)

    def show_settings(self):
        self._clear_panel()
        ttk.Label(self.active_panel, text="⚙️ Edit Settings", font=("Segoe UI", 16, "bold")).pack(pady=20)

        entry = ttk.Entry(self.active_panel, width=50)
        entry.insert(0, str(self.config_data))
        entry.pack(pady=10)

        def save():
            try:
                new_data = eval(entry.get())
                save_config(new_data)
                messagebox.showinfo("Saved", "Configuration updated!")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(self.active_panel, text="Save Config", command=save).pack(pady=10)


if __name__ == "__main__":
    app = Dashboard()
    app.mainloop()
