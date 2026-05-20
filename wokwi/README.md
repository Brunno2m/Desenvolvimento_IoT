# Wokwi ESP32 MQTT DHT

Projeto mínimo para simular no Wokwi dentro do Codespace/VS Code.

Arquivos:
- `sketch.ino`: leitura do DHT22 e publicação MQTT
- `diagram.json`: circuito no simulador
- `libraries.txt`: dependências do sketch
- `wokwi.toml`: configuração do projeto

Tópicos MQTT:
- `logistica/frio/temperatura`
- `logistica/frio/status`
- `logistica/frio/comando`

Comandos aceitos no tópico de comando:
- `ON`
- `OFF`
- `PING`

Se estiver usando o Wokwi no VS Code, abra esta pasta e rode a simulação localmente.
