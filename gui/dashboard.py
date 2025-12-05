# dashboard.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import hashlib, threading, time, os, sqlite3, pathlib, datetime, shutil
import yaml
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# import DB and main_app bridge
from utils import db
import main

# helper functions
def human_size(bytes_size: int) -> str:
    if bytes_size < 1024:
        return f"{bytes_size} B"
    if bytes_size < 1024**2:
        return f"{bytes_size/1024:.1f} KB"
    if bytes_size < 1024**3:
        return f"{bytes_size/1024**2:.1f} MB"
    return f"{bytes_size/1024**3:.1f} GB"

def compute_hashes(file_path):
    md5 = hashlib.md5(); sha = hashlib.sha256()
    with open(file_path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            md5.update(chunk); sha.update(chunk)
    return md5.hexdigest(), sha.hexdigest()

# Login window using DB.auth_user
class LoginWindow(tk.Toplevel):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.title("TRACE-MUSIC Login")
        self.geometry("420x300")
        self.configure(bg="#1e1e1e")
        self.on_success = on_success
        self.resizable(False, False)

        ttk.Label(self, text="TRACE-MUSIC", font=("Segoe UI", 20, "bold"), background="#1e1e1e", foreground="white").pack(pady=10)

        frm = tk.Frame(self, bg="#1e1e1e")
        frm.pack(pady=10)

        ttk.Label(frm, text="Username:", background="#1e1e1e", foreground="white").grid(row=0, column=0, sticky="w", pady=5)
        self.username = ttk.Entry(frm, width=30); self.username.grid(row=0, column=1, pady=5)
        ttk.Label(frm, text="Password:", background="#1e1e1e", foreground="white").grid(row=1, column=0, sticky="w", pady=5)
        self.password = ttk.Entry(frm, width=30, show="*"); self.password.grid(row=1, column=1, pady=5)

        ttk.Button(self, text="Login", command=self._attempt_login).pack(pady=12)

    def _attempt_login(self):
        user = db.auth_user(self.username.get().strip(), self.password.get().strip())
        if user:
            self.destroy(); self.on_success(user)
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")

# Main Dashboard (user view)
class MainDashboard(tk.Toplevel):
    def __init__(self, master, user):
        super().__init__(master)
        self.user = user
        self.title(f"TRACE-MUSIC - {user['username']}")
        self.geometry("1200x720")
        self.configure(bg="#121212")
        self.style = ttk.Style(self); self.style.theme_use('clam')

        self._build_header(); self._build_sidebar(); self._build_main_panel()
        self.refresh_user()

    def _build_header(self):
        header = tk.Frame(self, bg="#1f1f1f", height=70); header.pack(fill='x')
        tk.Label(header, text=f"TRACE-MUSIC — {self.user['username']}", font=("Segoe UI", 14, "bold"), bg="#1f1f1f", fg="#FFD4A3").pack(side='left', padx=20)
        if self.user.get('is_admin'):
            ttk.Button(header, text="Admin Panel", command=self.open_admin).pack(side='right', padx=20)

    def _build_sidebar(self):
        sidebar = tk.Frame(self, bg="#1b1b1b", width=220); sidebar.pack(fill='y', side='left')
        buttons = [("Overview", self.show_overview), ("My Files", self.show_files), ("Upload", self.show_upload), ("Integrity", self.show_integrity)]
        for t, cmd in buttons:
            ttk.Button(sidebar, text=t, command=cmd).pack(fill='x', padx=12, pady=8)

    def _build_main_panel(self):
        self.main_panel = tk.Frame(self, bg="#121212"); self.main_panel.pack(expand=True, fill='both')
        self.current_frame = None; self.show_overview()

    def _clear(self):
        if self.current_frame: self.current_frame.destroy()
        self.current_frame = tk.Frame(self.main_panel, bg="#121212"); self.current_frame.pack(expand=True, fill='both', padx=10, pady=10)

    def refresh_user(self):
        self.user = db.get_user(self.user['username'])

    def show_overview(self):
        self._clear(); tk.Label(self.current_frame, text="Overview", font=("Segoe UI", 16, "bold"), fg="#FFD4A3", bg="#121212").pack(anchor='nw')
        stats = db.get_stats()
        frame = tk.Frame(self.current_frame, bg="#1e1e1e"); frame.pack(pady=12, fill='x')
        left = tk.Frame(frame, bg="#1e1e1e"); left.pack(side='left', padx=8, pady=8, fill='both', expand=True)
        right = tk.Frame(frame, bg="#1e1e1e"); right.pack(side='left', padx=8, pady=8, fill='both')
        tk.Label(left, text=f"Nodes: {stats['nodes']}", bg="#1e1e1e", fg='white').pack(anchor='w', pady=4)
        tk.Label(left, text=f"Users: {stats['users']}", bg="#1e1e1e", fg='white').pack(anchor='w', pady=4)
        tk.Label(left, text=f"Total Stored: {human_size(stats['total_storage'])}", bg="#1e1e1e", fg='white').pack(anchor='w', pady=4)
        self.refresh_user()
        used = self.user['storage_used']; cap = self.user['max_storage']
        tk.Label(right, text=f"Your Storage", bg="#1e1e1e", fg='white').pack(anchor='w')
        pb = ttk.Progressbar(right, maximum=cap, value=used, length=300); pb.pack(pady=6)
        tk.Label(right, text=f"{used}MB / {cap}MB", bg="#1e1e1e", fg='#FFD4A3').pack()

    def show_files(self):
        self._clear(); tk.Label(self.current_frame, text="My Files", font=("Segoe UI", 16, "bold"), fg="#FFD4A3", bg="#121212").pack(anchor='nw')
        cols = ("id", "filename", "size", "md5", "sha256", "uploaded_at")
        tree = ttk.Treeview(self.current_frame, columns=cols, show='headings'); 
        for c in cols: tree.heading(c, text=c.capitalize())
        tree.pack(expand=True, fill='both')
        files = db.list_user_files(self.user['id'])
        for f in files:
            tree.insert('', 'end', values=(f['id'], f['filename'], human_size(f['size']), f['md5'][:10]+"...", f['sha256'][:10]+"...", f['uploaded_at']))
        frm = tk.Frame(self.current_frame, bg='#121212'); frm.pack(fill='x', pady=8)
        ttk.Button(frm, text='Download', command=lambda: self._download_selected(tree)).pack(side='left', padx=6)
        ttk.Button(frm, text='Delete', command=lambda: self._delete_selected(tree)).pack(side='left', padx=6)

    def _download_selected(self, tree):
        sel = tree.selection(); 
        if not sel: return messagebox.showwarning('Select', 'Select a file')
        item = tree.item(sel[0]); fid = item['values'][0]; rec = db.get_file(fid)
        src = rec['path']; dest = filedialog.asksaveasfilename(initialfile=rec['filename'])
        if dest:
            shutil.copy2(src, dest); messagebox.showinfo('Downloaded', f'Saved to {dest}')

    def _delete_selected(self, tree):
        sel = tree.selection(); 
        if not sel: return messagebox.showwarning('Select', 'Select a file')
        item = tree.item(sel[0]); fid = item['values'][0]; rec = db.get_file(fid)
        if messagebox.askyesno('Delete', f"Delete {rec['filename']}?"):
            db.delete_file(fid); self.show_files()

    def show_upload(self):
        self._clear(); tk.Label(self.current_frame, text="Upload File", font=("Segoe UI", 16, "bold"), fg="#FFD4A3", bg="#121212").pack(anchor='nw')
        ttk.Button(self.current_frame, text='Select & Upload', command=self._upload_file).pack(pady=20)

    def _upload_file(self):
        path = filedialog.askopenfilename(); 
        if not path: return
        size = os.path.getsize(path); size_mb = size // (1024*1024)
        if self.user['storage_used'] + size_mb > self.user['max_storage']:
            return messagebox.showerror('Storage full', 'Not enough storage for this upload')
        user_dir = pathlib.Path('storage') / str(self.user['id']); user_dir.mkdir(parents=True, exist_ok=True)
        dest = user_dir / os.path.basename(path); shutil.copy2(path, dest)
        md5, sha256 = compute_hashes(dest); now = datetime.datetime.utcnow().isoformat()
        db.add_file(self.user['id'], os.path.basename(path), str(dest), size, md5, sha256, now)
        db.increment_user_storage(self.user['id'], size_mb)
        messagebox.showinfo('Uploaded', 'File uploaded successfully'); self.refresh_user(); self.show_overview()

    def show_integrity(self):
        self._clear(); tk.Label(self.current_frame, text="Integrity Check", font=("Segoe UI", 16, "bold"), fg="#FFD4A3", bg="#121212").pack(anchor='nw')
        ttk.Button(self.current_frame, text='Select File to Verify', command=self._integrity_check).pack(pady=20)

    def _integrity_check(self):
        path = filedialog.askopenfilename(); 
        if not path: return
        md5, sha = compute_hashes(path); messagebox.showinfo('Hashes', f'MD5: {md5}\nSHA256: {sha}')

    def open_admin(self):
        AdminDashboard(self)

# Admin window (uses DB and main_app APIs)
class AdminDashboard(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master); self.title('Admin Dashboard'); self.geometry('1100x700'); self.configure(bg='#121212'); self._build()

    def _build(self):
        tk.Label(self, text='Admin - System Management', font=("Segoe UI", 16, 'bold'), fg='#FFD4A3', bg='#121212').pack(pady=10)
        tabs = ttk.Notebook(self); tabs.pack(expand=True, fill='both', padx=12, pady=12)
        self.tab_stats = ttk.Frame(tabs); self.tab_nodes = ttk.Frame(tabs); self.tab_users = ttk.Frame(tabs)
        tabs.add(self.tab_stats, text='Stats'); tabs.add(self.tab_nodes, text='Nodes'); tabs.add(self.tab_users, text='Users')
        self.build_stats(); self.build_nodes(); self.build_users()

    def build_stats(self):
        stats = db.get_stats()
        tk.Label(self.tab_stats, text=f"Nodes: {stats['nodes']}", bg='#121212', fg='white').pack(pady=6)
        tk.Label(self.tab_stats, text=f"Users: {stats['users']}", bg='#121212', fg='white').pack(pady=6)
        tk.Label(self.tab_stats, text=f"Total Storage: {human_size(stats['total_storage'])}", bg='#121212', fg='white').pack(pady=6)

    def build_nodes(self):
        frm = tk.Frame(self.tab_nodes, bg='#121212'); frm.pack(fill='both', expand=True, padx=12, pady=12)
        tree = ttk.Treeview(frm, columns=('id','memory','status'), show='headings'); 
        for c in ('id','memory','status'): tree.heading(c, text=c); tree.pack(expand=True, fill='both')
        for n in db.list_nodes(): tree.insert('', 'end', values=(n['node_id'], n['memory'], n['status']))
        btns = tk.Frame(self.tab_nodes, bg='#121212'); btns.pack(pady=8)
        ttk.Button(btns, text='Add Node', command=self._add_node).pack(side='left', padx=6)
        ttk.Button(btns, text='Remove Node', command=lambda:self._remove_node(tree)).pack(side='left', padx=6)

    def _add_node(self):
        nid = f"node{int(time.time())%100000}"
        # add to runtime network & DB
        main_app.add_node(nid, memory=1024)
        messagebox.showinfo('Added', f'Node {nid} added'); self.destroy(); AdminDashboard(self.master)

    def _remove_node(self, tree):
        sel = tree.selection(); 
        if not sel: return messagebox.showwarning('Select','Select a node')
        nid = tree.item(sel[0])['values'][0]; db.delete_node(nid); messagebox.showinfo('Removed', f'{nid} removed'); self.destroy(); AdminDashboard(self.master)

    def build_users(self):
        frm = tk.Frame(self.tab_users, bg='#121212'); frm.pack(fill='both', expand=True, padx=12, pady=12)
        tree = ttk.Treeview(frm, columns=('id','username','storage','quota'), show='headings'); 
        for c in ('id','username','storage','quota'): tree.heading(c, text=c); tree.pack(expand=True, fill='both')
        for u in db.list_users(): tree.insert('', 'end', values=(u['id'], u['username'], f"{u['storage_used']}MB", f"{u['max_storage']}MB"))
        btns = tk.Frame(self.tab_users, bg='#121212'); btns.pack(pady=8)
        ttk.Button(btns, text='Create User', command=self._create_user).pack(side='left', padx=6)
        ttk.Button(btns, text='Delete User', command=lambda:self._delete_user(tree)).pack(side='left', padx=6)

    def _create_user(self):
        uname = f'user{int(time.time())%10000}'
        db.add_user(uname, 'secret', max_storage=500)
        messagebox.showinfo('Created', f'User {uname} created'); self.destroy(); AdminDashboard(self.master)

    def _delete_user(self, tree):
        sel = tree.selection(); 
        if not sel: return messagebox.showwarning('Select','Select a user')
        uid = tree.item(sel[0])['values'][0]; db.delete_file(uid); db_conn = None
        db_conn = None
        db_conn = None
        db_conn = None
        db_conn = None
        # Actually delete user:
        conn = sqlite3.connect(str(pathlib.Path(__file__).resolve().parents[1] / "trace_music.db"))
        cur = conn.cursor(); cur.execute("DELETE FROM users WHERE id=?", (uid,)); conn.commit(); conn.close()
        messagebox.showinfo('Deleted', 'User removed'); self.destroy(); AdminDashboard(self.master)

# App launcher
if __name__ == '__main__':
    db.init_db()
    root = tk.Tk(); root.withdraw()
    def start_main(user): root.destroy(); app = MainDashboard(None, user); app.mainloop()
    LoginWindow(root, start_main)
    root.mainloop()
