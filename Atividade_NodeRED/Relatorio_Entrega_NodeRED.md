# Atividade: Integracao do Projeto com Node-RED (MQTT)

## 1. Objetivo
Integrar o projeto IoT anterior ao ambiente Node-RED usando protocolo MQTT, com dashboard para monitoramento do sistema e controles de atuacao.

## 2. Ambiente e Execucao
### 2.1. Subir Node-RED via Docker
```bash
docker rm -f nodered >/dev/null 2>&1 || true
mkdir -p ~/nodered-data
sudo chown -R 1000:1000 ~/nodered-data
docker run -d --name nodered -p 1880:1880 -v ~/nodered-data:/data --restart unless-stopped nodered/node-red:latest
```

### 2.2. Broker MQTT
Use seu broker MQTT local ou em container (porta padrao 1883).
Exemplo local:
```bash
mosquitto -v
```

### 2.3. Pacote de Dashboard
No Node-RED, instalar o pacote:
- node-red-dashboard

Menu: Manage palette -> Install -> buscar por node-red-dashboard.

## 3. Importacao do Flow
Arquivo exportado pronto para importacao:
- flows_nodered_mqtt_dashboard.json

Passos:
1. Abrir Node-RED em http://localhost:1880.
2. Menu -> Import -> selecionar o JSON.
3. Validar configuracao do broker MQTT (localhost:1883 ou host do seu broker).
4. Deploy.

## 4. Topicos MQTT utilizados
- escola/turma1/iot/temperatura (telemetria)
- escola/turma1/iot/status (estado do sistema)
- escola/turma1/iot/atuador/cmd (comando ON/OFF)
- escola/turma1/iot/comando (comando PING)

## 5. Evidencias da Entrega (obrigatorio)
Inserir as imagens na pasta imagens e manter os nomes abaixo.

### 5.1. Dashboard em execucao
![Dashboard geral](imagens/dashboard_geral.png)

### 5.2. Dashboard com atuacao
![Dashboard com botao/switch acionado](imagens/dashboard_atuacao.png)

### 5.3. Flows no Node-RED
![Tela dos flows no editor Node-RED](imagens/flows_nodered.png)

### 5.4. (Opcional) Evidencia do MQTT
![Mensagens MQTT em terminal](imagens/mqtt_terminal.png)

## 6. Resultado observado
O dashboard exibiu corretamente o estado do sistema por meio dos topicos MQTT de temperatura e status. Tambem foi possivel atuar no sistema pelo switch/botao, publicando comandos no topico do atuador.

## 7. Arquivos entregues
- imagens do dashboard
- imagens dos flows
- json exportado do Node-RED (flows_nodered_mqtt_dashboard.json)

## 8. Observacoes
Se estiver em Codespaces e nao abrir a porta 1880 externamente, torne a porta publica ou use o encaminhamento de portas do ambiente.
