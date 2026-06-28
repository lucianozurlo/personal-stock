import os
import requests
from typing import Any, Dict, Optional


class N8nClientError(Exception):
    pass


class N8nConnectionError(N8nClientError):
    pass


class N8nTimeoutError(N8nClientError):
    pass


class N8nInvalidResponseError(N8nClientError):
    pass


class N8nClient:
    TIMEOUT = 30

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.environ.get('N8N_WEBHOOK_URL')
        if not self.webhook_url:
            raise ValueError('N8N_WEBHOOK_URL not configured')

    def send(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=self.TIMEOUT,
            )

            if response.status_code != 200:
                raise N8nConnectionError(
                    f"n8n returned HTTP {response.status_code}: {response.text}"
                )

            if not response.content:
                raise N8nInvalidResponseError(
                    "n8n responded 200 but with empty body"
                )

            try:
                return response.json()
            except ValueError as e:
                raise N8nInvalidResponseError(
                    f"Response is not valid JSON: {response.text[:200]}"
                ) from e

        except requests.Timeout as e:
            raise N8nTimeoutError(
                f"Request to n8n timed out after {self.TIMEOUT}s"
            ) from e
        except requests.ConnectionError as e:
            raise N8nConnectionError(
                f"Could not connect to n8n at {self.webhook_url}"
            ) from e
