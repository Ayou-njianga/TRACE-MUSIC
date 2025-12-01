from utils.logging_config import setup_logging
from utils.exceptions import NodeNotFoundError

log_getter = setup_logging()
logger = log_getter(__name__)


class Message:
    def __init__(self, src, dest, mtype, payload):
        self.src = src
        self.dest = dest
        self.type = mtype
        self.payload = payload


class StorageVirtualNetwork:
    """
    Decoupled virtual network for TRACE-MUSIC.
    Routes messages between nodes and coordinator.
    """

    def __init__(self):
        self.nodes = {}
        logger.info("StorageVirtualNetwork initialized")

    def add_node(self, node):
        node.network = self
        self.nodes[node.node_id] = node
        logger.info(f"Node '{node.node_id}' joined the network")
        node.heartbeat.start()  # start heartbeat thread

    def get_node(self, node_id):
        if node_id not in self.nodes:
            raise NodeNotFoundError(f"Node '{node_id}' not found")
        return self.nodes[node_id]

    def send_message(self, src_id, dest_id, mtype, payload=None):
        if dest_id not in self.nodes:
            raise NodeNotFoundError(dest_id)

        msg = Message(src_id, dest_id, mtype, payload or {})
        logger.debug(
            f"Routing message {mtype} from '{src_id}' to '{dest_id}'"
        )
        self.nodes[dest_id].on_message(msg)

    def broadcast(self, src_id, mtype, payload=None):
        for node_id in self.nodes:
            if node_id != src_id:
                self.send_message(src_id, node_id, mtype, payload)
