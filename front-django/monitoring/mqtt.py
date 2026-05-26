from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class NodeRedTarget:
    base_url: str


def _node_red_base_url() -> str:
    return getattr(settings, "NODE_RED_BASE_URL", "http://localhost:1880").rstrip("/")


def _target() -> NodeRedTarget:
    return NodeRedTarget(base_url=_node_red_base_url())


def ensure_client_started() -> None:
    # Django does not connect to MQTT directly anymore.
    # The dashboard state is pulled exclusively from Node-RED over HTTP.
    return


def fetch_state() -> dict:
    url = f"{_target().base_url}/state"
    request = Request(url, headers={"Accept": "application/json"})

    try:
        with urlopen(request, timeout=10) as response:
            payload = response.read().decode("utf-8", errors="ignore")
            data = json.loads(payload or "{}")
            if isinstance(data, dict):
                return data
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        LOGGER.warning("Falha ao buscar estado do Node-RED em %s: %s", url, exc)

    return {"success": False, "data": {}}


def publish_command(command: str) -> tuple[bool, str]:
    normalized = str(command).strip().upper()
    if normalized not in {"ON", "OFF", "PING"}:
        return False, "Comando inválido"

    url = f"{_target().base_url}/command"
    body = json.dumps({"command": normalized}).encode("utf-8")
    request = Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )

    try:
        with urlopen(request, timeout=10) as response:
            payload = response.read().decode("utf-8", errors="ignore")
            data = json.loads(payload or "{}")
            if isinstance(data, dict):
                success = bool(data.get("success", response.status < 400))
                message = str(data.get("message", f"Comando {normalized} enviado"))
                return success, message
    except HTTPError as exc:
        try:
            payload = exc.read().decode("utf-8", errors="ignore")
            data = json.loads(payload or "{}")
            message = str(data.get("message", f"Falha ao publicar comando: HTTP {exc.code}"))
        except Exception:
            message = f"Falha ao publicar comando: HTTP {exc.code}"
        LOGGER.warning("Erro HTTP ao enviar comando ao Node-RED em %s: %s", url, exc)
        return False, message
    except (URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        LOGGER.warning("Falha ao enviar comando ao Node-RED em %s: %s", url, exc)
        return False, f"Falha ao publicar comando no Node-RED: {exc}"

    return False, "Resposta inválida do Node-RED"
