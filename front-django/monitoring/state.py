from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from threading import RLock

from django.utils import timezone


@dataclass
class DashboardState:
    lock: RLock = field(default_factory=RLock, repr=False)
    mqtt_connected: bool = False
    mqtt_message: str = "Aguardando conexão com o broker"
    mqtt_source: str = ""
    latest_temperature: float | None = None
    latest_status: str = "Aguardando dados"
    latest_topic: str = ""
    last_updated: datetime | None = None
    last_command: str = "OFF"
    message_count: int = 0
    history: deque = field(default_factory=lambda: deque(maxlen=60), repr=False)


STATE = DashboardState()


def _serialize_timestamp(value: datetime | None) -> str | None:
    if value is None:
        return None
    return timezone.localtime(value).isoformat()


def _record_history_entry() -> None:
    if STATE.latest_temperature is None:
        return

    STATE.history.append(
        {
            "timestamp": _serialize_timestamp(STATE.last_updated),
            "temperature": STATE.latest_temperature,
            "status": STATE.latest_status,
        }
    )


def set_connection(connected: bool, message: str, source: str = "") -> None:
    with STATE.lock:
        STATE.mqtt_connected = connected
        STATE.mqtt_message = message
        if source:
            STATE.mqtt_source = source


def set_last_command(command: str) -> None:
    with STATE.lock:
        STATE.last_command = command
        STATE.last_updated = timezone.now()


def ingest_message(topic: str, payload: str) -> None:
    with STATE.lock:
        STATE.message_count += 1
        STATE.latest_topic = topic
        STATE.last_updated = timezone.now()

        if topic.endswith("temperatura"):
            try:
                temperature = float(str(payload).replace(",", "."))
                STATE.latest_temperature = temperature
                STATE.latest_status = "ALERTA" if temperature > 8.0 else "NORMAL"
                _record_history_entry()
                return
            except ValueError:
                STATE.latest_status = "Dado inválido"
                return

        elif topic.endswith("status"):
            STATE.latest_status = str(payload).strip().upper() or "SEM STATUS"
            _record_history_entry()
            return

        elif topic.endswith("atuador/estado"):
            STATE.last_command = str(payload).strip().upper() or STATE.last_command
            return


def get_snapshot() -> dict:
    with STATE.lock:
        return {
            "mqtt_connected": STATE.mqtt_connected,
            "mqtt_message": STATE.mqtt_message,
            "mqtt_source": STATE.mqtt_source,
            "latest_temperature": STATE.latest_temperature,
            "latest_status": STATE.latest_status,
            "latest_topic": STATE.latest_topic,
            "last_updated": _serialize_timestamp(STATE.last_updated),
            "last_command": STATE.last_command,
            "message_count": STATE.message_count,
            "history": list(STATE.history),
        }
