# IFRN - Parnamirim

## Programação para Internet das Coisas

# Relatório do Projeto IoT

### Integracão entre Wokwi, Node-RED e Django para monitoramento de frota frigorificada

**Componentes do grupo**

- Brunno de Melo Marques
- Emanuel Correia Tavares

**Data**

- Maio de 2026

---

## 1. Introdução

Este projeto apresenta uma solução de Internet das Coisas voltada ao monitoramento de uma frota de caminhões frigorificados. A proposta integra simulador de hardware, mensageria MQTT, automação de fluxo e interface web, permitindo visualizar em tempo quase real a temperatura da câmara e o estado operacional da frota.

## 2. Objetivo

Desenvolver uma aplicação web capaz de receber telemetria de temperatura, processar os dados publicados pelo dispositivo simulado e exibi-los em um painel visual profissional, com foco em operação logística e rastreio térmico.

## 3. Solução proposta

A solução foi estruturada com os seguintes componentes:

- **Wokwi:** simula o dispositivo embarcado com ESP32, sensor DHT22 e LEDs de indicação.
- **Broker MQTT:** recebe as mensagens publicadas pelo dispositivo e distribui os dados aos consumidores.
- **Node-RED:** atua como camada de integração e automação, consumindo a telemetria do broker.
- **Django:** fornece a interface visual principal, com dashboard de frota, leitura de temperatura e acompanhamento do estado do sistema.

O fluxo foi organizado para que a temperatura gerada no Wokwi seja publicada em um tópico MQTT e consumida pelo painel Django. O Node-RED participa do ecossistema como componente de integração e observação do tráfego MQTT.

## 4. Arquitetura do sistema

### 4.1. Dispositivo simulado

O código do Wokwi utiliza um ESP32, conexão Wi-Fi e a biblioteca PubSubClient para enviar a temperatura lida pelo DHT22 ao broker MQTT. O envio é feito no tópico `logistica/frio/temperatura`.

### 4.2. Camada de mensageria

O broker MQTT atua como ponto central da comunicação, recebendo as mensagens do Wokwi e repassando-as para os assinantes interessados, entre eles o Node-RED e o Django.

### 4.3. Camada de integração

O Node-RED recebe o fluxo de dados MQTT, permitindo visualização, automação e futuras expansões de controle. Ele funciona como ponte de observação entre a telemetria e a interface web.

### 4.4. Interface web

O Django foi desenvolvido como dashboard executivo da frota, apresentando a temperatura atual, o estado de conexão, o histórico de leitura e cartões visuais dos veículos. O primeiro caminhão utiliza a telemetria real; os demais são exibidos com dados simulados para reforçar a percepção de frota operacional.

## 5. Funcionalidades implementadas

- Monitoramento de temperatura em tempo real.
- Indicação visual por meio de LED verde ou vermelho na frota.
- Exibição de histórico da telemetria.
- Painel com visual limpo e profissional.
- Separação entre o caminhão monitorado ao vivo e os demais cartões simulados.

## 6. Resultados obtidos

A integração entre Wokwi, MQTT, Node-RED e Django permitiu construir uma solução funcional de monitoramento IoT. O painel web passou a refletir a telemetria publicada pelo dispositivo simulado, oferecendo uma visão clara do estado térmico da operação.

## 7. Conclusão

O projeto demonstrou, na prática, como tecnologias de IoT podem ser combinadas para construir um sistema de monitoramento logístico com boa usabilidade e arquitetura simples. A solução atende ao objetivo de representar uma frota frigorificada com destaque para o controle de temperatura, elemento essencial em operações de transporte refrigerado.

## 8. Tecnologias utilizadas

- ESP32 no simulador Wokwi
- Sensor DHT22
- Protocolo MQTT
- Node-RED
- Django
- HTML, CSS e JavaScript
