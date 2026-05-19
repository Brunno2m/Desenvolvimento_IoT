# Arquitetura Técnica - Front-end Django + MQTT

## 📐 Diagrama de Arquitetura Completa

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CAMADA DE APRESENTAÇÃO                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  Browser (Cliente)                                                   │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │ Dashboard HTML + Chart.js                                    │  │   │
│  │  │ ┌──────────────┬──────────────┬──────────────────────────┐   │  │   │
│  │  │ │ Hero Panel   │ Metrics Grid │ Temperature Chart       │   │  │   │
│  │  │ │ Conexão      │ - Temp       │ - Histórico 60 pontos   │   │  │   │
│  │  │ │ Status       │ - Status     │ - Atualiza em tempo real│   │  │   │
│  │  │ │              │ - Conexão    │                         │   │  │   │
│  │  │ │              │ - Updated    │                         │   │  │   │
│  │  │ └──────────────┴──────────────┴──────────────────────────┘   │  │   │
│  │  │ ┌──────────────────────────────────────────────────────────┐  │  │   │
│  │  │ │ Botões de Comando                                        │  │  │   │
│  │  │ │ [Ligar] [Desligar] [Ping]                               │  │  │   │
│  │  │ └──────────────────────────────────────────────────────────┘  │  │   │
│  │  │ ┌──────────────────────────────────────────────────────────┐  │  │   │
│  │  │ │ Frota Frigorificada (Fleet Cards)                        │  │  │   │
│  │  │ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │  │  │   │
│  │  │ │ │ FR-101      │ │ FR-204      │ │ FR-312      │         │  │  │   │
│  │  │ │ │ QRF-1C24    │ │ QRF-8A19    │ │ QRF-5K77    │         │  │  │   │
│  │  │ │ │ Live/OK ✓   │ │ Simulado/OK │ │ Simulado/⚠  │         │  │  │   │
│  │  │ │ │ 7.2°C       │ │ 5.4°C       │ │ 4.8°C       │         │  │  │   │
│  │  │ │ └─────────────┘ └─────────────┘ └─────────────┘         │  │  │   │
│  │  │ └──────────────────────────────────────────────────────────┘  │  │   │
│  │  └──────────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  JavaScript (dashboard.js)                                                 │
│  ├─ setInterval(refreshState, 4000) ← Polling a cada 4 segundos           │
│  ├─ fetch(/api/state/) ← GET dados atualizados                            │
│  ├─ fetch(/api/command/) ← POST comandos                                  │
│  ├─ Chart.update() ← Renderiza gráfico                                    │
│  └─ DOM manipulation ← Atualiza cards visuais                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ HTTP/HTTPS
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CAMADA DE APLICAÇÃO                                 │
│ ┌──────────────────────────────────────────────────────────────────────┐    │
│ │ Django Application (Port 8000)                                       │    │
│ │ ┌────────────────────────────────────────────────────────────────┐  │    │
│ │ │ URLs & Routing (urls.py)                                       │  │    │
│ │ │ ┌──────────────┬──────────────┬──────────────────────────────┐ │  │    │
│ │ │ │ GET  /       │ GET  /api/   │ POST /api/command/          │ │  │    │
│ │ │ │      (views) │      state/  │ (CSRF exempt)               │ │  │    │
│ │ │ │              │              │                             │ │  │    │
│ │ │ │ dashboard()  │ api_state()  │ api_command()               │ │  │    │
│ │ │ └──────────────┴──────────────┴──────────────────────────────┘ │  │    │
│ │ │                                                                │  │    │
│ │ │ Views (views.py)                                             │  │    │
│ │ │ ┌────────────────────────────────────────────────────────────┐ │  │    │
│ │ │ │ dashboard(request):                                        │ │  │    │
│ │ │ │   - ensure_client_started()                               │ │  │    │
│ │ │ │   - get_snapshot()                                        │ │  │    │
│ │ │ │   - render template com contexto                         │ │  │    │
│ │ │ │                                                            │ │  │    │
│ │ │ │ api_state(request):                                       │ │  │    │
│ │ │ │   - return JsonResponse(get_snapshot())                  │ │  │    │
│ │ │ │                                                            │ │  │    │
│ │ │ │ api_command(request):                                     │ │  │    │
│ │ │ │   - parse JSON body                                      │ │  │    │
│ │ │ │   - publish_command(command)                             │ │  │    │
│ │ │ │   - return resultado                                      │ │  │    │
│ │ │ └────────────────────────────────────────────────────────────┘ │  │    │
│ │ │                                                                │  │    │
│ │ │ State Management (state.py)                                  │  │    │
│ │ │ ┌────────────────────────────────────────────────────────────┐ │  │    │
│ │ │ │ DashboardState (Dataclass)                                │ │  │    │
│ │ │ │ ├─ mqtt_connected: bool                                   │ │  │    │
│ │ │ │ ├─ mqtt_message: str                                      │ │  │    │
│ │ │ │ ├─ latest_temperature: float | None                       │ │  │    │
│ │ │ │ ├─ latest_status: str                                     │ │  │    │
│ │ │ │ ├─ last_command: str                                      │ │  │    │
│ │ │ │ ├─ message_count: int                                     │ │  │    │
│ │ │ │ ├─ history: deque (maxlen=60)                             │ │  │    │
│ │ │ │ └─ lock: RLock (thread-safe)                              │ │  │    │
│ │ │ │                                                            │ │  │    │
│ │ │ │ set_connection(connected, message, source)                │ │  │    │
│ │ │ │ set_last_command(command)                                 │ │  │    │
│ │ │ │ ingest_message(topic, payload) ← Processa mensagens      │ │  │    │
│ │ │ │ get_snapshot() ← Retorna estado thread-safe              │ │  │    │
│ │ │ └────────────────────────────────────────────────────────────┘ │  │    │
│ │ │                                                                │  │    │
│ │ │ MQTT Client Management (mqtt.py)                             │  │    │
│ │ │ ┌────────────────────────────────────────────────────────────┐ │  │    │
│ │ │ │ ensure_client_started()                                   │ │  │    │
│ │ │ │   └─ _worker() [Thread Daemon]                            │ │  │    │
│ │ │ │      ├─ _parse_brokers() → List[BrokerTarget]             │ │  │    │
│ │ │ │      ├─ for cada broker:                                  │ │  │    │
│ │ │ │      │  ├─ mqtt.Client(mqtt.MQTTv311)                    │ │  │    │
│ │ │ │      │  ├─ _configure_client()                           │ │  │    │
│ │ │ │      │  │  ├─ on_connect → subscribe + set_connection   │ │  │    │
│ │ │ │      │  │  ├─ on_disconnect → set_connection(False)      │ │  │    │
│ │ │ │      │  │  └─ on_message → ingest_message()              │ │  │    │
│ │ │ │      │  ├─ client.connect(host, port, keepalive=60)      │ │  │    │
│ │ │ │      │  └─ client.loop_forever()                         │ │  │    │
│ │ │ │      └─ sleep(5) + retry se erro                         │ │  │    │
│ │ │ │                                                            │ │  │    │
│ │ │ │ publish_command(command) → (bool, str)                    │ │  │    │
│ │ │ │   ├─ valida comando (ON|OFF|PING)                         │ │  │    │
│ │ │ │   ├─ para cada broker:                                    │ │  │    │
│ │ │ │   │  ├─ mqtt.Client() [temporário]                       │ │  │    │
│ │ │ │   │  ├─ client.connect()                                 │ │  │    │
│ │ │ │   │  ├─ client.publish(topic, payload, qos=1)            │ │  │    │
│ │ │ │   │  └─ client.disconnect()                              │ │  │    │
│ │ │ │   └─ set_last_command()                                  │ │  │    │
│ │ │ │                                                            │ │  │    │
│ │ │ │ Subscribed Topics:                                        │ │  │    │
│ │ │ │   ├─ logistica/frio/temperatura (QoS=1)                   │ │  │    │
│ │ │ │   └─ logistica/frio/status (QoS=1)                        │ │  │    │
│ │ │ │                                                            │ │  │    │
│ │ │ │ Published Topics:                                         │ │  │    │
│ │ │ │   └─ logistica/frio/comando (QoS=1, retain=False)         │ │  │    │
│ │ │ └────────────────────────────────────────────────────────────┘ │  │    │
│ │ └────────────────────────────────────────────────────────────────┘  │    │
│ └──────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ paho-mqtt (TCP/IP)
                                  │ (cliente subscriber/publisher)
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CAMADA MQTT                                         │
│ ┌──────────────────────────────────────────────────────────────────────┐    │
│ │ MQTT Brokers (High Availability)                                    │    │
│ │ ┌───────────────────────────────┐  ┌──────────────────────────────┐ │    │
│ │ │ Primary Broker                │  │ Secondary Broker (Fallback)  │ │    │
│ │ │ localhost:1883 (ou config)     │  │ broker.hivemq.com:1883       │ │    │
│ │ │                               │  │                              │ │    │
│ │ │ Topics:                       │  │ Topics Sincronizados         │ │    │
│ │ │ ├─ logistica/frio/+           │  │ ├─ logistica/frio/+          │ │    │
│ │ │ │  ├─ temperatura (#PAYLOAD)  │  │ │  ├─ temperatura            │ │    │
│ │ │ │  ├─ status                  │  │ │  ├─ status                 │ │    │
│ │ │ │  ├─ comando ◄─────────────  │  │ │  └─ comando                │ │    │
│ │ │ │  └─ atuador/estado          │  │ │                            │ │    │
│ │ │ └─                             │  │                              │ │    │
│ │ │                               │  │                              │ │    │
│ │ │ Clientes Conectados:          │  │                              │ │    │
│ │ │ • django-fleet-dashboard-0    │  │                              │ │    │
│ │ │ • django-fleet-dashboard-1    │  │                              │ │    │
│ │ │ • node-red-dashboard ◄───┐    │  │                              │ │    │
│ │ │ • sensor-simulated        │    │  │                              │ │    │
│ │ └───────────────────────────┼────┘  └──────────────────────────────┘ │    │
│ └────────────────────────────┼─────────────────────────────────────────┘    │
│                              │                                              │
│                              ├─ (pub/sub)                                    │
│                              ▼                                              │
│ ┌──────────────────────────────────────────────────────────────────────┐    │
│ │ Topic Namespace: logistica/frio/                                    │    │
│ │                                                                      │    │
│ │ Produtor: Node-RED (Publisher)                                     │    │
│ │ Consumidor: Django (Subscriber)                                    │    │
│ │ Controlador: Django (Publisher)                                    │    │
│ └──────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                ▼                 ▼                 ▼
        ┌──────────────┐  ┌──────────────┐  ┌────────────────┐
        │ Node-RED     │  │ Sensor/      │  │ Relay/         │
        │ Dashboard    │  │ Simulador    │  │ Atuador        │
        │              │  │              │  │                │
        │ (opcional)   │  │ Publica      │  │ Subscreve      │
        │              │  │ temperatura/ │  │ comando        │
        │ Subscreve:   │  │ status       │  │ Controla       │
        │ • temperatura│  │              │  │ refrigeração   │
        │ • status     │  │              │  │                │
        │ • comando    │  │              │  │                │
        │              │  │              │  │                │
        │ Publica:     │  │              │  │                │
        │ • status     │  │              │  │                │
        │ • evento     │  │              │  │                │
        └──────────────┘  └──────────────┘  └────────────────┘
```

---

## 🔄 Fluxos de Dados Detalhados

### Fluxo 1: Recepção de Temperatura (Node-RED → Django → Frontend)

```
Sensor/Simulador publica em "logistica/frio/temperatura"
        │
        ▼
    MQTT Broker
        │
        ▼
Django MQTT Client (thread subscriber)
    on_message(client, userdata, msg)
        │
        ├─ topic: "logistica/frio/temperatura"
        ├─ payload: "7.2"
        │
        ▼
    ingest_message("logistica/frio/temperatura", "7.2")
        │
        ├─ STATE.lock.acquire() [thread-safe]
        │
        ├─ float("7.2") = 7.2
        │
        ├─ 7.2 > 8.0? → False
        │  STATE.latest_status = "NORMAL"
        │
        ├─ STATE.latest_temperature = 7.2
        │
        ├─ _record_history_entry() 
        │  STATE.history.append({
        │    "timestamp": "2026-05-19T14:30:45...",
        │    "temperature": 7.2,
        │    "status": "NORMAL"
        │  })
        │
        └─ STATE.lock.release()
        
                 │
                 ▼ (4 segundos depois)
         
    Browser fetch("/api/state/")
        │
        ▼
    Django GET /api/state/
        │
        ├─ ensure_client_started() [idempotente]
        │
        ├─ get_snapshot()
        │  └─ retorna cópia thread-safe do STATE
        │
        ▼
    JsonResponse com estado completo
        │
        ▼
    JavaScript dashboard.js recebe JSON
        │
        ├─ renderState(payload.data)
        │  │
        │  ├─ document.getElementById("hero-temperature").textContent = "7.2 °C"
        │  │
        │  ├─ document.getElementById("metric-status").textContent = "NORMAL"
        │  │
        │  ├─ chart.data.datasets[0].data = [7.1, 7.15, 7.2, ...]
        │  │
        │  └─ chart.update("none") [sem animação]
        │
        ▼
    DOM atualizado
        │
        ▼
    Usuário vê "Temperatura: 7.2°C, Status: NORMAL"
```

### Fluxo 2: Envio de Comando (Frontend → Django → Node-RED → Atuador)

```
Usuário clica botão "Ligar refrigeração" [data-command="ON"]
        │
        ▼
    JavaScript button.addEventListener("click")
        │
        ├─ sendCommand("ON")
        │
        └─ fetch("/api/command/", {
            method: "POST",
            body: { "command": "ON" }
          })
        
                 │
                 ▼
        
    Django POST /api/command/
        │
        ├─ parse JSON: { "command": "ON" }
        │
        ├─ publish_command("ON")
        │  │
        │  ├─ normalize: "ON".upper() = "ON"
        │  │
        │  ├─ validate: "ON" in {"ON", "OFF", "PING"}? → True
        │  │
        │  ├─ topic = "logistica/frio/comando"
        │  │
        │  ├─ payload = "ON"
        │  │
        │  ├─ Para cada broker:
        │  │  ├─ mqtt.Client() [novo cliente temporário]
        │  │  │
        │  │  ├─ client.connect(broker.host, broker.port)
        │  │  │
        │  │  ├─ client.publish(
        │  │  │    topic="logistica/frio/comando",
        │  │  │    payload="ON",
        │  │  │    qos=1,
        │  │  │    retain=False
        │  │  │  )
        │  │  │
        │  │  ├─ set_last_command("ON")
        │  │  │  └─ STATE.last_command = "ON"
        │  │  │
        │  │  └─ client.disconnect()
        │  │
        │  └─ return (True, "Comando ON enviado para logistica/frio/comando")
        │
        ├─ JsonResponse({"success": True, "message": "...", "command": "ON"})
        │
        └─ pushEvent("Comando ON enviado para logistica/frio/comando", "event-status-ok")
        
                 │
                 ▼
        
    MQTT Broker recebe publicação
        │
        ├─ Subscritos a "logistica/frio/comando":
        │  ├─ Node-RED (dashboard)
        │  └─ Controladores/Atuadores
        │
        └─ Entrega mensagem [QoS=1]
        
                 │
                 ▼
        
    Node-RED recebe mensagem
        │
        ├─ Node de input MQTT
        │
        ├─ Processa: payload = "ON"
        │
        └─ Ativa função: ligar refrigeração
        
                 │
                 ▼
        
    Relé/GPIO ativa
        │
        └─ Refrigeração LIGADA ✓
        
                 │
                 ▼ (opcional: enviar confirmação)
        
    Node-RED publica em "logistica/frio/atuador/estado"
        │
        ├─ payload: "ATIVO" ou "ON"
        │
        └─ Django subscreve e atualiza STATE.last_command
```

---

## 🏗️ Arquitetura de Thread-Safety

```
┌────────────────────────────────────────────────┐
│ Django Main Thread (Request Handling)          │
│ ┌──────────────────────────────────────────┐   │
│ │ request handler                          │   │
│ │ ├─ views.py: GET /api/state/            │   │
│ │ │  └─ get_snapshot() [acquires lock]     │   │
│ │ │     └─ cria cópia do STATE             │   │
│ │ │        └─ release lock                 │   │
│ │ │           → retorna JSON               │   │
│ │ │                                         │   │
│ │ │  POST /api/command/                    │   │
│ │ │  └─ publish_command()                  │   │
│ │ │     └─ set_last_command() [lock]       │   │
│ │ │        → retorna resultado             │   │
│ │ └                                         │   │
│ └──────────────────────────────────────────┘   │
│              ▲                                  │
│              │ HTTP requests                   │
└──────────────┼──────────────────────────────────┘
               │
               │
┌──────────────┼──────────────────────────────────┐
│ MQTT Background Thread (Daemon)                │
│ ┌──────────────────────────────────────────┐   │
│ │ _worker()                                │   │
│ │ ├─ while True:                           │   │
│ │ │  ├─ for cada broker:                   │   │
│ │ │  │  ├─ mqtt.Client()                   │   │
│ │ │  │  ├─ on_connect:                     │   │
│ │ │  │  │  ├─ subscribe()                  │   │
│ │ │  │  │  └─ set_connection() [lock]      │   │
│ │ │  │  │     STATE.mqtt_connected = True  │   │
│ │ │  │  │                                   │   │
│ │ │  │  ├─ on_disconnect:                  │   │
│ │ │  │  │  └─ set_connection() [lock]      │   │
│ │ │  │  │     STATE.mqtt_connected = False │   │
│ │ │  │  │                                   │   │
│ │ │  │  ├─ on_message:                     │   │
│ │ │  │  │  └─ ingest_message() [lock]      │   │
│ │ │  │  │     ├─ parse payload             │   │
│ │ │  │  │     ├─ atualizar STATE           │   │
│ │ │  │  │     └─ record history            │   │
│ │ │  │  │                                   │   │
│ │ │  │  ├─ client.loop_forever() ◄─────┐  │   │
│ │ │  │  │  [blocking]                  │  │   │
│ │ │  │  └─────────────────────────────────┤  │   │
│ │ │  │                                     │  │   │
│ │ │  └─ sleep(5) + retry                 │  │   │
│ │ │                                        │  │   │
│ │ └────────────────────────────────────────┘  │   │
│                                                │   │
│ STATE (Compartilhado com main thread)          │   │
│ ┌──────────────────────────────────────────┐   │   │
│ │ DashboardState                           │   │   │
│ │ ├─ lock: RLock() [mutual exclusion]      │   │   │
│ │ ├─ mqtt_connected: bool                  │   │   │
│ │ ├─ latest_temperature: float             │   │   │
│ │ ├─ latest_status: str                    │   │   │
│ │ ├─ history: deque (maxlen=60)            │   │   │
│ │ └─ ... mais campos ...                   │   │   │
│ │                                          │   │   │
│ │ Acesso sincronizado:                     │   │   │
│ │ • main thread: reads (get_snapshot)      │   │   │
│ │ • mqtt thread: writes (ingest_message) │   │   │
│ │ • ambas: set_connection/set_last_cmd  │   │   │
│ └──────────────────────────────────────────┘   │   │
└───────────────────────────────────────────────────┘

Garantias de Thread-Safety:
✓ RLock (Reentrant Lock) protege todas as mudanças de estado
✓ Operações são atomicamente protegidas
✓ get_snapshot() retorna cópia (não referência) do estado
✓ Sem deadlock possível (operações rápidas, sempre liberam lock)
```

---

## 📊 Fluxo de Dados do Histórico

```
Recebimento 1: temp=7.0 @ 14:30:40
    STATE.history = deque(
        {"timestamp": "14:30:40", "temperature": 7.0, "status": "NORMAL"}
    )

Recebimento 2: temp=7.1 @ 14:30:45
    STATE.history = deque(
        {"timestamp": "14:30:40", "temperature": 7.0, "status": "NORMAL"},
        {"timestamp": "14:30:45", "temperature": 7.1, "status": "NORMAL"}
    )

... (58 mais recebimentos) ...

Recebimento 60: temp=8.5 @ 15:10:30
    STATE.history = deque(maxlen=60) [CHEIO, remove mais antigo]
        # 59 últimas entradas + nova entrada
        ...
        {"timestamp": "15:10:30", "temperature": 8.5, "status": "ALERTA"}
    )

