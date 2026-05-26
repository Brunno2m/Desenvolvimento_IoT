from __future__ import annotations

import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .mqtt import ensure_client_started, fetch_state, publish_command


FLEET_UNITS = [
    {
        "device_id": "truck-01",
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
        "device_id": "truck-02",
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
        "device_id": "truck-03",
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


def _build_dashboard_snapshot() -> dict:
    node_red_response = fetch_state()
    snapshot = node_red_response.get("data", {}) if isinstance(node_red_response, dict) else {}
    fleet_map = snapshot.get("fleet", {})
    fleet_units = []

    for unit in FLEET_UNITS:
        live = fleet_map.get(unit["device_id"], {})
        has_live_data = live.get("message_count", 0) > 0
        latest_temperature = live.get("latest_temperature")
        if latest_temperature is None:
            latest_temperature = unit.get("simulated_temperature")

        fleet_units.append(
            {
                **unit,
                **live,
                "mode": "live" if has_live_data else unit["mode"],
                "is_live": has_live_data,
                "latest_temperature": latest_temperature,
                "latest_status": live.get("latest_status") or ("Aguardando dados" if not has_live_data else unit["status"]),
            }
        )

    snapshot["fleet_units"] = fleet_units
    active_device_id = snapshot.get("latest_device_id")
    if active_device_id:
        active_unit = next((unit for unit in fleet_units if unit["device_id"] == active_device_id), None)
        if active_unit and active_unit.get("history"):
            snapshot["history"] = active_unit["history"]

    return snapshot


def dashboard(request):
    ensure_client_started()
    snapshot = _build_dashboard_snapshot()
    context = {
        "snapshot": snapshot,
        "fleet_units": snapshot.get("fleet_units", FLEET_UNITS),
        "mqtt_config": {
            "broker": "Node-RED /state",
            "temperature_topic": "logistica/frio/#",
            "status_topic": "logistica/frio/#",
            "command_topic": "Node-RED /command",
        },
    }
    return render(request, "monitoring/dashboard.html", context)


@require_GET
def api_state(request):
    ensure_client_started()
    return JsonResponse({
        "success": True,
        "data": _build_dashboard_snapshot(),
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
