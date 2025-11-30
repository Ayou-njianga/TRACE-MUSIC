# coordinator.py
import os
import subprocess
import time
import json
import signal
import sys

from main import node1

ROOT = os.path.dirname(os.path.abspath(__file__))
NODES_DIR = os.path.join(ROOT, "nodes")
PYTHON = sys.executable  # use same python interpreter
NODE_SCRIPT = os.path.join(ROOT, "node_service.py")


def prepare_node_dir(node_name):
    d = os.path.join(NODES_DIR, node_name)
    os.makedirs(d, exist_ok=True)
    return d

def launch_nodes(n=5, start_port=8001, capacity_mb=100):
    procs = []
    peers = []
    for i in range(n):
        node_name = f"node{i+1}"
        storage = prepare_node_dir(node_name)
        port = start_port + i
        # Node args
        args = [PYTHON, NODE_SCRIPT,
                "--node-id", node_name,
                "--host", "0.0.0.0",
                "--port", str(port),
                "--storage-path", storage,
                "--capacity-mb", str(capacity_mb)]
        print("Launching", " ".join(args))
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        procs.append((node_name, port, p))
        peers.append({"host": "127.0.0.1", "port": port})
        time.sleep(0.2)  # slight stagger

    # Give nodes some time to start
    time.sleep(2)
    print("All nodes launched. Writing peers list to nodes/peers.json")
    with open(os.path.join(NODES_DIR, "peers.json"), "w") as f:
        json.dump(peers, f, indent=2)

    print("Coordinator controls:")
    print(" - To stop all nodes: press Ctrl-C here or run kill on each PID")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping nodes...")
        for name, port, p in procs:
            try:
                p.send_signal(signal.SIGINT)
            except Exception:
                try:
                    p.terminate()
                except Exception:
                    pass
        print("Stopped.")


def replicate(self, key, data, exclude_node=None):
    nodes = self.select_nodes_for_replication(exclude_node, count=self.cfg["network"]["replication_factor"])
    for n in nodes:
        self.network.send_message("coordinator", n, "replicate", {"key": key, "data": data})


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--nodes", type=int, default=5)
    parser.add_argument("--start-port", type=int, default=8001)
    parser.add_argument("--capacity-mb", type=int, default=100)
    args = parser.parse_args()
    os.makedirs(NODES_DIR, exist_ok=True)
    launch_nodes(n=args.nodes, start_port=args.start_port, capacity_mb=args.capacity_mb)


class Coordinator:
    
    pass