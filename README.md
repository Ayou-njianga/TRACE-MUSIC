# TRACE-MUSIC

Distributed cloud storage simulation for the Cameroon music industry. TRACE-MUSIC provides a REST gateway, gRPC services, and a browser-based frontend to create and manage virtual storage nodes, upload/download files split into chunks and replicated across nodes, and monitor system metrics.

This repository contains three main subsystems:

- CloudSim: core simulation and node implementations
- cloudrpc: gRPC server that controls node lifecycle and the network discovery service
- AuthService: gRPC-based authentication and user/account/quota management
- backend: FastAPI REST gateway that exposes operations to web clients and proxies gRPC operations
- frontend: static client and provider portals (HTML + JS)

## Quick Start (Windows)

Prerequisites:

- Python 3.10+ installed and on PATH
- PowerShell (Windows) - scripts provided are PowerShell scripts
- Optional: Create a virtual environment for isolation

1) From repository root, create and activate a venv (optional but recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install Python dependencies (recommended install in the venv):

```powershell
pip install fastapi uvicorn grpcio grpcio-tools pydantic pyyaml
```

3) Start the whole stack (opens separate PowerShell windows and the client in your browser):

```powershell
.\start_all.ps1
```

You can also start subsystems individually:

- Start CloudRPC (gRPC control & network): `cloudrpc\start_cloudrpc.ps1`
- Start AuthService (user mgmt): `AuthService\start_authservice.ps1`
- Start REST backend: `backend\start_backend.ps1`

The REST backend listens on `127.0.0.1:8000`; the client portal is served at `http://127.0.0.1:8000/client/`.

## Project Layout

Top-level folders and their purpose:

- `CloudSim/` — core simulation code (node factory, virtual node, storage/metrics/capacity, tests)
- `cloudrpc/` — gRPC server and proto definitions for managing nodes and the virtual network
- `AuthService/` — authentication gRPC service and its protobufs
- `backend/` — FastAPI REST gateway; serves the frontend static files under `/client` and `/provider`
- `frontend/apps/` — static client and provider portals in `public/`

Key files:

- `start_all.ps1` — convenience script to launch all services and open the client
- `backend/api.py` — REST API gateway (mounts static files and proxies to gRPC services)
- `cloudrpc/server.py` — gRPC CloudRPC service (node lifecycle + network)
- `AuthService/cloud.py` — AuthService gRPC implementation

## How storage works (high level)

1. Files uploaded via REST are split into chunks.
2. Each chunk is replicated across several virtual nodes (replication factor configurable).
3. Nodes either run as local threads/processes (via `CloudSim` node factory) or are controlled via `cloudrpc` (gRPC) for multi-process setups.
4. Nodes expose a small TCP protocol to receive/store chunks and to serve them back for downloads.

## Tests

Unit tests for the simulation are under `CloudSim/tests/`. Run them with `pytest` from the repository root after installing test dependencies.

```powershell
pip install pytest
pytest CloudSim/tests
```

## Troubleshooting

- If the backend cannot connect to the gRPC servers, ensure `cloudrpc` and `AuthService` windows are started and show no errors.
- If ports conflict, check `CloudSim/config.yaml` and the start scripts for port assignments.
- If static frontend files don’t load, confirm the backend is running on port `8000` and that `frontend/apps/client/public` exists.

## Development notes

- The REST gateway (`backend/api.py`) attempts to use gRPC for node/network operations and falls back to direct `CloudSim` factory calls when gRPC is unavailable.
- Configuration is loaded from `CloudSim/config.yaml`. Adjust replication and storage defaults there.

## Contributing

See `CONTRIBUTING.md` for contribution guidelines, branch/PR policy and testing expectations.

## License & Contact

Add your preferred license file to the repository (e.g., `LICENSE`). For questions or help, open an issue in this repository.

