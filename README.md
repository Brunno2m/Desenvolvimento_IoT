# Desenvolvimento_IoT

## Subir a stack MQTT + Node-RED

```bash
docker compose up -d
```

Isso sobe:
- `mosquitto` na porta `1883`
- `node-red` na porta `1880`

## Acesso

- Node-RED: http://localhost:1880
- Broker MQTT para o Wokwi web: broker.hivemq.com:1883
- Broker MQTT local do Docker: localhost:1883

## Django

Para a interface do Django receber os dados, o Node-RED precisa estar ativo e expondo `http://localhost:1880/state` e `http://localhost:1880/command`. O Django consome esses endpoints e não acessa o broker MQTT diretamente. Se você estiver usando o Wokwi no site, o flow do Node-RED precisa estar apontado para `broker.hivemq.com:1883`, não para o broker local do Docker.


cd /workspaces/Desenvolvimento_IoT/front-django && source .venv/bin/activate

python manage.py runserver