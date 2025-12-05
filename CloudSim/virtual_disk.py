# virtual_disk.py
import os
import threading
from typing import Optional, Dict, Tuple, List

class VirtualDiskError(Exception):
    pass

class VirtualDisk:
    """
    File-backed virtual disk.
    Stores files under a directory and enforces a capacity (MB).
    """
    def __init__(self, root_path: str, capacity_mb: int = 100):
        self.root = os.path.abspath(root_path)
        self.capacity = int(capacity_mb) * 1024 * 1024
        self.lock = threading.RLock()
        os.makedirs(self.root, exist_ok=True)

    def _full_path(self, filename: str) -> str:
        safe = os.path.normpath(filename).lstrip(os.sep)
        return os.path.join(self.root, safe)

    def used_bytes(self) -> int:
        total = 0
        for dirpath, _, filenames in os.walk(self.root):
            for f in filenames:
                try:
                    total += os.path.getsize(os.path.join(dirpath, f))
                except OSError:
                    pass
        return total

    def free_bytes(self) -> int:
        return max(0, self.capacity - self.used_bytes())

    def list_files(self) -> List[Tuple[str,int]]:
        out = []
        for dirpath, _, filenames in os.walk(self.root):
            for f in filenames:
                p = os.path.join(dirpath, f)
                try:
                    out.append((os.path.relpath(p, self.root), os.path.getsize(p)))
                except OSError:
                    pass
        return out

    def write_file(self, filename: str, data: bytes, overwrite: bool = False):
        with self.lock:
            path = self._full_path(filename)
            dirp = os.path.dirname(path)
            os.makedirs(dirp, exist_ok=True)

            # If file exists and not overwrite, raise
            if os.path.exists(path) and not overwrite:
                raise VirtualDiskError("File exists and overwrite is False")

            # compute required space: if overwriting, subtract old size
            old_size = os.path.getsize(path) if os.path.exists(path) else 0
            needed = len(data) - old_size
            if needed > self.free_bytes():
                raise VirtualDiskError(f"Not enough disk space: need {needed} bytes, free {self.free_bytes()}")

            # write data
            tmp = path + ".tmp"
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, path)
            return os.path.relpath(path, self.root)

    def read_file(self, filename: str) -> bytes:
        with self.lock:
            path = self._full_path(filename)
            if not os.path.exists(path):
                raise VirtualDiskError("File not found")
            with open(path, "rb") as f:
                return f.read()

    def delete_file(self, filename: str):
        with self.lock:
            path = self._full_path(filename)
            if os.path.exists(path):
                os.remove(path)
                # try to cleanup empty dirs
                try:
                    d = os.path.dirname(path)
                    while d and d != self.root:
                        if not os.listdir(d):
                            os.rmdir(d)
                            d = os.path.dirname(d)
                        else:
                            break
                except OSError:
                    pass
                return True
            return False

    def stat(self) -> Dict:
        with self.lock:
            return {
                "capacity_bytes": self.capacity,
                "used_bytes": self.used_bytes(),
                "free_bytes": self.free_bytes(),
                "files_count": len(self.list_files())
            }
