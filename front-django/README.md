# Front Django - Frota Frigorificada

Aplicação Django para visualizar, em tempo real, a temperatura da câmara frigorífica e o status recebido pelo Node-RED via MQTT.

## O que a aplicação faz

- Escuta os tópicos MQTT `logistica/frio/temperatura` e `logistica/frio/status`.
- Exibe uma dashboard visual com temperatura atual, status operacional, conexão MQTT e histórico.
- Permite enviar comandos `ON`, `OFF` e `PING` para o broker.

## Como executar

```bash
cd front-django
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Variáveis de ambiente úteis

- `MQTT_HOST`: padrão `broker.hivemq.com`
- `MQTT_PORT`: padrão `1883`
- `MQTT_USERNAME`: opcional
- `MQTT_PASSWORD`: opcional
- `MQTT_TEMPERATURE_TOPIC`: padrão `logistica/frio/temperatura`
- `MQTT_STATUS_TOPIC`: padrão `logistica/frio/status`
- `MQTT_COMMAND_TOPIC`: padrão `logistica/frio/comando`

## Integração com o Node-RED

O backend Django lê os mesmos tópicos publicados pelo Wokwi e pelo fluxo do Node-RED. A temperatura publicada no tópico `logistica/frio/temperatura` vira o dado principal do painel, e o status é derivado automaticamente com base no valor recebido.

Se o Django não mostrar dados, verifique se o Wokwi ainda está publicando em `broker.hivemq.com:1883` e se o Node-RED foi conectado ao mesmo broker e tópico.
