#!/usr/bin/env python3
"""
Comprehensive functionality test for TRACE-MUSIC CloudSim system.
Tests all client and provider portal features.
"""

import requests
import json
import time
import sys
from typing import Dict, List, Tuple

# Configuration
BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 10

# Test results tracking
class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.skipped = []
    
    def add_pass(self, test_name: str, message: str = ""):
        self.passed.append((test_name, message))
        print(f"✅ {test_name}" + (f" - {message}" if message else ""))
    
    def add_fail(self, test_name: str, message: str):
        self.failed.append((test_name, message))
        print(f"❌ {test_name}: {message}")
    
    def add_skip(self, test_name: str, reason: str):
        self.skipped.append((test_name, reason))
        print(f"⏭️  {test_name} (skipped: {reason})")
    
    def summary(self):
        total = len(self.passed) + len(self.failed) + len(self.skipped)
        print("\n" + "="*60)
        print(f"TEST SUMMARY: {len(self.passed)}/{total} passed")
        print("="*60)
        if self.failed:
            print("\n❌ FAILED TESTS:")
            for name, msg in self.failed:
                print(f"  - {name}: {msg}")
        if self.skipped:
            print("\n⏭️  SKIPPED TESTS:")
            for name, reason in self.skipped:
                print(f"  - {name}: {reason}")
        return len(self.failed) == 0

results = TestResults()

# ==================== HELPER FUNCTIONS ====================

def check_service(name: str, port: int) -> bool:
    """Check if a service is running by opening a TCP socket to the port."""
    import socket
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            return True
    except Exception:
        return False


# Globals for tests (set in main)
TEST_USERNAME = "testuser"
TEST_EMAIL = "test@example.com"

