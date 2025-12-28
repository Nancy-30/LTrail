# LTrail Backend

FastAPI backend server for LTrail dashboard with WebSocket support for real-time updates.

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### GET `/api/traces`
Get all traces (with pagination)

Query parameters:
- `limit`: Number of traces to return (default: 50)
- `offset`: Offset for pagination (default: 0)

### GET `/api/traces/{trace_id}`
Get a specific trace by ID

### POST `/api/traces`
Create or update a trace

### POST `/api/traces/{trace_id}/steps`
Add or update a step in a trace (for real-time updates)

### WebSocket `/ws/{trace_id}`
Connect to WebSocket for real-time trace updates

## Health Check

### GET `/api/health`
Health check endpoint

