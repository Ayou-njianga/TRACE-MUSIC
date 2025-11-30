from flask import logging
import argparse
from coordinator import Coordinator

from storage_virtual_network import StorageVirtualNetwork
from storage_virtual_node import StorageVirtualNode


from utils.logging_config import setup_logging
log_getter = setup_logging()   # configure root logging
logger = log_getter(__name__)

logger.info("Starting TRACE-MUSIC main module")


from utils.config import load_config
cfg = load_config()
log_getter = setup_logging(level=getattr(logging, cfg["logging"]["level"]), logfile=cfg["logging"]["file"])
logger = log_getter(__name__)

# Create network
network = StorageVirtualNetwork()

# Create nodes
node1 = StorageVirtualNode("node1", cpu_capacity=4, memory_capacity=16, storage_capacity=500, bandwidth=1000)
node2 = StorageVirtualNode("node2", cpu_capacity=8, memory_capacity=32, storage_capacity=1000, bandwidth=2000)

# Add nodes to network
network.add_node(node1)
network.add_node(node2)

# Connect nodes with 1Gbps link
network.connect_nodes("node1", "node2", bandwidth=1000)


def main():
    cfg = load_config()
    log_getter = setup_logging(level=getattr(logging, cfg['logging']['level']), logfile=cfg['logging']['file'])
    logger = log_getter(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["start", "add-node", "list-nodes"])
    parser.add_argument("--node-id")
    args = parser.parse_args()

    coord = Coordinator(cfg)
    if args.command == "start":
        coord.start()
        logger.info("Coordinator started")
    elif args.command == "add-node":
        coord.add_node(args.node_id)
    elif args.command == "list-nodes":
        print(coord.list_nodes())


# Initiate file transfer (100MB file from node1 to node2)
transfer = network.initiate_file_transfer(
    source_node_id="node1",
    target_node_id="node2",
    file_name="large_dataset.zip",
    file_size=100 * 1024 * 1024  # 100MB
)

if transfer:
    print(f"Transfer initiated: {transfer.file_id}")
    
    # Process transfer in chunks
    while True:
        chunks_done, completed = network.process_file_transfer(
            source_node_id="node1",
            target_node_id="node2",
            file_id=transfer.file_id,
            chunks_per_step=3  # Process 3 chunks at a time
        )
        
        print(f"Transferred {chunks_done} chunks, completed: {completed}")
        
        if completed:
            print("Transfer completed successfully!")
            break
            
        # Get network stats
        stats = network.get_network_stats()
        print(f"Network utilization: {stats['bandwidth_utilization']:.2f}%")
        print(f"Storage utilization on node2: {node2.get_storage_utilization()['utilization_percent']:.2f}%")