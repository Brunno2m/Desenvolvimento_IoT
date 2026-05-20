INSTITUTO FEDERAL DE EDUCACAO, CIENCIA E TECNOLOGIA DO RIO GRANDE DO NORTE  
CAMPUS PARNAMIRIM  
TECNOLOGIA EM SISTEMAS PARA INTERNET  
DISCIPLINA: PROGRAMACAO PARA INTERNET DAS COISAS


BRUNNO DE MELO MARQUES  
EMANUEL CORREIA TAVARES


SISTEMA DE TELEMETRIA E MONITORAMENTO DE CADEIA DE FRIO PARA TRANSPORTE FRIGORIFICO:  
PROTOTIPO FUNCIONAL DE IOT INTEGRADO COM NODE-RED E DJANGO


PARNAMIRIM - RN  
2026

\newpage

# 1 INTRODUCAO

O transporte de cargas pereciveis exige controle continuo de temperatura para reduzir perdas logisticas e preservar a qualidade sanitaria dos produtos. Nesse contexto, foi desenvolvido um prototipo de Internet das Coisas (IoT) para monitoramento termico de uma cadeia de frio, com foco em telemetria em tempo real, visualizacao operacional e envio de comandos remotos.

O sistema integra tres camadas principais: dispositivo embarcado (ESP32), middleware de orquestracao (Node-RED) e interface de aplicacao (Django). A proposta permite observar variacoes de temperatura simuladas em bancada por potenciometro e validar, na pratica, a comunicacao MQTT entre hardware e software.

# 2 OBJETIVOS

## 2.1 Objetivo geral

Desenvolver e validar um prototipo funcional de monitoramento termico para transporte frigorifico com comunicacao MQTT e painel operacional web.

## 2.2 Objetivos especificos

- Capturar variacao analogica de temperatura simulada por potenciometro no ESP32.
- Publicar dados de temperatura e status em topicos MQTT.
- Centralizar ingestao, processamento e exposicao de estado no Node-RED.
- Disponibilizar painel web em Django para consulta de estado e envio de comandos.
- Validar o funcionamento em ambiente de simulacao (Wokwi) e em bancada fisica.

# 3 ARQUITETURA GERAL DO SISTEMA

A arquitetura foi estruturada de forma desacoplada e orientada a eventos:

- Camada de dispositivo: ESP32 (simulado no Wokwi e implementado fisicamente).
- Camada de mensageria: broker publico MQTT (HiveMQ).
- Camada de orquestracao: Node-RED (Codespaces), consumindo topicos, consolidando estado e expondo endpoints HTTP.
- Camada de aplicacao: Django, com front-end moderno para visualizacao e comando.

Topicos MQTT utilizados:

- logistica/frio/temperatura
- logistica/frio/status
- logistica/frio/comando

Endpoints Node-RED utilizados:

- GET /state
- POST /command
- GET /nrtest

# 4 DETALHAMENTO DO HARDWARE E CONEXOES

Para a demonstracao final em bancada fisica, o circuito foi simplificado para os componentes efetivamente utilizados:

- ESP32
- Potenciometro no GPIO 35 (ADC) para simular variacao termica
- LED verde para faixa ideal
- LED vermelho para faixa de alerta
- Resistores limitadores de corrente para os LEDs

Faixas adotadas no firmware:

- Temperatura ideal: de 2,0 C a 8,0 C (LED verde)
- Fora da faixa ideal: abaixo de 2,0 C ou acima de 8,0 C (LED vermelho)

Observacao tecnica: o pino ADC do ESP32 opera em 3,3 V, portanto o potenciometro deve ser alimentado com 3,3 V e GND.

Figura 1 - Montagem fisica do prototipo em bancada  
Fonte: Autores (2026).

Figura 2 - Simulacao no ambiente Wokwi  
Fonte: Autores (2026).

# 5 FIRMWARE DO ESP32

O firmware foi implementado com as bibliotecas WiFi.h e PubSubClient.h. O ciclo de operacao contempla:

