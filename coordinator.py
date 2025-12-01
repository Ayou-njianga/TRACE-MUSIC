# coordinator.py
from utils.logging_config import setup_logging
from utils.config import load_config
from utils.health import NodeRegistry
from utils.exceptions import NodeNotFoundError
import hashlib
from utils.exceptions import StorageError

log_getter = setup_logging()
logger = log_getter(__name__)


class Coordinator:
    """
    Central controller of TRACE-MUSIC.
    Handles node registration, heartbeats, and replication.
    """

    def __init__(self, network):
        self.network = network
        self.cfg = load_config()

        self.registry = NodeRegistry()

        logger.info("Coordinator initialized")

    def add_node(self, node):
        self.network.add_node(node)
        self.registry.mark_seen(node.node_id)
        logger.info(f"Coordinator registered node '{node.node_id}'")

    def list_nodes(self):
        return list(self.network.nodes.keys())

    def on_message(self, message):
        """
        Coordinator receives messages (e.g., heartbeats).
        """
        if message.type == "heartbeat":
            self.registry.mark_seen(message.src)
            logger.debug(f"Heartbeat received from {message.src}")

    def replicate(self, key, data, exclude_node=None):
        R = self.cfg["network"]["replication_factor"]
        nodes = [
            n for n in self.network.nodes
            if n != exclude_node
        ][:R]

        logger.info(f"Replicating '{key}' to {nodes}")

        for n in nodes:
            self.network.send_message("coordinator", n, "replicate", {
                "key": key,
                "data": data
            })


    def hash_data(self, data: bytes):
        return hashlib.sha256(data).hexdigest()

    def upload(self, key: str, data: bytes):
        """
        Upload a file into the distributed storage system.
        Stored on the first node, then replicated.
        """
        # pick first node for storage
        nodes = list(self.network.nodes.values())
        if not nodes:
            raise StorageError("No nodes available")

        primary = nodes[0]

        if not primary.store(key, data):
            raise StorageError("Primary storage failed")

        # replicate to others
        self.replicate(key, data, exclude_node=primary.node_id)

        logger.info(f"Upload complete for key '{key}'")
        return True

    def download(self, key: str):
        """
        Try retrieving from any node.
        """
        for node in self.network.nodes.values():
            data = node.retrieve(key)
            if data is not None:
                logger.info(f"Retrieved '{key}' from {node.node_id}")
                return data
        return None


    def check_node_health(self):
        """
        Called periodically to detect dead nodes.
        """
        timeout = self.cfg["node"]["heartbeat_timeout"]
        dead_nodes = self.registry.stale_nodes(timeout)

        for node_id in dead_nodes:
            logger.warning(f"Node '{node_id}' is offline")


