#!/usr/bin/env python3
import requests, time, io, sys
BASE = 'http://localhost:8000'

def p(msg):
    print(msg)

# Unique IDs
ts = int(time.time())
node_id = f"cli_test_node_{ts}"
username = f"cli_test_user_{ts}"
email = f"{username}@example.com"

# 1. Create node
p('\n== Create node ==')
resp = requests.post(f"{BASE}/nodes", json={
    "node_id": node_id,
    "cpu": 1,
    "memory": 1,
    "storage": 5,
    "bandwidth": 50,
    "host": "localhost"
}, timeout=10)
print('Create node status:', resp.status_code, resp.text)
if resp.status_code != 200:
    sys.exit(1)

# 2. Start node
p('\n== Start node ==')
resp = requests.post(f"{BASE}/nodes/{node_id}/start", timeout=10)
print('Start node status:', resp.status_code, resp.text)

# 3. Wait for node to appear running in /status
p('\n== Poll status for running nodes ==')
for i in range(12):
    try:
        r = requests.get(f"{BASE}/status", timeout=5)
        if r.status_code==200:
            nodes = r.json().get('nodes', [])
            for n in nodes:
                if n.get('node_id')==node_id and n.get('running'):
                    p('Node is running')
                    break
            else:
                p(f'Attempt {i+1}: node not running yet')
                time.sleep(1)
                continue
            break
    except Exception as e:
        p('Status check error: '+str(e))
        time.sleep(1)
else:
    p('Node did not become running in time')

# 4. Register user
p('\n== Register test user ==')
resp = requests.post(f"{BASE}/auth/register", json={
    'username': username,
    'email': email,
    'password': 'testpass123',
    'quota_gb': 1
}, timeout=10)
print('Register status:', resp.status_code, resp.text)
if resp.status_code != 200:
    p('Registration may have failed but continuing')

# 5. Upload file
p('\n== Upload file ==')
file_content = b'hello world from test ' + str(ts).encode()
files = {'file': ('test.txt', io.BytesIO(file_content), 'text/plain'), 'user': (None, username)}
try:
    r = requests.post(f"{BASE}/files", files=files, timeout=30)
    print('Upload status:', r.status_code, r.text)
    if r.status_code==200:
        file_id = r.json().get('file_id')
    else:
        file_id = None
except Exception as e:
    print('Upload error', e)
    file_id = None

# 6. Download file
p('\n== Download file ==')
if file_id:
    r = requests.get(f"{BASE}/files/{file_id}/download", timeout=20)
    print('Download status:', r.status_code)
    if r.status_code==200:
        data = r.content
        print('Downloaded bytes:', len(data))
        if data.startswith(b'hello world'):
            print('Content looks correct')
        else:
            print('Content mismatch')
    else:
        print('Download failed:', r.text)
else:
    print('No file_id from upload; skipping download')

# 7. Delete file
p('\n== Delete file ==')
if file_id:
    r = requests.delete(f"{BASE}/files/{file_id}?user={username}", timeout=10)
    print('Delete status:', r.status_code, r.text)
else:
    print('No file to delete')

p('\nDone')
