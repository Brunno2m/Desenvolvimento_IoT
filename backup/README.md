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
- Broker MQTT: localhost:1883

## Django

Para a interface do Django receber os dados, o broker Mosquitto precisa estar ativo. Se estiver executando o Django fora do Docker, mantenha `MQTT_HOST=localhost` e `MQTT_PORT=1883`.


cd /workspaces/Desenvolvimento_IoT/front-django && source .venv/bin/activate