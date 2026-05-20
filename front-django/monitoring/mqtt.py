from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass

import paho.mqtt.client as mqtt
from django.conf import settings

from .state import ingest_message, set_connection, set_last_command


LOGGER = logging.getLogger(__name__)
_started = False
_start_lock = threading.Lock()


@dataclass(frozen=True)
class BrokerTarget:
    host: str
    port: int


def _parse_brokers() -> list[BrokerTarget]:
    brokers: list[BrokerTarget] = []
    for item in settings.MQTT_BROKERS:
        host, _, port_text = item.partition(":")
        if not host:
            continue
        brokers.append(BrokerTarget(host=host, port=int(port_text or settings.MQTT_PORT)))
    return brokers or [BrokerTarget(host=settings.MQTT_HOST, port=settings.MQTT_PORT)]


def _configure_client(client: mqtt.Client, source_label: str) -> None:
    if settings.MQTT_USERNAME:
        client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

    def on_connect(client, userdata, flags, reason_code, properties=None):
        if int(reason_code) == 0:
            client.subscribe(settings.MQTT_TEMPERATURE_TOPIC, qos=1)
            client.subscribe(settings.MQTT_STATUS_TOPIC, qos=1)
            set_connection(True, f"Conectado em {source_label}", source_label)
            LOGGER.info("MQTT conectado em %s", source_label)
        else:
            set_connection(False, f"Falha na conexão MQTT: {reason_code}", source_label)
            LOGGER.warning("Falha MQTT ao conectar: %s", reason_code)

    def on_disconnect(client, userdata, reason_code, properties=None):
        set_connection(False, f"Broker indisponível ({reason_code})", source_label)
        LOGGER.warning("MQTT desconectado: %s", reason_code)

    def on_message(client, userdata, msg):
        payload = msg.payload.decode("utf-8", errors="ignore")
        ingest_message(msg.topic, payload)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message


def _worker() -> None:
    brokers = _parse_brokers()
    while True:
        for index, broker in enumerate(brokers):
            client = mqtt.Client(
                client_id=f"{settings.MQTT_CLIENT_ID}-{index}",
                protocol=mqtt.MQTTv311,
            )
            source_label = f"{broker.host}:{broker.port}"
            _configure_client(client, source_label)

            try:
                set_connection(False, f"Conectando em {source_label}...", source_label)
                client.connect(broker.host, broker.port, keepalive=60)
                client.loop_forever()
            except Exception as exc:
                LOGGER.exception("Erro MQTT em %s: %s", source_label, exc)
                set_connection(False, f"Erro MQTT em {source_label}: {exc}", source_label)
                time.sleep(5)


def ensure_client_started() -> None:
    global _started
    # Respect setting to allow Node-RED to be the primary MQTT client
    if not getattr(settings, "MQTT_CLIENT_ENABLED", True):
        LOGGER.info("MQTT client disabled via settings; Node-RED is primary broker client")
        return

    with _start_lock:
        if _started:
            return
        thread = threading.Thread(target=_worker, name="mqtt-monitoring", daemon=True)
        thread.start()
        _started = True


def publish_command(command: str) -> tuple[bool, str]:
    normalized = str(command).strip().upper()
    if normalized not in {"ON", "OFF", "PING"}:
        return False, "Comando inválido"

    topic = settings.MQTT_PING_TOPIC if normalized == "PING" else settings.MQTT_COMMAND_TOPIC
    payload = normalized if normalized != "PING" else "PING"
    errors: list[str] = []

    for index, broker in enumerate(_parse_brokers()):
        client = mqtt.Client(client_id=f"{settings.MQTT_CLIENT_ID}-publisher-{index}", protocol=mqtt.MQTTv311)
        if settings.MQTT_USERNAME:
            client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

        try:
            client.connect(broker.host, broker.port, keepalive=30)
            client.publish(topic, payload=payload, qos=1, retain=False)
            client.disconnect()
            set_last_command(normalized)
        except Exception as exc:
            LOGGER.exception("Falha ao publicar comando MQTT em %s:%s", broker.host, broker.port)
            errors.append(f"{broker.host}:{broker.port} -> {exc}")

    if len(errors) == len(_parse_brokers()):
        return False, "Falha ao publicar comando: " + " | ".join(errors)

    return True, f"Comando {normalized} enviado para {topic}"