----
Updated documentation and quickstart for the TRACE-MUSIC project.
│    Chunks       Chunks         Chunks               │
└────────────────────────────────────────────────────┘
```

## Features

### Core Storage Features
- **Distributed File Storage**: Files split into 256KB-1MB chunks
- **Automatic Replication**: Default 3-way replication for fault tolerance
- **Distributed Upload/Download**: Chunks streamed over TCP to/from nodes
- **Dynamic Node Management**: Create, start, stop, delete nodes via REST API
- **Storage Utilization Tracking**: Per-node and system-wide metrics

### Authentication & Authorization
- **User Registration**: Create accounts with initial quota (default 1GB)
- **OTP-based Login**: Two-factor authentication via email OTP
- **Quota Management**: Track and enforce per-user storage quotas
- **File Ownership**: Track which files belong to which users

### Monitoring & Metrics
- **Real-time Metrics**: Throughput, latency, RTT, error rates
- **Node Health**: Monitor node status, storage utilization, performance
- **Transfer History**: Track all uploads/downloads with timestamps
- **Capacity Planning**: Predict storage exhaustion and recommend actions
- **Performance Reports**: Network utilization, transfer statistics

### APIs

#### REST Endpoints (FastAPI on Port 8000)

**System Status**
- `GET /status` - Overall system status and node list
- `GET /system/info` - Aggregated resource information
- `GET /metrics` - Comprehensive performance metrics
- `GET /metrics/users/{username}` - User-specific metrics
- `GET /capacity` - Storage capacity information

**File Operations**
- `POST /files` - Upload a file (with replication)
- `GET /files` - List all files in system
- `GET /files/{file_id}/download` - Download a file
- `DELETE /files/{file_id}` - Delete a file

**Node Management**
- `POST /nodes` - Create a single node
- `POST /nodes/batch` - Create multiple nodes
- `GET /nodes/{node_id}/details` - Node details and metrics
- `POST /nodes/{node_id}/start` - Start a stopped node
- `POST /nodes/{node_id}/stop` - Stop a running node
- `POST /nodes/{node_id}/restart` - Restart a node
- `DELETE /nodes/{node_id}` - Delete a node

**Network Management**
- `POST /network/start` - Start network service
- `POST /network/stop` - Stop network service
- `GET /network/status` - Network status and registered nodes

**Authentication** (via gRPC to AuthService)
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user (sends OTP)
- `POST /auth/verify-otp` - Verify OTP and get token
- `GET /auth/profile/{username}` - Get user profile
- `GET /auth/files/{username}` - List user's files
- `POST /auth/check-quota/{username}` - Check upload quota
- `GET /auth/users` - List all users (admin)
- `POST /auth/users/{username}/quota` - Update user quota (admin)

**Frontend**
- `GET /` - Redirect to client portal
- `GET /client/` - Client web portal
- `GET /provider/` - Provider web portal

## Installation

### Prerequisites
- Python 3.8+
- Windows PowerShell (for startup scripts)
- pip package manager

### Step 1: Clone Repository
```powershell
git clone https://github.com/Ayou-njianga/TRACE-MUSIC.git
cd TRACE-MUSIC
```

### Step 2: Install Dependencies
```powershell
# Install CloudSim dependencies
pip install -r CloudSim/requirements.txt

# Install backend dependencies
pip install fastapi uvicorn grpcio grpcio-tools pydantic pyyaml bcrypt
```

### Step 3: Verify Installation
```powershell
# Test imports
python -c "import fastapi, grpc, pydantic, yaml; print('All imports successful!')"
```

## Quick Start

### Option 1: Start All Services (Recommended)
```powershell
cd TRACE-MUSIC
.\start_all.ps1
```

This launches:
1. **CloudRPC Server** (gRPC on port 50051) - Node management
2. **AuthService** (gRPC on port 51234) - User authentication
3. **Backend API** (REST on port 8000) - Main REST gateway
4. **Client Portal** - Opens `http://127.0.0.1:8000/client/` in your browser

### Option 2: Start Services Individually

**Terminal 1 - CloudRPC Server:**
```powershell
cd cloudrpc
.\start_cloudrpc.ps1
```
Runs on: `localhost:50051`

**Terminal 2 - AuthService:**
```powershell
cd AuthService
.\start_authservice.ps1
```
Runs on: `localhost:51234`

**Terminal 3 - Backend API:**
```powershell
cd backend
.\start_backend.ps1
```
Runs on: `http://127.0.0.1:8000`

## Frontend & Backend Integration

### ✅ Integration Status
The frontend and backend are fully integrated:

**Frontend Features:**
- **Client Portal** (`/client/`) - User file storage and management
  - Register/Login with OTP verification
  - Upload files with automatic replication
  - Download and manage files
  - View storage quota and usage
  
- **Provider Portal** (`/provider/`) - Infrastructure management
  - Create and manage virtual nodes
  - Monitor node health and storage
  - Start/stop/restart nodes
  - View real-time metrics
  - Manage user quotas
  - Network service control

**Backend Integration:**
- All frontend pages served statically by FastAPI on port 8000
- CORS middleware enabled for cross-origin requests
- All API endpoints implemented and tested
- Automatic frontend startup with `.\start_all.ps1`

**Access Points:**
- Client Portal: `http://127.0.0.1:8000/client/`
- Provider Portal: `http://127.0.0.1:8000/provider/`
- API Root: `http://127.0.0.1:8000/`

### Typical User Workflows

**Client User:**
1. Open Client Portal
2. Register account (get 1GB free quota)
3. Login via OTP
4. Create nodes via Provider portal
5. Upload files
6. Download files anytime

