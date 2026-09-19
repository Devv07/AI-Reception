from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv

from integration.event import IntegrationEvent


load_dotenv()


class BackendIntegrationClient:
    """
    Lightweight HTTP client for the shared AI Reception backend.

    Uses Python's standard library so the integration layer does
    not require another HTTP package.

    Configuration comes from .env:

        SHARED_BACKEND_URL=http://127.0.0.1:8000
        SHARED_BACKEND_EVENT_PATH=/api/integration/events

    Optional:

        SHARED_BACKEND_API_KEY=...
        SHARED_BACKEND_TIMEOUT=10
    """

    def __init__(
        self,
        base_url: str | None = None,
        event_path: str | None = None,
        api_key: str | None = None,
        timeout: float | None = None,
    ) -> None:

        self.base_url = (
            base_url
            or os.getenv(
                "SHARED_BACKEND_URL",
                "http://127.0.0.1:8000",
            )
        ).rstrip("/")

        self.event_path = (
            event_path
            or os.getenv(
                "SHARED_BACKEND_EVENT_PATH",
                "/api/integration/events",
            )
        )

        if not self.event_path.startswith("/"):
            self.event_path = "/" + self.event_path

        self.api_key = (
            api_key
            if api_key is not None
            else os.getenv(
                "SHARED_BACKEND_API_KEY",
                "",
            )
        )

        configured_timeout = os.getenv(
            "SHARED_BACKEND_TIMEOUT",
            "10",
        )

        self.timeout = (
            timeout
            if timeout is not None
            else float(configured_timeout)
        )

    @property
    def event_url(self) -> str:
        return f"{self.base_url}{self.event_path}"

    def send_event(
        self,
        event: IntegrationEvent,
    ) -> dict[str, Any]:

        if not isinstance(event, IntegrationEvent):
            raise TypeError(
                "event must be an IntegrationEvent"
            )

        payload = event.to_dict()

        body = json.dumps(
            payload,
            ensure_ascii=False,
        ).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if self.api_key:
            headers["Authorization"] = (
                f"Bearer {self.api_key}"
            )

        request = Request(
            self.event_url,
            data=body,
            headers=headers,
            method="POST",
        )

        try:
            with urlopen(
                request,
                timeout=self.timeout,
            ) as response:

                raw_response = response.read().decode(
                    "utf-8",
                    errors="replace",
                )

                status_code = response.status

                try:
                    response_data = (
                        json.loads(raw_response)
                        if raw_response
                        else {}
                    )
                except json.JSONDecodeError:
                    response_data = {
                        "raw": raw_response
                    }

                return {
                    "success": True,
                    "status_code": status_code,
                    "response": response_data,
                    "event_id": event.event_id,
                }

        except HTTPError as exc:

            error_body = ""

            try:
                error_body = exc.read().decode(
                    "utf-8",
                    errors="replace",
                )
            except Exception:
                pass

            return {
                "success": False,
                "status_code": exc.code,
                "error": error_body
                or str(exc),
                "event_id": event.event_id,
            }

        except URLError as exc:

            return {
                "success": False,
                "status_code": None,
                "error": str(exc.reason),
                "event_id": event.event_id,
            }

        except Exception as exc:

            return {
                "success": False,
                "status_code": None,
                "error": str(exc),
                "error_type": type(exc).__name__,
                "event_id": event.event_id,
            }