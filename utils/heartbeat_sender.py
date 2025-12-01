import time
import threading

class HeartbeatSender:
    """
    Runs a background thread that periodically sends heartbeat messages
    from a node to the coordinator.
    """

    def __init__(self, node, interval=5):
        self.node = node
        self.interval = interval
        self._running = False

    def start(self):
        if self._running:
            return
        self._running = True
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()

    def _loop(self):
        while self._running:
            try:
                self.node.network.send_message(
                    self.node.node_id,
                    "coordinator",
                    "heartbeat",
                    {"node": self.node.node_id}
                )
            except Exception as e:
                pass
            time.sleep(self.interval)

    def stop(self):
        self._running = False
