# storage_node_base.py
from abc import ABC, abstractmethod

class StorageNodeBase(ABC):
    def __init__(self, node_id: str):
        self.node_id = node_id

    @abstractmethod
    def store(self, key: str, data: bytes) -> bool:
        """Store bytes for key. Return True on success."""

    @abstractmethod
    def retrieve(self, key: str) -> bytes | None:
        """Return bytes or None if not found."""

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key and return True if deleted."""
