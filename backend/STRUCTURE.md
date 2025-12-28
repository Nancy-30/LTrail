# Backend Structure

This document describes the refactored backend structure with proper separation of concerns.

## Directory Structure

```
backend/
├── main.py                 # FastAPI app initialization
├── dependencies.py         # Shared service instances
├── routes/                # Route handlers
│   ├── __init__.py        # Main router that includes all routes
│   ├── traces.py          # Trace CRUD endpoints
│   ├── websocket.py       # WebSocket endpoints
│   ├── health.py          # Health check endpoint
│   └── static.py         # Static file serving
├── schemas/               # Pydantic models
│   ├── __init__.py        # Schema exports
│   └── trace.py           # Trace-related schemas
└── services/              # Business logic
    ├── __init__.py        # Service exports
    ├── storage.py         # Storage service
    └── websocket_manager.py  # WebSocket manager
```

## Components

### 1. Schemas (`schemas/`)

Pydantic models for request/response validation:

- **TraceData**: Input model for creating traces
- **TraceResponse**: Output model for trace data
- **StepUpdate**: Input model for step updates
- **TraceListResponse**: Response model for trace list
- **HealthResponse**: Response model for health check
- **TraceCreateResponse**: Response model for trace creation
- **StepUpdateResponse**: Response model for step updates

### 2. Services (`services/`)

Business logic and data management:

- **StorageService**: Manages in-memory storage of traces and steps
- **WebSocketManager**: Manages WebSocket connections and broadcasting

### 3. Routes (`routes/`)

API endpoint handlers:

- **traces.py**: 
  - `GET /api/traces` - List all traces
  - `GET /api/traces/{trace_id}` - Get specific trace
  - `POST /api/traces` - Create trace
  - `POST /api/traces/{trace_id}/steps` - Add/update step

- **websocket.py**:
  - `WS /ws/{trace_id}` - WebSocket connection for real-time updates

- **health.py**:
  - `GET /api/health` - Health check endpoint

- **static.py**:
  - `GET /` - Root endpoint
  - `GET /{full_path:path}` - Serve React SPA

### 4. Dependencies (`dependencies.py`)

Shared service instances and dependency injection functions.

### 5. Main (`main.py`)

FastAPI app initialization:
- CORS middleware setup
- Route registration
- Static file mounting

## Usage

The main router is imported in `main.py`:

```python
from routes import api_router
app.include_router(api_router)
```

All routes are automatically included via `routes/__init__.py`.

## Benefits

1. **Separation of Concerns**: Each component has a single responsibility
2. **Maintainability**: Easy to find and modify specific functionality
3. **Testability**: Services and routes can be tested independently
4. **Scalability**: Easy to add new routes or services
5. **Type Safety**: Pydantic schemas provide validation and type hints

