# utils/health.py
import time, threading
from typing import Dict

class NodeRegistry:
    def __init__(self):
        self._nodes = {}  # node_id -> last_seen_ts

    def mark_seen(self, node_id):
        self._nodes[node_id] = time.time()

    def stale_nodes(self, timeout):
        now = time.time()
        return [n for n, t in self._nodes.items() if now - t > timeout]

# a simple thread that checks for staleness
def start_monitor(registry: NodeRegistry, timeout: int, check_interval: int, on_stale):
    def _run():
        while True:
            stale = registry.stale_nodes(timeout)
            for n in stale:
                on_stale(n)
            time.sleep(check_interval)
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t
