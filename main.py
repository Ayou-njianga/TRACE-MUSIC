import argparse
import logging
from coordinator import Coordinator
from storage_virtual_network import StorageVirtualNetwork
from storage_virtual_node import StorageVirtualNode
from utils.config import load_config
from utils.logging_config import setup_logging


def build_sample_network(network):
    """
    Temporary testing network
    """
    n1 = StorageVirtualNode("node1")
    n2 = StorageVirtualNode("node2")

    network.add_node(n1)
    network.add_node(n2)


def main():
    cfg = load_config()
    log_getter = setup_logging(
        level=getattr(logging, cfg["logging"]["level"]),
        logfile=cfg["logging"]["file"]
    )
    logger = log_getter(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["start", "list-nodes", "add-node"])
    parser.add_argument("--node-id")
    args = parser.parse_args()

    network = StorageVirtualNetwork()
    coord = Coordinator(network)

    build_sample_network(network)

    if args.command == "start":
        logger.info("TRACE-MUSIC system started")
    elif args.command == "list-nodes":
        print(coord.list_nodes())
    elif args.command == "add-node":
        if not args.node_id:
            print("Error: --node-id required")
        else:
            node = StorageVirtualNode(args.node_id)
            coord.add_node(node)
            print(f"Node '{args.node_id}' added.")


if __name__ == "__main__":
    main()
