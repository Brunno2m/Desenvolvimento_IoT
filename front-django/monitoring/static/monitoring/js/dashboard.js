(function () {
    const snapshot = JSON.parse(document.getElementById("snapshot-data").textContent);
    // Node-RED base URL (ajuste se Node-RED estiver em outro host/porta)
    const NODERED_BASE = "http://localhost:1880";
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
    const history = snapshot.history || [];

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

    function pushEvent(message, tone) {
        const item = document.createElement("li");
        item.className = tone || "";
        item.textContent = message;
        eventsList.prepend(item);
        while (eventsList.children.length > 5) {
            eventsList.lastElementChild.remove();
        }
    }

    function renderState(data) {
        const currentTemperature = Number(data.latest_temperature);
        const isTemperatureAvailable = !Number.isNaN(currentTemperature);

        temperatureNode.textContent = `${formatTemperature(data.latest_temperature)} °C`;
        statusNode.textContent = data.latest_status || "--";
        connectionNode.textContent = data.mqtt_connected ? "Ativo" : "Offline";
        sourceNode.textContent = data.mqtt_source || "Origem MQTT indisponível";
        updatedNode.textContent = formatDate(data.last_updated);
        heroTemperature.textContent = `${formatTemperature(data.latest_temperature)} °C`;
        heroStatus.textContent = data.latest_status || "--";
        heroConnection.textContent = data.mqtt_message || "--";

        fleetCards.forEach((card) => {
            const light = card.querySelector("[data-fleet-light]");
            const label = card.querySelector("[data-fleet-label]");
            const reading = card.querySelector("[data-fleet-temperature]");
            if (!light || !label) {
                return;
            }

            const targetTemperature = Number(card.dataset.targetTemperature);
            const mode = card.dataset.mode;
            const simulatedTemperature = Number(card.dataset.simulatedTemperature);
            const temperatureValue = mode === "live" ? currentTemperature : simulatedTemperature;
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
            label.textContent = mode === "live"
                ? (isTemperatureIdeal ? "Ao vivo / OK" : "Ao vivo / alerta")
                : (isTemperatureIdeal ? "Simulado / OK" : "Simulado / alerta");
            if (reading) {
                reading.textContent = `${formatTemperature(temperatureValue)} °C`;
            }
        });

        if (data.history && data.history.length) {
            chart.data.labels = data.history.map((entry) => formatDate(entry.timestamp));
            chart.data.datasets[0].data = data.history.map((entry) => entry.temperature);
            chart.update("none");
        }

        const latestEvent = data.latest_status
            ? `Status atualizado para ${data.latest_status}`
            : "Aguardando status do Node-RED";
        const tone = statusClass(data.latest_status);
        pushEvent(latestEvent, tone);
    }

    const chart = new Chart(document.getElementById("temperature-chart"), {
        type: "line",
        data: {
            labels: history.map((entry) => formatDate(entry.timestamp)),
            datasets: [{
                label: "Temperatura da câmara",
                data: history.map((entry) => entry.temperature),
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

    async function fetchNodeRed(path, options) {
        try {
            const response = await fetch(`${NODERED_BASE}${path}`, options);
            if (!response.ok) throw new Error('HTTP ' + response.status);
            return await response.json();
        } catch (err) {
            return null;
        }
    }

    async function refreshState() {
        // Prioriza Node-RED
        const nr = await fetchNodeRed('/state');
        if (nr && nr.success) {
            renderState(nr.data);
            return;
        }

        // Fallback para API Django
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
        // Tenta enviar via Node-RED primeiro
        const nr = await fetchNodeRed('/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command }),
        });
        if (nr) {
            pushEvent(nr.message, nr.success ? 'event-status-ok' : 'event-status-error');
            return;
        }

        // Fallback para Django
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
