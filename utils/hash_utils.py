import hashlib

def compute_hash(data: bytes) -> str:
    """
    Compute SHA-256 hash of byte data.
    Returns hex digest string.
    """
    sha = hashlib.sha256()
    sha.update(data)
    return sha.hexdigest()


def compute_file_hash(path) -> str:
    """
    Compute SHA-256 hash of a file stored on disk.
    """
    sha = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(4096)
            if not chunk:
                break
            sha.update(chunk)
    return sha.hexdigest()
