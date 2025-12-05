# main_app.py
from storage_virtual_network import StorageVirtualNetwork
from storage_virtual_node import StorageVirtualNode
from coordinator import Coordinator
from utils import db

# Initialize DB (make sure db.init_db() was called elsewhere; db module does that in our dashboard)
db.init_db()

# Build network and coordinator
NETWORK = StorageVirtualNetwork()
COORD = Coordinator(NETWORK)

# On startup, ensure nodes in DB are registered in network
for n in db.list_nodes():
    # create StorageVirtualNode (basic) and add to network and coordinator
    node_obj = StorageVirtualNode(node_id=n['node_id'], memory_capacity=n.get('memory',1024))
    NETWORK.add_node(node_obj)
    COORD.add_node(node_obj)

def add_node(node_id: str, memory: int=1024):
    # Add DB entry
    db.add_node_to_db(node_id, memory=memory, status="Online")
    # Add actual node to network
    node_obj = StorageVirtualNode(node_id=node_id, memory_capacity=memory)
    NETWORK.add_node(node_obj)
    COORD.add_node(node_obj)
    return True

def list_nodes():
    return db.list_nodes()