**Provider Admin:**
1. Open Provider Portal
2. Create 3+ nodes (e.g., Node1, Node2, Node3)
3. Start all nodes
4. Monitor metrics and storage
5. Manage user quotas

## Configuration

Edit `CloudSim/config.yaml` to customize:
- Number of virtual nodes
- Node resources (CPU, memory, storage, bandwidth)
- Storage chunk size
- Replication factor
- Network simulation parameters

Example:
```yaml
node_factory:
  start_port: 5000
  port_range_size: 1000

storage:
  base_directory: storage
  chunk_size_bytes: 524288

replication:
  default_factor: 3
  min_factor: 2
```

## Usage Examples

### Using the Web Portals

**Client Portal** (`http://127.0.0.1:8000/client/`)
- Register a new account
- Login with username and OTP
- Upload files
- Download files
- View file list
- Monitor usage and quota

**Provider Portal** (`http://127.0.0.1:8000/provider/`)
- Create virtual storage nodes
- Monitor node status and health
- View storage utilization
- Check system metrics
- Start/stop nodes

### Using curl/REST API

**Upload a File:**
```bash
curl -X POST "http://127.0.0.1:8000/files" \
  -F "file=@myfile.mp3" \
  -F "user=testuser"
```

**Download a File:**
```bash
curl -X GET "http://127.0.0.1:8000/files/{file_id}/download?user=testuser" \
  -o downloaded_file.mp3
```

**Create a Node:**
```bash
curl -X POST "http://127.0.0.1:8000/nodes" \
  -H "Content-Type: application/json" \
  -d '{
    "node_id": "node1",
    "cpu": 2,
    "memory": 4,
    "storage": 10,
    "bandwidth": 100
  }'
```

**Get System Status:**
```bash
curl "http://127.0.0.1:8000/status"
```

**Register User:**
```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser",
    "email": "user@example.com",
    "password": "password123",
    "quota_gb": 5
  }'
```

## Architecture Details

### Virtual Nodes
- Each node runs in a separate Python thread
- Listens on its own TCP port (5000, 5001, ...)
- Maintains local file chunks on disk
- Tracks storage utilization and network connections
- Simulates realistic cloud node behavior

### Chunk-based Storage
- Files are split into 256KB-1MB chunks for distribution
- Each chunk is replicated to multiple nodes (default 3)
- Chunks identified by `{file_id}_chunk_{index}.bin`
- Checksums (MD5) verify data integrity on transfer
- Round-robin distribution ensures balanced load

### gRPC Communication
- **CloudRPC** (port 50051): Node lifecycle, network management
- **AuthService** (port 51234): User management, quota enforcement
- Enables efficient RPC with protocol buffers
- Separate from REST API for scalability

### Network Simulation
- TCP sockets simulate network transfers
- Configurable latency and bandwidth
- Node discovery service (port 9999)
- Network state tracking and statistics

## Development

### Adding New Endpoints
Edit `backend/api.py` and add FastAPI routes:
```python
@app.get("/api/endpoint")
def my_endpoint():
    return {"message": "Hello World"}
```

### Modifying Node Behavior
Edit `CloudSim/storage_virtual_node.py` to customize node logic.

### Updating Configuration
Edit `CloudSim/config.yaml` or modify `config_loader.py`.

### Running Tests
```powershell
cd CloudSim
pytest tests/
```

## Troubleshooting

### "Port already in use"
- Check if services are already running: `netstat -ano | findstr :8000`
- Kill existing process: `taskkill /PID {pid} /F`

### "Connection refused" to gRPC server
- Ensure CloudRPC server is running on port 50051
- Check firewall settings

### "No nodes available"
- Create nodes via `/nodes` endpoint or Provider portal
- Ensure node processes are running

### "Upload/Download failed"
- Verify at least one node is running
- Check network service is active via `/network/status`
- Review backend logs for detailed error messages

## Performance Characteristics

- **Typical Upload**: 100MB file → ~2-5 seconds (with 3-way replication)
- **Typical Download**: 100MB file → ~1-3 seconds (single stream)
- **Node Creation**: <1 second per node
- **Metrics Collection**: Real-time, <10ms overhead
- **Storage Overhead**: ~3x for 3-way replication (configurable)

## Future Enhancements

- [ ] Erasure coding (reduce storage overhead to 1.5x)
- [ ] Load balancing across nodes
- [ ] Automatic node failover and recovery
- [ ] Data compression
- [ ] Encryption at rest and in transit
- [ ] Multi-region support
- [ ] Kubernetes deployment
- [ ] Mobile apps (iOS/Android)
- [ ] Advanced analytics dashboard

## License

Proprietary - TRACE-MUSIC Project

## Author

Ayouba Njianga - Cameroon Music Industry Innovation

## Support

For issues and questions, please open an issue on GitHub or contact the development team.
