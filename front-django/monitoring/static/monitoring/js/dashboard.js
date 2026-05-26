(function () {
    const snapshot = JSON.parse(document.getElementById("snapshot-data").textContent);
    const eventsList = document.getElementById("events-list");
    const temperatureNode = document.getElementById("metric-temperature");
    const statusNode = document.getElementById("metric-status");
    const connectionNode = document.getElementById("metric-connection");
    const sourceNode = document.getElementById("metric-source");
    const updatedNode = document.getElementById("metric-updated");
    const heroTemperature = document.getElementById("hero-temperature");
    const heroStatus = document.getElementById("hero-status");
    const heroConnection = document.getElementById("hero-connection");
    const fleetCards = Array.from(document.querySelectorAll("[data-fleet-card]"));
    const fleetCharts = new Map();
    const initialFleetUnits = Array.isArray(snapshot.fleet_units) ? snapshot.fleet_units : [];
    let lastEventSignature = "";

    function formatTemperature(value) {
        if (value === null || value === undefined || Number.isNaN(Number(value))) {
            return "--";
        }
        return Number(value).toFixed(1);
    }

    function formatDate(value) {
        if (!value) {
            return "Aguardando dados";
        }
        return new Intl.DateTimeFormat("pt-BR", {
            dateStyle: "short",
            timeStyle: "medium",
        }).format(new Date(value));
    }

    function statusClass(value) {
        const normalized = String(value || "").toUpperCase();
        if (normalized.includes("ALERTA") || normalized.includes("ERRO")) {
            return "event-status-alert";
        }
        if (normalized.includes("NORMAL") || normalized.includes("OK") || normalized.includes("OPER")) {
            return "event-status-ok";
        }
        return "";
    }

    function getUnitHistory(unit) {
        return Array.isArray(unit?.history) ? unit.history : [];
    }

    function getUnitColor(unit) {
        if (unit?.is_live) {
            return "#64d29f";
        }
        return "#8bb4ff";
    }

    function ensureMiniChart(canvas, unit) {
        if (!canvas) {
            return null;
        }

        const history = getUnitHistory(unit);
        const labels = history.map((entry) => formatDate(entry.timestamp));
        const dataset = history.map((entry) => entry.temperature);
        const existing = fleetCharts.get(canvas);

        if (existing) {
            existing.data.labels = labels;
            existing.data.datasets[0].label = unit?.code || unit?.device_id || "Unidade";
            existing.data.datasets[0].data = dataset;
            existing.data.datasets[0].borderColor = getUnitColor(unit);
            existing.data.datasets[0].backgroundColor = `${getUnitColor(unit)}22`;
            existing.update("none");
            return existing;
        }

        const chart = new Chart(canvas, {
            type: "line",
            data: {
                labels,
                datasets: [{
                    label: unit?.code || unit?.device_id || "Unidade",
                    data: dataset,
                    borderColor: getUnitColor(unit),
                    backgroundColor: `${getUnitColor(unit)}22`,
                    tension: 0.35,
                    fill: true,
                    pointRadius: 1.5,
                    pointHoverRadius: 3,
                    borderWidth: 2,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label(context) {
                                return `${context.dataset.label}: ${formatTemperature(context.parsed.y)} °C`;
                            },
                        },
                    },
                },
                scales: {
                    x: {
                        ticks: { display: false },
                        grid: { display: false },
                    },
                    y: {
                        ticks: { color: "#9ab5aa", maxTicksLimit: 3 },
                        grid: { color: "rgba(255,255,255,0.05)" },
                    },
                },
            },
        });

        fleetCharts.set(canvas, chart);
        return chart;
    }

    function pickActiveUnit(data, fleetUnits) {
        const activeId = data.latest_device_id;
        if (activeId) {
            const activeUnit = fleetUnits.find((unit) => unit.device_id === activeId);
            if (activeUnit) {
                return activeUnit;
            }
        }

        return fleetUnits.find((unit) => unit.is_live) || fleetUnits[0] || null;
    }

    function pushEvent(message, tone) {
        const signature = `${tone || ""}|${message || ""}`;
        if (signature === lastEventSignature) {
            return;
        }
        lastEventSignature = signature;
        const item = document.createElement("li");
        item.className = tone || "";
        item.textContent = message;
        eventsList.prepend(item);
        while (eventsList.children.length > 5) {
            eventsList.lastElementChild.remove();
        }
    }

    function renderState(data) {
        const fleetUnits = Array.isArray(data.fleet_units) && data.fleet_units.length ? data.fleet_units : initialFleetUnits;
        const activeUnit = pickActiveUnit(data, fleetUnits);
        const currentTemperature = Number(activeUnit?.latest_temperature ?? data.latest_temperature);
        const isTemperatureAvailable = !Number.isNaN(currentTemperature);

        temperatureNode.textContent = `${formatTemperature(activeUnit?.latest_temperature ?? data.latest_temperature)} °C`;
        statusNode.textContent = activeUnit?.latest_status || data.latest_status || "--";
        connectionNode.textContent = data.mqtt_connected ? "Ativo" : "Offline";
        sourceNode.textContent = activeUnit ? `${activeUnit.code} · ${activeUnit.device_id}` : (data.mqtt_source || "Origem MQTT indisponível");
        updatedNode.textContent = formatDate(data.last_updated);
        heroTemperature.textContent = `${formatTemperature(activeUnit?.latest_temperature ?? data.latest_temperature)} °C`;
        heroStatus.textContent = activeUnit?.latest_status || data.latest_status || "--";
        heroConnection.textContent = data.mqtt_message || "--";

        fleetCards.forEach((card) => {
            const deviceId = card.dataset.deviceId;
            const unit = fleetUnits.find((item) => item.device_id === deviceId) || null;
            const light = card.querySelector("[data-fleet-light]");
            const label = card.querySelector("[data-fleet-label]");
            const reading = card.querySelector("[data-fleet-temperature]");
            const miniChartCanvas = card.querySelector("[data-fleet-chart]");
            if (!light || !label) {
                return;
            }

            const targetTemperature = Number(card.dataset.targetTemperature);
            const mode = card.dataset.mode;
            const simulatedTemperature = Number(card.dataset.simulatedTemperature);
            const temperatureValue = unit?.latest_temperature ?? (mode === "live" ? currentTemperature : simulatedTemperature);
            const temperatureAvailable = !Number.isNaN(temperatureValue);
            const isTemperatureIdeal = temperatureAvailable && !Number.isNaN(targetTemperature) && temperatureValue <= targetTemperature;

            card.classList.toggle("fleet-card-ideal", isTemperatureIdeal);
            card.classList.toggle("fleet-card-alert", temperatureAvailable && !isTemperatureIdeal);

            if (!temperatureAvailable) {
                light.classList.remove("is-green", "is-red");
                label.textContent = "Aguardando";
                if (reading) {
                    reading.textContent = "-- °C";
                }
                return;
            }

            light.classList.toggle("is-green", isTemperatureIdeal);
            light.classList.toggle("is-red", !isTemperatureIdeal);
            label.textContent = unit?.is_live
                ? (isTemperatureIdeal ? "Ao vivo / OK" : "Ao vivo / alerta")
                : (isTemperatureIdeal ? "Simulado / OK" : "Simulado / alerta");
            if (reading) {
                reading.textContent = `${formatTemperature(temperatureValue)} °C`;
            }

            ensureMiniChart(miniChartCanvas, unit || { code: card.querySelector("strong")?.textContent, device_id: deviceId, history: [] });
        });

        const mainHistory = getUnitHistory(activeUnit);
        const chartHistory = mainHistory.length ? mainHistory : (Array.isArray(data.history) ? data.history : []);
        chart.data.labels = chartHistory.map((entry) => formatDate(entry.timestamp));
        chart.data.datasets[0].label = activeUnit?.code || activeUnit?.device_id || "Temperatura da frota";
        chart.data.datasets[0].data = chartHistory.map((entry) => entry.temperature);
        chart.update("none");

        if (activeUnit) {
            const latestEvent = `${activeUnit.code}: ${formatTemperature(activeUnit.latest_temperature)} °C · ${activeUnit.latest_status || "--"}`;
            pushEvent(latestEvent, statusClass(activeUnit.latest_status));
        } else if (data.latest_status) {
            pushEvent(`Status atualizado para ${data.latest_status}`, statusClass(data.latest_status));
        }
    }

    const chart = new Chart(document.getElementById("temperature-chart"), {
        type: "line",
        data: {
            labels: (snapshot.history || []).map((entry) => formatDate(entry.timestamp)),
            datasets: [{
                label: "Temperatura da frota",
                data: (snapshot.history || []).map((entry) => entry.temperature),
                borderColor: "#64d29f",
                backgroundColor: "rgba(100, 210, 159, 0.12)",
                tension: 0.35,
                fill: true,
                pointRadius: 2,
                pointHoverRadius: 4,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            plugins: {
                legend: {
                    labels: {
                        color: "#f3f8f6",
                        font: {
                            family: "Manrope",
                        },
                    },
                },
            },
            scales: {
                x: {
                    ticks: { color: "#9ab5aa" },
                    grid: { color: "rgba(255,255,255,0.05)" },
                },
                y: {
                    ticks: { color: "#9ab5aa" },
                    grid: { color: "rgba(255,255,255,0.05)" },
                },
            },
        },
    });

    renderState(snapshot);

    async function refreshState() {
        try {
            const response = await fetch('/api/state/');
            const payload = await response.json();
            if (payload.success) {
                renderState(payload.data);
                return;
            }
        } catch (error) {
            // ignorar aqui e cair no pushEvent abaixo
        }

        pushEvent('Falha ao consultar o estado remoto.', 'event-status-error');
    }

    async function sendCommand(command) {
        try {
            const response = await fetch('/api/command/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify({ command }),
            });
            const payload = await response.json();
            pushEvent(payload.message, payload.success ? 'event-status-ok' : 'event-status-error');
        } catch (error) {
            pushEvent('Erro ao enviar comando para o broker.', 'event-status-error');
        }
    }

    document.querySelectorAll("[data-command]").forEach((button) => {
        button.addEventListener("click", () => sendCommand(button.dataset.command));
    });

    setInterval(refreshState, 4000);
})();
