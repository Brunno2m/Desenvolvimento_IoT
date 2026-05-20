from __future__ import annotations

import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from fleet_front import settings

from .mqtt import ensure_client_started, publish_command
from .state import get_snapshot


FLEET_UNITS = [
    {
        "code": "FR-101",
        "plate": "QRF-1C24",
        "route": "Centro de distribuição -> Supermercados",
        "target_temperature": 8,
        "target_temperature_label": "8°C",
        "status": "Em operação",
        "mode": "live",
        "simulated_temperature": None,
    },
    {
        "code": "FR-204",
        "plate": "QRF-8A19",
        "route": "Planta industrial -> Porto seco",
        "target_temperature": 6,
        "target_temperature_label": "6°C",
        "status": "Em trânsito",
        "mode": "simulated",
        "simulated_temperature": 5.4,
    },
    {
        "code": "FR-312",
        "plate": "QRF-5K77",
        "route": "CD -> Unidade hospitalar",
        "target_temperature": 4,
        "target_temperature_label": "4°C",
        "status": "Em inspeção",
        "mode": "simulated",
        "simulated_temperature": 4.8,
    },
]


def dashboard(request):
    ensure_client_started()
    snapshot = get_snapshot()
    context = {
        "snapshot": snapshot,
        "fleet_units": FLEET_UNITS,
        "mqtt_config": {
            "broker": ", ".join(settings.MQTT_BROKERS),
            "temperature_topic": settings.MQTT_TEMPERATURE_TOPIC,
            "status_topic": settings.MQTT_STATUS_TOPIC,
            "command_topic": settings.MQTT_COMMAND_TOPIC,
        },
    }
    return render(request, "monitoring/dashboard.html", context)


@require_GET
def api_state(request):
    ensure_client_started()
    return JsonResponse({
        "success": True,
        "data": get_snapshot(),
    })


@csrf_exempt
@require_POST
def api_command(request):
    ensure_client_started()
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Corpo JSON inválido"}, status=400)

    command = body.get("command", "")
    ok, message = publish_command(command)
    status_code = 200 if ok else 503
    return JsonResponse({"success": ok, "message": message, "command": str(command).upper()}, status=status_code)
