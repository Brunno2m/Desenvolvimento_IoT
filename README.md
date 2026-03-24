# Desenvolvimento_IoT


docker run -d --name nodered -p 1880:1880 -v nodered_data:/data --restart unless-stopped nodered/node-red



docker run -d --name nodered -p 1880:1880 -v nodered_data:/data --restart unless-stopped nodered/node-reddocker run -d --name nodered -p 1880:1880 -v nodered_data:/data --restart unless-stopped nodered/node-red


docker rm -f nodered >/dev/null 2>&1 || true && sudo mkdir -p ~/nodered-data && sudo chown -R 1000:1000 ~/nodered-data && docker run -d --name nodered -p 1880:1880 -v ~/nodered-data:/data --restart unless-stopped nodered/node-red:latest && (gh codespace ports visibility 1880:public -c "$CODESPACE_NAME" >/dev/null 2>&1 || true) && sleep 5 && URL="https://${CODESPACE_NAME}-1880.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}" && echo "Node-RED: $URL" && curl -I -sS "$URL" | head -n 1