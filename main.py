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
    parser.add_argument("command", choices=["start", "list-nodes", "add-node", "upload", "download"])
    parser.add_argument("--node-id")
    parser.add_argument("--file")
    parser.add_argument("--key")
    parser.add_argument("--output")
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

    elif args.command == "upload":
        if not args.file:
            print("Error: --file required")
        else:
            with open(args.file, "rb") as fh:
                data = fh.read()
            key = args.key or args.file
            coord.upload(key, data)
            print(f"Uploaded '{key}'")

    elif args.command == "download":
        if not args.key:
            print("Error: --key required")
        else:
            data = coord.download(args.key)
            if data is None:
                print("File not found")
            else:
                out = args.output or args.key
                with open(out, "wb") as fh:
                    fh.write(data)
                print(f"Downloaded to '{out}'")

if __name__ == "__main__":
    main()
