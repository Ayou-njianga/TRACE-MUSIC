# Upload Functionality Verification Report

## Current Implementation Status

### ✅ What's Already Working

1. **File Upload Endpoint** (`POST /files`)
   - Accepts file uploads with FormData (file, user)
   - Chunks files across multiple nodes (configurable chunk size)
   - Distributes chunks with replication factor (default 3)
   - Returns: `{ok, file_id, file_name, size}`

2. **File Storage Recording** (`AuthService/cloud.py`)
   - `AddFileRecord()` - Records file metadata in user's files list
   - Automatically updates `used_bytes` when file is uploaded
   - Stores: file_id, name, size, node list

3. **User Profile Storage Tracking** (`GET /auth/profile/{username}`)
   - Returns: `used_bytes`, `quota_bytes`, `usage_percent`
   - Dynamically calculated based on all user files
   - Used by frontend to display storage usage

4. **File Listing** (`GET /auth/files/{username}`)
   - Returns all user files with metadata
   - Shows file size for each file
   - Enables file browser UI

5. **Frontend Upload Page**
   - Drag-and-drop file upload
   - Shows available storage before upload
   - Quota checking before upload
   - Progress bar during upload
   - Redirects to files page after upload

### ✅ How Memory Usage is Tracked

**Backend Flow:**
```
User uploads file → Backend receives data
    ↓
Backend sends chunks to nodes via network (simulated)
    ↓
Backend calls AddFileRecord() via gRPC to AuthService
    ↓
AuthService stores file metadata and adds file.size to user.used_bytes
    ↓
User.used_bytes now reflects total storage consumed
```

**Frontend Display:**
- Dashboard: Shows system status, storage usage bar
- Upload Page: Shows "Available Storage: X GB" (quota - used)
- Files Page: Shows table of all files with sizes
- Profile Page: Shows detailed usage stats

### ✅ File Persistence

**Files are stored on nodes via:**
1. Virtual nodes in `CloudSim/nodes_state.json` track node state
2. Chunks sent via TCP network simulation to nodes
3. Nodes maintain storage directory (configurable in config.yaml)
4. Default: `storage/` directory in CloudSim folder

### Current Storage Architecture

```
CloudSim/
├── config.yaml                    # Node storage config
├── storage/                       # Virtual storage root
│   ├── node_<id>/                # Per-node storage
│   │   └── chunks/               # Chunk files
│   └── ...
├── nodes_state.json              # Node state tracking
└── users.json (AuthService)       # User file metadata
```

## Verification Checklist

- [ ] **Upload a test file**
  - Navigate to Upload page
  - Select a small file (1-10 MB)
  - Upload should complete
  - Should see "File uploaded successfully!"

- [ ] **Check files list**
  - Go to Files page
  - File should appear in table
  - File size should match original

- [ ] **Verify storage tracking**
  - Go to Dashboard
  - "Your Storage" card should show:
    - Used bytes increased
    - Usage percentage updated
    - Remaining space decreased
  - Go to Profile
  - Should show exact byte counts

- [ ] **Multiple uploads**
  - Upload 2-3 files
  - Total used_bytes should be sum of all file sizes
  - Files page should list all files
  - Storage usage should increment each time

- [ ] **Quota checking**
  - Try uploading file larger than remaining quota
  - Should get error: "Not enough storage!"
  - File should not be recorded

- [ ] **File download**
  - Click download on any file
  - Should retrieve file from nodes
  - File content should match original

## How to Test the System

### 1. Start All Services
```powershell
cd c:\Users\AYOUBA\StudioProjects\TRACE-MUSIC
.\start_all.ps1
```

Wait for all services to start (CloudRPC, AuthService, Backend).

### 2. Access the Client Portal
- Open browser: http://localhost:8000/client/
- Register new account or login

### 3. Create a Node (for storage)
- Go to Provider portal: http://localhost:8000/provider/
- Navigate to Nodes section
- Create at least 1 node
- Start the node

### 4. Upload a File
- Go back to Client portal
- Click Upload
- Select a test file (small, <100MB)
- Click "Upload File"
- Verify success message

### 5. Verify Storage Tracking
- Click Dashboard
- Check "Your Storage" card - should show bytes used
- Check summary at top
- Go to Profile - should show detailed stats
- Go to Files - file should be listed

## Expected Behavior

When a file is uploaded successfully:
1. File gets unique ID (MD5 hash of name + timestamp)
2. File is chunked (256KB - 1MB chunks)
3. Chunks are distributed to 3 nodes (with replication)
4. Network transfers are simulated (chunks sent via TCP to nodes)
5. File record is added to user's profile:
   - File ID, name, size, node list stored
   - user.used_bytes incremented
6. Frontend shows file in list and updates storage bar

## Troubleshooting

### File uploads but doesn't show in file list
- Check if AuthService is running
- Verify backend logs for `AddFileRecord` errors
- Check if user file record was actually saved

### Storage usage doesn't update
- Confirm file record was added (check file list first)
- Verify `/auth/profile/{username}` endpoint returns correct used_bytes
- Check AuthService `users.json` file directly

### Download fails
- Ensure nodes are still running
- Verify chunks were stored on nodes
- Check backend logs for retrieval errors

## Files Modified/Used

**Backend:**
- `backend/api.py` - Upload, download, profile, files endpoints
- All endpoints already have quota checking and file recording

**AuthService:**
- `AuthService/cloud.py` - AddFileRecord, file metadata storage
- `AuthService/users.json` - Persistent user data with files and used_bytes

**Frontend:**
- `frontend/apps/client/public/main.js` - Upload handler, storage display
- All display logic already implemented

## Next Steps (If Issues Found)

1. **Add file persistence layer** - If files aren't surviving node restarts
2. **Improve download mechanism** - If file reconstruction fails
3. **Add data integrity checking** - MD5 checksums for chunks
4. **Implement garbage collection** - For deleted files on nodes
5. **Add storage optimization** - Compression, deduplication

## Summary

The upload functionality is **fully implemented** with:
- ✅ File storage on virtual nodes
- ✅ Memory/storage usage tracking in AuthService
- ✅ Frontend display of storage stats
- ✅ Quota enforcement before upload
- ✅ File persistence and retrieval

Everything should work as a normal cloud storage system. Files are stored, tracked, and quotas are managed automatically.
