# Frontend-Backend Integration Checklist

## ✅ Integration Status

### Frontend & Backend Architecture
- [x] **Frontend Files Exist**: Client and Provider portals present
  - `frontend/apps/client/public/index.html` - Client portal
  - `frontend/apps/client/public/main.js` - Client logic
  - `frontend/apps/provider/public/index.html` - Provider portal
  - `frontend/apps/provider/public/main.js` - Provider logic

- [x] **Static Files Mounted**: Backend serves frontend apps
  - `/client` → mounts `frontend/apps/client/public` with html=True
  - `/provider` → mounts `frontend/apps/provider/public` with html=True
  - `/` → redirects to `/client/` for convenience

- [x] **CORS Enabled**: Backend allows requests from any origin
  - CORSMiddleware added to FastAPI app
  - Allows all methods and headers (safe for development)

- [x] **API Routes Exist**: All frontend endpoints implemented in backend
  - `/auth/*` - Authentication endpoints (login, register, verify-otp, profile, files, quota check, users)
  - `/files` - File upload/list/download/delete
  - `/nodes/*` - Node management (create, start, stop, delete, restart, details)
  - `/status` - System status
  - `/metrics` - Performance metrics
  - `/network/*` - Network service control
  - `/capacity` - Capacity information

### Frontend API Usage
- [x] **Relative URL Paths**: Frontend uses relative paths (`/auth/login`, `/files`)
  - Works with any host/port the backend runs on
  - No hardcoded localhost references

- [x] **Client Portal Features**:
  - ✅ Login/Register (OTP verification)
  - ✅ File upload with quota check
  - ✅ File listing and download
  - ✅ File deletion
  - ✅ Profile/storage usage display

- [x] **Provider Portal Features**:
  - ✅ Node creation (single & batch)
  - ✅ Node management (start/stop/restart/delete)
  - ✅ Node details and health monitoring
  - ✅ Network service control
  - ✅ Metrics dashboard
  - ✅ User management and quota updates

### Backend Dependencies
- [x] **Required Packages Installed**:
  - fastapi - REST API framework
  - uvicorn - ASGI server
  - pydantic - Data validation
  - grpcio - gRPC support
  - grpcio-tools - gRPC compilation
  - pyyaml - Configuration parsing
  - bcrypt - Password hashing
  - starlette - CORS middleware support

### Service Dependencies
- [x] **Backend Requires**:
  - CloudRPC server running on port 50051
  - AuthService running on port 51234
  - Backend runs on port 8000

## Running the System

### Quick Start (Recommended)
```powershell
# From repository root:
.\start_all.ps1
```
This launches:
1. CloudRPC server (Port 50051)
2. AuthService (Port 51234)
3. Backend REST API (Port 8000)
4. Opens http://127.0.0.1:8000/client/ in browser

### Manual Start (if needed)
```powershell
# Terminal 1: CloudRPC server
cd cloudrpc
.\start_cloudrpc.ps1

# Terminal 2: AuthService
cd AuthService
.\start_authservice.ps1

# Terminal 3: Backend
cd backend
python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```

### Access Points
- **Client Portal**: http://127.0.0.1:8000/client/
- **Provider Portal**: http://127.0.0.1:8000/provider/
- **API Status**: http://127.0.0.1:8000/status

## Testing Integration

### Health Check Endpoints
```bash
# Check backend is running
curl http://127.0.0.1:8000/status

# Test imports
curl http://127.0.0.1:8000/test/imports

# Get system info
curl http://127.0.0.1:8000/system/info
```

### API Test Workflow
1. **Register** → POST /auth/register
2. **Login** → POST /auth/login (sends OTP)
3. **Verify OTP** → POST /auth/verify-otp
4. **Create Nodes** → POST /nodes or POST /nodes/batch
5. **Start Nodes** → POST /nodes/{node_id}/start
6. **Upload File** → POST /files (multipart form)
7. **List Files** → GET /auth/files/{username}
8. **Download File** → GET /files/{file_id}/download

## Known Limitations & Notes

- **Authentication**: OTP sent to user's email (requires AuthService email config)
- **Storage**: Virtual nodes use local filesystem in `node1_storage/` directory
- **Network**: Simulated TCP network between nodes (no real network traffic)
- **Metrics**: Collected in-memory (resets when backend stops)
- **Frontend**: SPA (Single Page Application) with client-side routing using hash (#/)

## Troubleshooting

### Frontend won't load
- Ensure backend is running on port 8000
- Check browser console (F12) for errors
- Verify `frontend/apps/client/public/` files exist

### API calls return 503/Connection Refused
- CloudRPC server not running (required by backend)
- AuthService not running (required by auth endpoints)
- Check individual service logs

### Files won't upload
- Create at least one node first via Provider portal
- Start the node before uploading
- Ensure network service is running

### Auth fails
- AuthService must be running on port 51234
- Check `AuthService/users.json` for user records
- OTP email may not be configured (see AuthService/params.py)
