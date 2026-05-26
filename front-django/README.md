# Front Django - Frota Frigorificada

Aplicação Django para visualizar, em tempo real, a temperatura da câmara frigorífica e o status recebido pelo Node-RED via MQTT.

## O que a aplicação faz

- Consome o estado publicado pelo Node-RED via HTTP em `/state`.
- Exibe uma dashboard visual com frota, histórico por caminhão, conexão com o Node-RED e status operacional.
- Envia comandos `ON`, `OFF` e `PING` para o Node-RED em `/command`.

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

- `NODE_RED_BASE_URL`: padrão `http://localhost:1880`

## Integração com o Node-RED

O backend Django não assina MQTT diretamente. Ele consulta o endpoint `/state` do Node-RED e usa a resposta como fonte única do painel. O Node-RED, por sua vez, continua conectado ao broker MQTT e recebe os dados do Wokwi.

Se o Django não mostrar dados, verifique se o Node-RED está ativo e expondo `/state` em `http://localhost:1880`, e se o flow MQTT está recebendo as mensagens do Wokwi.