def test_endpoint(method: str, endpoint: str, expected_status: int = 200, 
                  json_data: Dict = None, form_data: Dict = None, files = None) -> Tuple[bool, str, any]:
    """Test a single endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=TEST_TIMEOUT)
        elif method == "POST":
            response = requests.post(url, json=json_data, data=form_data, files=files, timeout=TEST_TIMEOUT)
        elif method == "DELETE":
            response = requests.delete(url, timeout=TEST_TIMEOUT)
        else:
            return False, f"Unknown method {method}", None
        
        if response.status_code == expected_status:
            try:
                data = response.json()
                return True, "", data
            except:
                return True, "", response.text
        else:
            return False, f"Expected {expected_status}, got {response.status_code}: {response.text[:100]}", None
    except Exception as e:
        return False, str(e), None


def ensure_nodes_running(min_running: int = 1) -> bool:
    """Ensure at least `min_running` nodes are running by creating/starting nodes if needed."""
    try:
        ok, msg, status = test_endpoint("GET", "/status", 200)
        if not ok:
            return False
        nodes = status.get("nodes", [])
        running = sum(1 for n in nodes if n.get("running"))
        if running >= min_running:
            return True

        need = max(0, min_running - running)
        base_id = f"auto_node_{int(time.time())}_"
        payload = {
            "count": need,
            "base_id": base_id,
            "cpu": 1,
            "memory": 1,
            "storage": 5,
            "bandwidth": 50
        }
        ok, msg, data = test_endpoint("POST", "/nodes/batch", 200, json_data=payload)
        if not ok:
            return False
        created = data.get("nodes", [])
        # Start created nodes
        for n in created:
            nid = n.get("node_id") or n.get("id")
            if not nid:
                continue
            test_endpoint("POST", f"/nodes/{nid}/start", 200)
            time.sleep(0.2)

        # Wait briefly for nodes to report running
        for _ in range(10):
            ok, msg, status = test_endpoint("GET", "/status", 200)
            if not ok:
                time.sleep(0.5)
                continue
            nodes = status.get("nodes", [])
            running = sum(1 for n in nodes if n.get("running"))
            if running >= min_running:
                return True
            time.sleep(0.5)
        return False
    except Exception:
        return False

# ==================== CLIENT PORTAL TESTS ====================

def test_client_auth():
    """Test client authentication flow"""
    print("\n📝 CLIENT AUTHENTICATION TESTS")
    print("-" * 60)
    
    # Test register (use unique username)
    global TEST_USERNAME, TEST_EMAIL
    success, msg, data = test_endpoint("POST", "/auth/register", 200, json_data={
        "username": TEST_USERNAME,
        "email": TEST_EMAIL,
        "password": "testpass123",
        "quota_gb": 1
    })
    if success:
        results.add_pass("Register user", data.get("message", ""))
    else:
        results.add_fail("Register user", msg)
        return False
    
    # Test login
    success, msg, data = test_endpoint("POST", "/auth/login", 200, json_data={
        "username": TEST_USERNAME,
        "password": "testpass123"
    })
    if success and "pending_id" in data:
        results.add_pass("Login user", "OTP sent")
        pending_id = data.get("pending_id")
    else:
        results.add_fail("Login user", msg)
        return False
    
    # Test OTP verification (we can't test the actual OTP without email access)
    results.add_skip("Verify OTP", "No email access in tests")
    
    # Test profile
    success, msg, data = test_endpoint("GET", f"/auth/profile/{TEST_USERNAME}", 200)
    if success:
        used = data.get("used_bytes", 0)
        quota = data.get("quota_bytes", 0)
        results.add_pass("Get profile", f"{used}B used of {quota}B quota")
    else:
        results.add_fail("Get profile", msg)
    
    # Test files list
    success, msg, data = test_endpoint("GET", f"/auth/files/{TEST_USERNAME}", 200)
    if success:
        count = data.get("count", 0)
        results.add_pass("Get files list", f"{count} files")
    else:
        results.add_fail("Get files list", msg)
    
    # Test quota check
    success, msg, data = test_endpoint("POST", f"/auth/check-quota/{TEST_USERNAME}?file_size=1000", 200)
    if success:
        allowed = data.get("allowed")
        remaining = data.get("remaining_gb", 0)
        results.add_pass("Check quota", f"Allowed: {allowed}, Remaining: {remaining}GB")
    else:
        results.add_fail("Check quota", msg)
    
    return True

def test_client_storage():
    """Test client file operations"""
    print("\n💾 CLIENT STORAGE TESTS")
    print("-" * 60)
    
    # First check if nodes are available
    success, msg, data = test_endpoint("GET", "/status", 200)
    if not success:
        results.add_skip("Upload file", "Status endpoint not available")
        results.add_skip("Download file", "Status endpoint not available")
        results.add_skip("Delete file", "Status endpoint not available")
        return False
    
    nodes = data.get("nodes", [])
    running = sum(1 for n in nodes if n.get("running"))
    if running == 0:
        # Try to auto-create and start nodes for the test
        created = ensure_nodes_running(min_running=2)
        if not created:
            results.add_skip("Upload file", "No running nodes and auto-create failed")
            results.add_skip("Download file", "No running nodes and auto-create failed")
            results.add_skip("Delete file", "No running nodes and auto-create failed")
            return False
    
    # Test upload
    import io
    test_file = ("test.txt", io.BytesIO(b"test content " * 1000), "text/plain")
    success, msg, data = test_endpoint("POST", "/files", 200, files={"file": test_file, "user": (None, TEST_USERNAME)})
    if success:
        file_id = data.get("file_id", "")
        results.add_pass("Upload file", f"ID: {file_id}")
    else:
        results.add_fail("Upload file", msg)
        return False
    
    # Test download
    success, msg, response_data = test_endpoint("GET", f"/files/{file_id}/download", 200)
    if success:
        results.add_pass("Download file", f"Retrieved {len(response_data) if isinstance(response_data, bytes) else len(str(response_data))} bytes")
    else:
        results.add_fail("Download file", msg)
    
    # Test delete
    success, msg, data = test_endpoint("DELETE", f"/files/{file_id}?user={TEST_USERNAME}", 200)
    if success:
        results.add_pass("Delete file", data.get("message", ""))
    else:
        results.add_fail("Delete file", msg)
    
    return True

# ==================== PROVIDER PORTAL TESTS ====================

def test_provider_nodes():
    """Test provider node management"""
    print("\n🖥️  PROVIDER NODE TESTS")
    print("-" * 60)
    
    # Test get status
    success, msg, data = test_endpoint("GET", "/status", 200)
    if success:
        total = data.get("total_nodes", 0)
        running = data.get("running_nodes", 0)
        results.add_pass("Get status", f"{total} total, {running} running")
    else:
        results.add_fail("Get status", msg)
        return False
    
    # Test create node
    success, msg, data = test_endpoint("POST", "/nodes", 200, json_data={
        "node_id": "test_node_1",
        "cpu": 2,
        "memory": 4,
        "storage": 10,
        "bandwidth": 100,
        "host": "localhost"
    })
    if success:
        node_id = data.get("node_id", "")
        port = data.get("port", "")
        results.add_pass("Create node", f"{node_id} on port {port}")
    else:
        if "already exists" in msg:
            results.add_skip("Create node", "Node already exists")
        else:
            results.add_fail("Create node", msg)
    
    # Test start node
    success, msg, data = test_endpoint("POST", "/nodes/test_node_1/start", 200)
    if success:
        results.add_pass("Start node", data.get("message", ""))
    else:
        results.add_fail("Start node", msg)
    
    time.sleep(0.5)
    
    # Test get node details
    success, msg, data = test_endpoint("GET", "/nodes/test_node_1/details", 200)
    if success:
        running = data.get("running", False)
        storage = data.get("storage", {}).get("utilization_percent", 0) if data.get("storage") else 0
        results.add_pass("Get node details", f"Running: {running}, Storage: {storage}%")
    else:
        results.add_fail("Get node details", msg)
    
    # Test stop node
    success, msg, data = test_endpoint("POST", "/nodes/test_node_1/stop", 200)
    if success:
        results.add_pass("Stop node", data.get("message", ""))
    else:
        results.add_fail("Stop node", msg)
    
    # Test restart node
    success, msg, data = test_endpoint("POST", "/nodes/test_node_1/restart", 200)
    if success:
        results.add_pass("Restart node", data.get("message", ""))
    else:
        results.add_fail("Restart node", msg)
    
    # Test batch create
    success, msg, data = test_endpoint("POST", "/nodes/batch", 200, json_data={
        "count": 2,
        "base_id": "batch_test_",
        "cpu": 2,
        "memory": 4,
        "storage": 10,
        "bandwidth": 100
    })
    if success:
        created = len(data.get("nodes", []))
        results.add_pass("Batch create nodes", f"Created {created} nodes")
    else:
        results.add_fail("Batch create nodes", msg)
    
    # Test delete node
    success, msg, data = test_endpoint("DELETE", "/nodes/test_node_1", 200)
    if success:
        results.add_pass("Delete node", data.get("message", ""))
    else:
        results.add_fail("Delete node", msg)
    
    return True

def test_provider_network():
    """Test provider network management"""
    print("\n🌐 PROVIDER NETWORK TESTS")
    print("-" * 60)
    
    # Test get network status
    success, msg, data = test_endpoint("GET", "/network/status", 200)
    if success:
        running = data.get("running", False)
        nodes = data.get("registered_nodes", 0)
        results.add_pass("Get network status", f"Running: {running}, Nodes: {nodes}")
    else:
        results.add_fail("Get network status", msg)
    
    # Test start network
    success, msg, data = test_endpoint("POST", "/network/start", 200)
    if success:
        results.add_pass("Start network", data.get("message", ""))
    else:
        if "CloudRPC" in msg or "unavailable" in msg.lower():
            results.add_skip("Start network", "CloudRPC not available")
        else:
            results.add_fail("Start network", msg)
    
    time.sleep(0.5)
    
    # Test stop network
    success, msg, data = test_endpoint("POST", "/network/stop", 200)
    if success:
        results.add_pass("Stop network", data.get("message", ""))
    else:
        if "CloudRPC" in msg or "unavailable" in msg.lower():
            results.add_skip("Stop network", "CloudRPC not available")
        else:
            results.add_fail("Stop network", msg)
    
    return True

def test_provider_metrics():
    """Test provider metrics and monitoring"""
    print("\n📊 PROVIDER METRICS TESTS")
    print("-" * 60)
    
    # Test system info
    success, msg, data = test_endpoint("GET", "/system/info", 200)
    if success:
        total_nodes = data.get("nodes", {}).get("total", 0)
        storage_gb = data.get("resources", {}).get("total_storage_gb", 0)
        results.add_pass("Get system info", f"{total_nodes} nodes, {storage_gb}GB storage")
    else:
        results.add_fail("Get system info", msg)
    
    # Test nodes health
    success, msg, data = test_endpoint("GET", "/nodes/health", 200)
    if success:
        healthy = data.get("healthy_count", 0)
        total = data.get("total_count", 0)
        results.add_pass("Get nodes health", f"{healthy}/{total} healthy")
    else:
        results.add_fail("Get nodes health", msg)
    
    # Test metrics
    success, msg, data = test_endpoint("GET", "/metrics", 200)
    if success:
        storage_util = data.get("storage_utilization_percent", 0)
        throughput = data.get("throughput_mbps", 0)
        nodes = len(data.get("node_details", []))
        results.add_pass("Get metrics", f"Utilization: {storage_util}%, Throughput: {throughput}Mbps, {nodes} nodes")
    else:
        results.add_fail("Get metrics", msg)
    
    # Test capacity report
    success, msg, data = test_endpoint("GET", "/capacity/report", 200)
    if success:
        results.add_pass("Get capacity report", "Report generated")
    else:
        results.add_fail("Get capacity report", msg)
    
    return True

def test_provider_users():
    """Test provider user administration"""
    print("\n👥 PROVIDER USER TESTS")
    print("-" * 60)
    
    # Test list all users
    success, msg, data = test_endpoint("GET", "/auth/users", 200)
    if success:
        count = len(data.get("users", []))
        results.add_pass("List all users", f"{count} users")
    else:
        results.add_fail("List all users", msg)
    
    # Test get user metrics
    success, msg, data = test_endpoint("GET", "/metrics/users/testuser", 200)
    if success:
        transfers = data.get("transfer_metrics", {}).get("total_transfers", 0)
        results.add_pass("Get user metrics", f"{transfers} transfers")
    else:
        results.add_fail("Get user metrics", msg)
    
    # Test update quota
    success, msg, data = test_endpoint("POST", "/auth/users/testuser/quota", 200, json_data={
        "quota_gb": 5
    })
    if success:
        results.add_pass("Update user quota", data.get("message", ""))
    else:
        results.add_fail("Update user quota", msg)
    
    return True

# ==================== MAIN EXECUTION ====================

def main():
    print("\n" + "="*60)
    print("TRACE-MUSIC SYSTEM FUNCTIONALITY TEST")
    print("="*60)
    
    # Check services
    print("\n🔍 Checking services...")
    backend_running = check_service("backend", 8000)
    auth_running = check_service("authservice", 51234)
    grpc_running = check_service("cloudrpc", 50051)
    
    print(f"Backend:    {'✅' if backend_running else '❌'}")
    print(f"AuthService: {'✅' if auth_running else '❌'}")
    print(f"CloudRPC:   {'✅' if grpc_running else '❌'}")
    
    if not backend_running:
        print("\n❌ Backend service is not running! Start it first:")
        print("   python -m uvicorn api:app --host 0.0.0.0 --port 8000")
        sys.exit(1)
    # Set unique test user to avoid collisions with previous runs
    global TEST_USERNAME, TEST_EMAIL
    TEST_USERNAME = f"testuser_{int(time.time())}"
    TEST_EMAIL = f"{TEST_USERNAME}@example.com"

    # Run tests
    try:
        test_client_auth()
        test_client_storage()
        test_provider_nodes()
        test_provider_network()
        test_provider_metrics()
        test_provider_users()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n⚠️  Tests failed with exception: {e}")
        import traceback
        traceback.print_exc()
    
    # Print summary
    success = results.summary()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
