# utils/db.py
import sqlite3
import pathlib
import hashlib
import os
from typing import Optional

DB_PATH = pathlib.Path(__file__).resolve().parents[1] / "trace_music.db"

def _connect():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = _connect()
    cur = conn.cursor()
    # users
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        storage_used INTEGER DEFAULT 0,
        max_storage INTEGER DEFAULT 500,
        is_admin INTEGER DEFAULT 0
    )""")
    # nodes
    cur.execute("""
    CREATE TABLE IF NOT EXISTS nodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        node_id TEXT UNIQUE,
        memory INTEGER,
        status TEXT
    )""")
    # files
    cur.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        filename TEXT,
        path TEXT,
        size INTEGER,
        md5 TEXT,
        sha256 TEXT,
        uploaded_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )""")
    conn.commit()
    # ensure admin exists
    cur.execute("SELECT id FROM users WHERE username = ?", ("admin",))
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO users (username,password,storage_used,max_storage,is_admin) VALUES (?,?,?,?,?)",
            ("admin","admin123",0,500,1)
        )
        conn.commit()
    conn.close()

# ---------- Users ----------
def auth_user(username: str, password: str) -> Optional[dict]:
    conn = _connect(); cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
    row = cur.fetchone(); conn.close()
    if not row: return None
    return dict(row)

def get_user(username: str) -> Optional[dict]:
    conn = _connect(); cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    row = cur.fetchone(); conn.close()
    return dict(row) if row else None

def add_user(username: str, password: str, max_storage: int=500) -> dict:
    conn = _connect(); cur = conn.cursor()
    cur.execute("INSERT INTO users (username,password,max_storage) VALUES (?,?,?)", (username,password,max_storage))
    conn.commit()
    uid = cur.lastrowid
    conn.close()
    return get_user_by_id(uid)

def get_user_by_id(uid:int):
    conn = _connect(); cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id=?", (uid,))
    row = cur.fetchone(); conn.close()
    return dict(row) if row else None

def list_users():
    conn = _connect(); cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    rows = [dict(r) for r in cur.fetchall()]; conn.close()
    return rows

def increment_user_storage(uid:int, mb:int):
    conn = _connect(); cur = conn.cursor()
    cur.execute("UPDATE users SET storage_used = storage_used + ? WHERE id = ?", (mb, uid))
    conn.commit(); conn.close()

# ---------- Nodes ----------
def add_node_to_db(node_id: str, memory: int=1024, status: str="Online"):
    conn = _connect(); cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO nodes (node_id,memory,status) VALUES (?,?,?)", (node_id,memory,status))
    conn.commit(); conn.close()

def list_nodes():
    conn = _connect(); cur = conn.cursor()
    cur.execute("SELECT * FROM nodes")
    rows = [dict(r) for r in cur.fetchall()]; conn.close()
    return rows

def delete_node(node_id: str):
    conn = _connect(); cur = conn.cursor()
    cur.execute("DELETE FROM nodes WHERE node_id=?", (node_id,))
    conn.commit(); conn.close()

# ---------- Files ----------
def add_file(user_id:int, filename:str, path:str, size:int, md5:str, sha256:str, uploaded_at:str):
    conn = _connect(); cur = conn.cursor()
    cur.execute(
        "INSERT INTO files (user_id,filename,path,size,md5,sha256,uploaded_at) VALUES (?,?,?,?,?,?,?)",
        (user_id, filename, path, size, md5, sha256, uploaded_at)
    )
    conn.commit(); conn.close()

def list_user_files(user_id:int):
    conn = _connect(); cur = conn.cursor()
    cur.execute("SELECT * FROM files WHERE user_id=?", (user_id,))
    rows = [dict(r) for r in cur.fetchall()]; conn.close()
    return rows

def get_file(fid:int):
    conn = _connect(); cur = conn.cursor()
    cur.execute("SELECT * FROM files WHERE id=?", (fid,))
    row = cur.fetchone(); conn.close()
    return dict(row) if row else None

def delete_file(fid:int):
    rec = get_file(fid)
    if rec:
        try:
            os.remove(rec['path'])
        except:
            pass
    conn = _connect(); cur = conn.cursor()
    cur.execute("DELETE FROM files WHERE id=?", (fid,))
    conn.commit(); conn.close()

def get_stats():
    conn = _connect(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as users FROM users"); users = cur.fetchone()["users"]
    cur.execute("SELECT COUNT(*) as nodes FROM nodes"); nodes = cur.fetchone()["nodes"]
    cur.execute("SELECT SUM(size) as total FROM files"); total = cur.fetchone()["total"] or 0
    conn.close()
    return {"users": users, "nodes": nodes, "total_storage": total}

# helper to ensure storage directory
def ensure_storage_dir():
    p = pathlib.Path(__file__).resolve().parents[1] / "storage"
    p.mkdir(parents=True, exist_ok=True)
    return p