- conexao Wi-Fi em modo station;
- reconexao MQTT automatica em caso de queda;
- leitura analogica do potenciometro com media amostral para reduzir ruido;
- conversao da leitura ADC para escala termica de -10 C a 30 C;
- aplicacao de histerese para evitar oscilacao visual excessiva nos LEDs;
- publicacao periodica da temperatura no topico MQTT.

No cenario final de apresentacao, sensores e atuadores nao utilizados (ex.: PIR e buzzer) foram desconsiderados para manter foco no requisito principal de monitoramento termico com sinalizacao visual simples.

# 6 INTEGRACAO COM NODE-RED

O Node-RED atua como nucleo de integracao do sistema. O fluxo implementado executa:

- assinatura dos topicos de temperatura e status;
- normalizacao do payload de temperatura para valor numerico;
- atualizacao de estado agregado para dashboard;
- exposicao de API HTTP para leitura de estado e envio de comando;
- apresentacao em dashboard com indicadores de operacao.

A persistencia do estado do Node-RED foi configurada por contextStorage localfilesystem (arquivo local de contexto), garantindo retencao basica do estado entre reinicios do runtime.

Figura 3 - Fluxo de orquestracao no Node-RED  
Fonte: Autores (2026).

# 7 APLICACAO WEB EM DJANGO

A aplicacao Django foi desenvolvida como interface de supervisao e comando. O front-end executa estrategia Node-RED first:

- consulta preferencial do estado via endpoint do Node-RED;
- envio preferencial de comando via endpoint do Node-RED;
- fallback para API Django em caso de indisponibilidade do Node-RED.

Com esse modelo, o middleware Node-RED permanece como prioridade operacional, enquanto a interface Django oferece uma camada visual moderna e adequada para demonstracao.

Figura 4 - Dashboard da aplicacao Django  
Fonte: Autores (2026).

# 8 VALIDACAO FUNCIONAL

A validacao do prototipo foi realizada com testes de comunicacao e observabilidade:

- recepcao de telemetria termica no Node-RED em tempo real;
- atualizacao dos widgets do dashboard Node-RED;
- resposta positiva dos endpoints HTTP de estado e comando;
- consumo de estado e envio de comando pela interface Django;
- verificacao visual de mudanca de faixa termica pelos LEDs no ESP32.

Resultados observados:

- comunicacao MQTT funcional e estavel para o escopo do prototipo;
- interoperabilidade entre ESP32, Node-RED e Django confirmada;
- capacidade de demonstracao academica atendida com arquitetura clara.

# 9 LIMITACOES E TRABALHOS FUTUROS

Embora funcional para apresentacao e avaliacao academica, o sistema ainda possui pontos de evolucao:

- autenticacao e autorizacao de rotas de comando (ex.: JWT);
- uso de TLS no broker MQTT e nos endpoints HTTP;
- persistencia historica de longo prazo em banco relacional;
- substituicao de polling periodico por atualizacao em tempo real com WebSocket;
- parametrizacao dinamica de limites de temperatura por tipo de carga.

# 10 CONCLUSAO

O prototipo desenvolvido atendeu ao objetivo de monitorar e demonstrar variacoes termicas de uma cadeia de frio por meio de uma arquitetura IoT integrada. A combinacao de ESP32, MQTT, Node-RED e Django proporcionou uma base tecnica consistente para coleta, visualizacao e comando remoto.

Os resultados confirmam a viabilidade do modelo para fins didaticos e para evolucao incremental em cenarios de maior maturidade, com seguranca e persistencia aprimoradas.

\newpage

# REFERENCIAS

HIVEMQ. MQTT Broker (Public Broker). Disponivel em: <https://www.hivemq.com/>. Acesso em: 20 maio 2026.

NODE-RED. Flow-based programming for the Internet of Things. Disponivel em: <https://nodered.org/>. Acesso em: 20 maio 2026.

DJANGO SOFTWARE FOUNDATION. Django Documentation. Disponivel em: <https://docs.djangoproject.com/>. Acesso em: 20 maio 2026.

ESPRESSIF SYSTEMS. ESP32 Series Datasheet. Disponivel em: <https://www.espressif.com/>. Acesso em: 20 maio 2026.
