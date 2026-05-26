# Wokwi ESP32 MQTT DHT

Projeto mínimo para simular no Wokwi dentro do Codespace/VS Code.

Arquivos:
- `sketch.ino`: leitura do DHT22 e publicação MQTT
- `diagram.json`: circuito no simulador
- `libraries.txt`: dependências do sketch
- `wokwi.toml`: configuração do projeto

Tópicos MQTT:
- `logistica/frio/<device_id>/temperatura`
- `logistica/frio/<device_id>/status`
- `logistica/frio/<device_id>/comando`
- `logistica/frio/comando` (comando broadcast compatível com a versão anterior)

Antes de duplicar a simulação no Wokwi, altere a constante `device_id` no `sketch.ino` para um valor único, como `truck-01`, `truck-02` e `truck-03`.

Comandos aceitos no tópico de comando:
- `ON`
- `OFF`
- `PING`

Se estiver usando o Wokwi no VS Code, abra esta pasta e rode a simulação localmente.
