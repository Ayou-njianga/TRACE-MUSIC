# node_service.py
import argparse
import json
import os
import threading
import time
from typing import Optional

from flask import Flask, jsonify, request, send_file, abort

from main import logger
from virtual_disk import VirtualDisk, VirtualDiskError
import requests

app = Flask(__name__)
node_info = {}
disk: Optional[VirtualDisk] = None
peers = set()
peers_lock = threading.RLock()


def on_message(self, message):
    logger.debug("Node %s received %s", self.node_id, message.type)
    if message.type == "heartbeat":
        self.handle_heartbeat(message)
    elif message.type == "replicate":
        self.store(message.payload['key'], message.payload['data'])


@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "node_id": node_info.get("node_id"),
        "port": node_info.get("port"),
        "addr": node_info.get("addr"),
        "disk": disk.stat()
    })

@app.route("/list", methods=["GET"])
def list_files():
    return jsonify({"files": disk.list_files()})

@app.route("/store", methods=["POST"])
def store():
    if 'file' not in request.files:
        return jsonify({"error": "missing file parameter"}), 400
    f = request.files['file']
    filename = request.form.get("filename") or f.filename or f"upload_{int(time.time())}"
    data = f.read()
    try:
        rel = disk.write_file(filename, data, overwrite=bool(request.form.get("overwrite","0")=="1"))
        return jsonify({"stored": rel}), 201
    except VirtualDiskError as e:
        return jsonify({"error": str(e)}), 507

@app.route("/retrieve/<path:name>", methods=["GET"])
def retrieve(name):
    try:
        data = disk.read_file(name)
    except VirtualDiskError:
        abort(404)
    # serve from a temp path to let flask set headers correctly
    temp_path = os.path.join(node_info['tmpdir'], f"tmp_{int(time.time()*1000)}")
    with open(temp_path, "wb") as w:
        w.write(data)
    return send_file(temp_path, as_attachment=True, download_name=os.path.basename(name))

@app.route("/delete/<path:name>", methods=["DELETE"])
def delete(name):
    ok = disk.delete_file(name)
    if ok:
        return jsonify({"deleted": name})
    return jsonify({"error": "not found"}), 404

@app.route("/peers", methods=["GET"])
def get_peers():
    with peers_lock:
        return jsonify({"peers": list(peers)})

@app.route("/peer", methods=["POST"])
def add_peer():
    body = request.json or {}
    host = body.get("host")
    port = body.get("port")
    if not host or not port:
        return jsonify({"error": "host and port required"}), 400
    with peers_lock:
        peers.add(f"http://{host}:{port}")
    return jsonify({"added": f"http://{host}:{port}"}), 201

# background heartbeat to peers
def heartbeat_loop(interval=10):
    while True:
        with peers_lock:
            peer_list = list(peers)
        for p in peer_list:
            try:
                r = requests.get(p + "/status", timeout=2)
                # we could update local peer metadata; right now just check reachability
                if r.status_code != 200:
                    pass
            except Exception:
                pass
        time.sleep(interval)

def run_node(node_id, host, port, storage_path, capacity_mb):
    global node_info, disk
    node_info = {
        "node_id": node_id,
        "addr": host,
        "port": port,
        "tmpdir": os.path.abspath(storage_path)
    }
    disk = VirtualDisk(storage_path, capacity_mb)
    # start heartbeat thread
    t = threading.Thread(target=heartbeat_loop, args=(10,), daemon=True)
    t.start()
    # start flask app
    app.run(host=host, port=port, threaded=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start a simple storage node")
    parser.add_argument("--node-id", required=True)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--storage-path", required=True)
    parser.add_argument("--capacity-mb", type=int, default=100)
    args = parser.parse_args()
    run_node(args.node_id, args.host, args.port, args.storage_path, args.capacity_mb)