get_snapshot() chamado:
    retorna:
    {
        "history": [
            {"timestamp": "14:30:45", "temperature": 7.1, "status": "NORMAL"},
            ...
            {"timestamp": "15:10:30", "temperature": 8.5, "status": "ALERTA"}
        ]
    }

Frontend recebe:
    chart.data.labels = [formatDate("14:30:45"), ..., formatDate("15:10:30")]
    chart.data.datasets[0].data = [7.1, ..., 8.5]
    chart.update("none")

Resultado Visual:
    ┌─────────────────────────────────────────┐
    │ Evolução da Temperatura                 │
    │                                         │
    │  9.0 ┤              ╱╲                  │
    │  8.5 ┤            ╱  ╲                 │
    │  8.0 ┤          ╱────  ╲               │
    │  7.5 ┤        ╱          ╲             │
    │  7.0 ┤──────╱              ╲           │
    │      ├────────────────────────────────┤
    │     14:30  14:40  14:50  15:00  15:10│
    └─────────────────────────────────────────┘
```

---

## 🔐 Segurança - Fluxo de Autenticação (Proposto)

```
Usuário tenta enviar comando sem token:
    fetch("/api/command/", {
        method: "POST",
        body: {"command": "ON"}
    })
        │
        ▼
    Django verifica Authorization header
        │
        └─ Não encontrado ❌
        
                 │
                 ▼
        
    JsonResponse({"success": false, "message": "Token necessário"}, status=401)


