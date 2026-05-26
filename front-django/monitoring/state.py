from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from threading import RLock

from django.utils import timezone


def _empty_history() -> deque:
    return deque(maxlen=60)


@dataclass
class FleetTelemetry:
    latest_temperature: float | None = None
    latest_status: str = "Aguardando dados"
    latest_topic: str = ""
    last_updated: datetime | None = None
    last_command: str = "OFF"
    message_count: int = 0
    history: deque = field(default_factory=_empty_history, repr=False)


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
    latest_device_id: str = ""
    history: deque = field(default_factory=_empty_history, repr=False)
    fleet: dict[str, FleetTelemetry] = field(default_factory=dict, repr=False)


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


def _normalize_topic(topic: str) -> tuple[str, str]:
    parts = [part for part in str(topic).strip("/").split("/") if part]
    if len(parts) >= 4 and parts[0] == "logistica" and parts[1] == "frio":
        return parts[2], "/".join(parts[3:])

    if parts == ["logistica", "frio", "temperatura"]:
        return "truck-01", "temperatura"

    if parts == ["logistica", "frio", "status"]:
        return "truck-01", "status"

    if parts == ["logistica", "frio", "comando"]:
        return "truck-01", "comando"

    if parts == ["logistica", "frio", "atuador", "estado"]:
        return "truck-01", "atuador/estado"

    return "truck-01", parts[-1] if parts else ""


def _get_fleet_telemetry(device_id: str) -> FleetTelemetry:
    telemetry = STATE.fleet.get(device_id)
    if telemetry is None:
        telemetry = FleetTelemetry()
        STATE.fleet[device_id] = telemetry
    return telemetry


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
        device_id, kind = _normalize_topic(topic)
        telemetry = _get_fleet_telemetry(device_id)

        STATE.message_count += 1
        STATE.latest_topic = topic
        STATE.latest_device_id = device_id
        STATE.last_updated = timezone.now()

        telemetry.message_count += 1
        telemetry.latest_topic = topic
        telemetry.last_updated = STATE.last_updated

        if kind.endswith("temperatura"):
            try:
                temperature = float(str(payload).replace(",", "."))
                telemetry.latest_temperature = temperature
                telemetry.latest_status = "ALERTA" if temperature > 8.0 else "NORMAL"
                telemetry.history.append(
                    {
                        "timestamp": _serialize_timestamp(STATE.last_updated),
                        "temperature": telemetry.latest_temperature,
                        "status": telemetry.latest_status,
                    }
                )
                STATE.latest_temperature = temperature
                STATE.latest_status = telemetry.latest_status
                _record_history_entry()
                return
            except ValueError:
                telemetry.latest_status = "Dado inválido"
                STATE.latest_status = "Dado inválido"
                return

        elif kind.endswith("status"):
            status = str(payload).strip().upper() or "SEM STATUS"
            telemetry.latest_status = status
            STATE.latest_status = status
            STATE.latest_temperature = telemetry.latest_temperature
            _record_history_entry()
            return

        elif kind.endswith("comando") or kind.endswith("atuador/estado"):
            command = str(payload).strip().upper() or STATE.last_command
            telemetry.last_command = command
            STATE.last_command = command
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
            "latest_device_id": STATE.latest_device_id,
            "last_updated": _serialize_timestamp(STATE.last_updated),
            "last_command": STATE.last_command,
            "message_count": STATE.message_count,
            "history": list(STATE.history),
            "fleet": {
                device_id: {
                    "latest_temperature": telemetry.latest_temperature,
                    "latest_status": telemetry.latest_status,
                    "latest_topic": telemetry.latest_topic,
                    "last_updated": _serialize_timestamp(telemetry.last_updated),
                    "last_command": telemetry.last_command,
                    "message_count": telemetry.message_count,
                    "history": list(telemetry.history),
                }
                for device_id, telemetry in STATE.fleet.items()
            },
        }
