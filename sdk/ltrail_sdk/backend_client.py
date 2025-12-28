"""HTTP backend client for sending traces to FastAPI backend."""

import json
import threading
from typing import Optional, Dict, Any
from urllib.parse import urljoin

try:
    import requests
    from requests import exceptions as requests_exceptions
except ImportError:
    requests = None
    requests_exceptions = None

from ltrail_sdk.core import LTrail
from ltrail_sdk.exceptions import LTrailError


class BackendClient:
    """Client for sending traces to a FastAPI backend."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        """
        Initialize the backend client.

        Args:
            base_url: Base URL of the FastAPI backend
            api_key: Optional API key for authentication
        """
        if requests is None:
            raise LTrailError(
                "requests library is required for BackendClient. "
                "Install it with: pip install requests"
            )
        
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
        
        self.session.headers.update({"Content-Type": "application/json"})

    def send_trace(self, ltrail_instance: LTrail, async_send: bool = True) -> Optional[Dict[str, Any]]:
        """
        Send a trace to the backend.

        Args:
            ltrail_instance: LTrail instance to send
            async_send: If True, send asynchronously in a background thread

        Returns:
            Response dictionary if sync, None if async
        """
        trace_data = ltrail_instance.export()
        url = urljoin(self.base_url, "/api/traces")

        def _send():
            try:
                response = self.session.post(url, json=trace_data, timeout=5)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                error_type = type(e).__name__
                if 'ConnectionError' in error_type or 'Connection' in str(e):
                    return None  # Backend not running
                elif 'Timeout' in error_type:
                    return None  # Backend timeout
                elif hasattr(e, 'response'):
                    print(f"Warning: Backend returned error: {e.response.status_code} - {e.response.text}")
                    return None
                else:
                    print(f"Warning: Failed to send trace to backend: {e}")
                    return None

        if async_send:
            thread = threading.Thread(target=_send, daemon=True)
            thread.start()
            return None
        else:
            return _send()

    def send_step_update(
        self, 
        trace_id: str, 
        step_data: Dict[str, Any],
        async_send: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Send a step update to the backend (for real-time updates).

        Args:
            trace_id: ID of the trace
            step_data: Step data dictionary
            async_send: If True, send asynchronously in a background thread

        Returns:
            Response dictionary if sync, None if async
        """
        url = urljoin(self.base_url, f"/api/traces/{trace_id}/steps")
        payload = {"trace_id": trace_id, "step": step_data}

        def _send():
            try:
                response = self.session.post(url, json=payload, timeout=5)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.ConnectionError:
                return None  # Backend not running - silently fail for step updates
            except Exception as e:
                # Don't print warnings for step updates to avoid spam
                return None

        if async_send:
            thread = threading.Thread(target=_send, daemon=True)
            thread.start()
            return None
        else:
            return _send()


class BackendStorage:
    """Storage backend that sends traces to FastAPI backend."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        """
        Initialize backend storage.

        Args:
            base_url: Base URL of the FastAPI backend
            api_key: Optional API key for authentication
        """
        self.client = BackendClient(base_url, api_key)

    def save_trace(self, ltrail_instance: LTrail, output_dir: Optional[str] = None) -> str:
        """
        Save a trace by sending it to the backend.

        Args:
            ltrail_instance: LTrail instance to save
            output_dir: Ignored (kept for compatibility)

        Returns:
            Trace ID
        """
        self.client.send_trace(ltrail_instance, async_send=True)
        return ltrail_instance.trace_id