Usuário obtém token primeiro:
    fetch("/api/token/", {
        method: "POST",
        body: {"username": "admin", "password": "123"}
    })
        │
        ▼
    TokenObtainPairView
        │
        ├─ valida credenciais
        │
        └─ retorna {"access": "eyJ...", "refresh": "eyJ..."}


Usuário envia comando com token:
    fetch("/api/command/", {
        method: "POST",
        headers: {
            "Authorization": "Bearer eyJ...",
            "Content-Type": "application/json"
        },
        body: {"command": "ON"}
    })
        │
        ▼
    Django verifica JWT
        │
        ├─ JWTAuthentication.authenticate()
        │  ├─ extrai token do header
        │  ├─ valida assinatura
        │  ├─ verifica expiração
        │  └─ retorna (user, validated_token)
        │
        ├─ IsAuthenticated.has_permission()
        │  └─ user != AnonymousUser? → True ✓
        │
        ▼
    publish_command("ON")
        │
        └─ sucesso ✓
```

---

**Esta arquitetura garante**:
- ✅ Recepção de dados MQTT confiável
- ✅ Envio de comandos seguro
- ✅ Sincronização em tempo real (4s polling)
- ✅ Thread-safety completo
- ✅ Fallback entre múltiplos brokers
- ✅ Histórico persistente em memória (60 pontos)
- ✅ UI responsiva e intuitiva
