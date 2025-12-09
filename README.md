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
