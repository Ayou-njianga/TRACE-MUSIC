# utils/exceptions.py
class TRACEError(Exception):
    """Base error for the TRACE-MUSIC project."""

class NodeNotFoundError(TRACEError):
    pass

class StorageError(TRACEError):
    pass
