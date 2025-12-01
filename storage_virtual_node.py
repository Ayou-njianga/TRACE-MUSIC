import os
from pathlib import Path
from storage_node_base import StorageNodeBase
from utils.logging_config import setup_logging
from utils.decorators import log_exceptions
from utils.config import load_config
from utils.heartbeat_sender import HeartbeatSender
from utils.hash_utils import compute_hash, compute_file_hash

cfg = load_config()
log_getter = setup_logging()
logger = log_getter(__name__)


class StorageVirtualNode(StorageNodeBase):
    """
    Represents a storage node in the TRACE-MUSIC platform.
    Stores data in a directory named after the node_id.
    """

    def __init__(
        self,
        node_id: str,
        cpu_capacity: int = 4,
        memory_capacity: int = 8,
        storage_capacity: int = 1000,
        bandwidth: int = 1000,
    ):
        super().__init__(node_id)

        self.network = None  # will be set by coordinator/network
        self.heartbeat = HeartbeatSender(self, cfg["node"]["heartbeat_interval"])

        self.cpu_capacity = cpu_capacity
        self.memory_capacity = memory_capacity
        self.storage_capacity = storage_capacity
        self.bandwidth = bandwidth

        self.data_dir = Path(cfg["paths"]["data_dir"]) / self.node_id
        self.data_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Node {self.node_id} initialized with storage at {self.data_dir}")


    def _path(self, key: str):
        safe = key.replace("/", "_")
        return self.data_dir / safe

    @log_exceptions(logger)
    def store(self, key: str, data: bytes) -> bool:
        try:
            with open(self._path(key), "wb") as fh:
                fh.write(data)

            hash_value = compute_hash(data)
            logger.info(f"[{self.node_id}] Stored '{key}' (hash={hash_value})")

            # store hash in metadata file
            (self._path(key).with_suffix(".hash")).write_text(hash_value)

            return True
        except Exception as e:
            logger.error(f"[{self.node_id}] Storage failure for '{key}': {e}")
            return False

    def retrieve(self, key: str) -> bytes | None:
        p = self._path(key)
        if not p.exists():
            logger.warning(f"[{self.node_id}] '{key}' not found")
            return None
        data = p.read_bytes()
        logger.info(f"[{self.node_id}] Retrieved '{key}'")
        return data

    def delete(self, key: str) -> bool:
        p = self._path(key)
        try:
            p.unlink()
            logger.info(f"[{self.node_id}] Deleted '{key}'")
            return True
        except FileNotFoundError:
            logger.warning(f"[{self.node_id}] Tried to delete missing key '{key}'")
            return False

    def verify_integrity(self, key: str) -> bool:
        """
        Compare stored hash file with recomputed hash.
        Returns True if file integrity OK.
        """
        data_path = self._path(key)
        hash_path = data_path.with_suffix(".hash")

        if not data_path.exists() or not hash_path.exists():
            logger.warning(f"[{self.node_id}] Integrity check failed: missing file or hash")
            return False

        stored_hash = hash_path.read_text().strip()
        computed = compute_file_hash(data_path)

        logger.info(f"[{self.node_id}] Integrity check for '{key}': stored={stored_hash}, computed={computed}")

        return stored_hash == computed

    def on_message(self, message):
        """
        Handle incoming network messages.
        """
        logger.debug(
            f"[{self.node_id}] Received message type='{message.type}' from={message.src}"
        )

        if message.type == "replicate":
            self.store(message.payload["key"], message.payload["data"])

        elif message.type == "heartbeat":
            # Nodes may optionally track coordinator heartbeats
            pass
