# Setup & Run Guide (Windows)

This document complements the `README.md` with expanded setup and run instructions, common troubleshooting steps, and tips for development.

## Requirements
- Windows 10/11
- PowerShell (v5.1 or later)
- Python 3.10+ on PATH
- Recommended: Use a Python virtual environment

## Create and activate venv

```powershell
cd <repo-root>
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Install dependencies

Core runtime dependencies required by the system:

```powershell
pip install fastapi uvicorn grpcio grpcio-tools pydantic pyyaml
```

If you plan to run tests:

```powershell
pip install pytest
```

Note: `CloudSim/requirements.txt` already lists `pyyaml` and can be extended if you decide to pin versions.

## Start services (convenience script)

From the repository root run:

```powershell
.\start_all.ps1
```

This will open three PowerShell windows:
- `cloudrpc` gRPC server (control plane) — default port `50051`
- `AuthService` gRPC auth server — default port `51234`
- `backend` FastAPI REST gateway — serves on `127.0.0.1:8000`

It also opens the client portal at `http://127.0.0.1:8000/client/` in your default browser.

## Start services manually

If you prefer to start services manually for debugging, open separate PowerShell windows and run:

```powershell
# CloudRPC
cd cloudrpc
./start_cloudrpc.ps1

# AuthService
cd AuthService
./start_authservice.ps1

# Backend
cd backend
./start_backend.ps1
```

## Run tests

```powershell
pip install pytest
pytest CloudSim/tests
```

## Troubleshooting

- "gRPC server not available" in the backend logs: make sure `cloudrpc` is running and listening on the configured port (`50051`).
- Port conflicts: check `CloudSim/config.yaml` and ensure ports are free or adjusted.
- Static files not found: verify `frontend/apps/client/public` exists and `backend` is running on port `8000`.
- Missing Python packages: install packages shown in the `pip install` step earlier.

## Development tips
- Use the `CloudSim/config.yaml` to tune replication and storage defaults.
- Use `backend/api.py` as the REST gateway for rapid integration testing with the front-end static files.

## Further reading
- `README.md` for project overview and quickstart
- `CONTRIBUTING.md` for contribution workflow
