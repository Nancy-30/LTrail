"""FastAPI backend for LTrail dashboard."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from routes import api_router, static

app = FastAPI(title="LTrail Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if os.getenv("ENVIRONMENT") != "production" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes first
app.include_router(api_router)

# Mount static files if they exist
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    # React build has nested static folder: static/static/js/... and static/static/css/...
    # Mount /static to serve from the nested static folder
    static_assets_dir = static_dir / "static"
    if static_assets_dir.exists():
        app.mount(
            "/static", StaticFiles(directory=str(static_assets_dir)), name="static"
        )
    # Include static router last to catch all non-API routes (SPA routing)
    app.include_router(static.router)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
