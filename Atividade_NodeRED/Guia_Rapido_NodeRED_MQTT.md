# Guia Rapido: Execucao da Atividade Node-RED + MQTT

## 1. Subir Node-RED em Docker
```bash
node-red
```

## 2. Abrir Node-RED
- URL local: http://localhost:1880
- Em Codespaces: usar URL encaminhada da porta 1880.

## 3. Instalar dashboard
- Menu -> Manage palette -> Install -> node-red-dashboard

Se aparecer aviso de no configurado em `ui_gauge` ou `ui_text`:
- Confirme que o pacote instalado e `node-red-dashboard` (Dashboard 1.x).
- Se tiver instalado `@flowfuse/node-red-dashboard`, remova para evitar conflito nesta atividade.
- Exclua o flow antigo no editor e importe novamente o arquivo `flows_nodered_mqtt_dashboard.json` atualizado.

## 4. Importar flow
- Importar arquivo: flows_nodered_mqtt_dashboard.json
- Conferir broker MQTT em broker.hivemq.com:1883.
- Clicar em Deploy.

Se o MQTT ficar em amarelo como "conectando":
- Verifique se os dois containers estao ativos com `docker ps`.
- O broker no Node-RED deve estar como host `broker.hivemq.com` e porta `1883`.
- Apos ajustar o broker, clique em Deploy novamente.

## 5. Gerar evidencias
- Abrir dashboard em /ui
Exemplo: http://localhost:1880/ui

Tirar prints:
1. Dashboard geral com temperatura e status.
2. Dashboard com switch/botao acionado.
3. Editor de flows mostrando o diagrama completo.

Salvar em:
- imagens/dashboard_geral.png
- imagens/dashboard_atuacao.png
- imagens/flows_nodered.png

## 6. Arquivos para entrega
- Relatorio_Entrega_NodeRED.md
- flows_nodered_mqtt_dashboard.json
- pasta imagens com os prints
