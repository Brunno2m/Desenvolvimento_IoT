# Guia Rapido: Execucao da Atividade Node-RED + MQTT

## 1. Subir Node-RED em Docker
```bash
docker rm -f nodered >/dev/null 2>&1 || true
mkdir -p ~/nodered-data
sudo chown -R 1000:1000 ~/nodered-data
docker run -d --name nodered -p 1880:1880 -v ~/nodered-data:/data --restart unless-stopped nodered/node-red:latest
```

## 2. Abrir Node-RED
- URL local: http://localhost:1880
- Em Codespaces: usar URL encaminhada da porta 1880.

## 3. Instalar dashboard
- Menu -> Manage palette -> Install -> node-red-dashboard

## 4. Importar flow
- Importar arquivo: flows_nodered_mqtt_dashboard.json
- Conferir broker MQTT em localhost:1883 (ou editar para seu host).
- Clicar em Deploy.

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
