import logging
import time

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)


class FootballDataAPIError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class FootballDataClient:
    """Cliente HTTP para football-data.org."""

    def __init__(self):
        self.base_url = settings.FOOTBALL_DATA_API_BASE_URL.rstrip("/")
        self.token = settings.FOOTBALL_DATA_API_TOKEN
        self.timeout = settings.FOOTBALL_DATA_TIMEOUT_SECONDS

    def _headers(self) -> dict[str, str]:
        return {"X-Auth-Token": self.token}

    def get_json(self, path: str, params: dict | None = None) -> dict:
        if not self.token:
            logger.warning("FOOTBALL_DATA_API_TOKEN no está configurado")
            raise FootballDataAPIError(
                "FOOTBALL_DATA_API_TOKEN no está configurado.", status_code=None
            )

        url = f"{self.base_url}{path}"
        start = time.monotonic()
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=self._headers(), params=params)
                response.raise_for_status()
                elapsed_ms = (time.monotonic() - start) * 1000
                logger.info(
                    "football-data.org %s status=%s elapsed_ms=%.0f params=%s",
                    path,
                    response.status_code,
                    elapsed_ms,
                    params,
                )
                return response.json()
        except httpx.HTTPStatusError as exc:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.error(
                "football-data.org %s status=%s elapsed_ms=%.0f params=%s",
                path,
                exc.response.status_code,
                elapsed_ms,
                params,
            )
            raise FootballDataAPIError(
                f"Error HTTP {exc.response.status_code} al consultar {path}",
                status_code=exc.response.status_code,
            ) from exc
        except httpx.RequestError as exc:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.error(
                "football-data.org %s connection error elapsed_ms=%.0f params=%s: %s",
                path,
                elapsed_ms,
                params,
                exc,
            )
            raise FootballDataAPIError(
                f"Error de conexión al consultar {path}: {exc}",
                status_code=None,
            ) from exc
