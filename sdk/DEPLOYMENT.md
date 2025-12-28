# Deployment Guide

## Overview

LTrail is designed to work with a deployed backend and frontend. Users only need to install the SDK from PyPI - no local setup required!

## Architecture

```
┌─────────────┐
│   User Code │
│  (with SDK) │
└──────┬──────┘
       │
       │ HTTP/WebSocket
       ▼
┌─────────────┐      ┌──────────────┐
│   Backend   │◄────►│   Frontend   │
│  (Render)   │      │   (Vercel)  │
└─────────────┘      └──────────────┘
```

## Deployment Steps

### 1. Deploy Backend (Render)

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `cd backend && pip install -r requirements.txt`
4. Set start command: `cd backend && python main.py`
5. Add environment variables if needed
6. Note the service URL (e.g., `https://ltrail-backend.onrender.com`)

### 2. Deploy Frontend (Vercel)

1. Import your project to Vercel
2. Set root directory to `frontend`
3. Set build command: `npm install && npm run build`
4. Add environment variable:
   - `REACT_APP_API_URL`: Your backend URL (e.g., `https://ltrail-backend.onrender.com`)
5. Deploy
6. Note the deployment URL (e.g., `https://ltrail-dashboard.vercel.app`)

### 3. Update SDK Default URLs

Update the default URLs in `sdk/ltrail_sdk/backend_client.py`:

```python
base_url = os.getenv(
    "LTRAIL_BACKEND_URL",
    "https://ltrail-backend.onrender.com"  # Your Render URL
)
```

And update dashboard URL references to your Vercel URL.

### 4. Publish SDK to PyPI

```bash
cd sdk
python -m build
python -m twine upload dist/*
```

## User Experience

### For End Users

Users simply:

1. **Install the SDK:**
   ```bash
   pip install ltrail-sdk
   ```

2. **Use it in their code:**
   ```python
   from ltrail_sdk import LTrail, BackendClient
   
   # BackendClient automatically uses production backend
   backend_client = BackendClient()
   
   ltrail = LTrail.start_trace(name="My Workflow")
   with ltrail.step("my_step") as step:
       # ... their code ...
       backend_client.send_step_update(ltrail.trace_id, step.to_dict())
   
   ltrail.complete()
   backend_client.send_trace(ltrail)
   ```

3. **View traces in dashboard:**
   - Go to `https://ltrail-dashboard.vercel.app`
   - All traces appear automatically
   - No local setup needed!

### Environment Variables (Optional)

Users can override defaults:

- `LTRAIL_BACKEND_URL`: Custom backend URL (defaults to production)
- `LTRAIL_DASHBOARD_URL`: Custom dashboard URL (for display purposes)

## Local Development

For local development, users can still use local backend:

```python
from ltrail_sdk import BackendClient

# Use local backend
backend_client = BackendClient(base_url="http://localhost:8000")
```

Or set environment variable:

```bash
export LTRAIL_BACKEND_URL="http://localhost:8000"
```

## Backend Configuration

The backend should be configured to:

1. **Accept CORS from frontend domain:**
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://ltrail-dashboard.vercel.app"],
       # ...
   )
   ```

2. **Use persistent storage** (not in-memory):
   - Consider using a database (PostgreSQL, MongoDB, etc.)
   - Or file-based storage that persists across restarts

3. **Handle WebSocket connections** from frontend domain

## Frontend Configuration

The frontend should:

1. **Point to production backend:**
   - Update API calls to use `REACT_APP_API_URL`
   - Update WebSocket connections to use backend URL

2. **Handle production URLs:**
   - WebSocket: `wss://ltrail-backend.onrender.com/ws/{trace_id}`
   - API: `https://ltrail-backend.onrender.com/api/traces`

## Security Considerations

1. **API Keys (Optional):**
   - Backend can require API keys for authentication
   - Users pass API key to `BackendClient(api_key="...")`

2. **Rate Limiting:**
   - Backend should implement rate limiting
   - Prevent abuse of the service

3. **Data Privacy:**
   - Consider data retention policies
   - Allow users to delete their traces

## Monitoring

- Monitor backend health on Render dashboard
- Monitor frontend deployments on Vercel
- Set up alerts for backend downtime
- Track SDK usage via PyPI download stats

