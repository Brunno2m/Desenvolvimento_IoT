# Relatório Completo: Fundamentos e Prática com Protocolo MQTT

## 1. Introdução ao MQTT
O **MQTT (Message Queuing Telemetry Transport)** é um protocolo de mensagens leve, projetado para dispositivos com restrições de processamento e para redes de baixa largura de banda, alta latência ou não confiáveis. Hoje é amplamente considerado o protocolo padrão para a Internet das Coisas (IoT). O protocolo funciona de forma assíncrona, eliminando a necessidade de os dispositivos estarem conectados ao mesmo tempo.

## 2. Conceitos Fundamentais

### Modelo Publish-Subscribe (Pub/Sub)
Diferente do modelo tradicional cliente-servidor, no MQTT, os clientes que enviam informações não se comunicam diretamente com os clientes que recebem. Em vez disso, a comunicação é gerenciada por um servidor central, criando um desacoplamento poderoso.

* **Broker (Servidor Central):** É o coração do protocolo MQTT. Ele é responsável por receber todas as mensagens, analisar os tópicos, filtrar e encaminhar as informações de forma eficiente para os clientes interessados.
* **Publisher (Publicador):** Um cliente (como um sensor de temperatura) que envia (publica) uma mensagem e anexa a ela um "tópico". Ele não precisa saber se há alguém escutando.
* **Subscriber (Assinante):** Um cliente que informa ao broker que está interessado em um "tópico" específico. Quando o broker recebe mensagens com esse tópico, ele as repassa imediatamente ao assinante.
* **Tópicos:** São strings UTF-8 estruturadas em níveis separados por barras (ex: `escola/turma1/teste`), funcionando como canais de comunicação ou endereços lógicos de roteamento.

---

## 3. Evidências Práticas da Atividade

As seções a seguir demonstram a aplicação prática destes conceitos utilizando o **Eclipse Mosquitto**, um broker MQTT de código aberto, operando em ambiente local.

### 3.1. Execução do Broker MQTT
A instalação do Mosquitto e de seus utilitários de cliente (`mosquitto-clients`) foi realizada com sucesso. O serviço local é responsável pela mediação de nossas mensagens.

**Comando utilizado para iniciar o serviço localmente na porta padrão (1883):**
```bash
mosquitto -v
# ou via serviço dependendo da instalação
```

> **📸 Inserir Imagem 1 Aqui**
> *Substitua o link abaixo pelo caminho da sua imagem mostrando o terminal com o broker em execução.*
> `![Terminal com o Broker em execução](imagens/broker.png)`

### 3.2. Assinando um Tópico (Subscriber)
Para receber as mensagens, um terminal foi designado exclusivamente como assinante, aguardando publicações sob um tópico específico.

**Comando utilizado para assinar o tópico `escola/turma1/teste`:**
```bash
mosquitto_sub -h localhost -t escola/turma1/teste -v
```

> **📸 Inserir Imagem 2 Aqui**
> *Substitua o link abaixo pela captura de tela mostrando o terminal inscrito (aguardando ou recebendo os dados).*
> `![Terminal Assinando o Tópico](imagens/subscriber.png)`

### 3.3. Publicando Mensagens (Publisher)
Com o assinante ativo, as mensagens foram disparadas partindo de outro cliente (terminal), simulando um dispositivo enviando pacotes de dados.

**Comandos utilizados:**
```bash
mosquitto_pub -h localhost -t escola/turma1/teste -m "Mensagem 1"
mosquitto_pub -h localhost -t escola/turma1/teste -m "Mensagem 2"
mosquitto_pub -h localhost -t escola/turma1/teste -m "Mensagem 3"
```

> **📸 Inserir Imagem 3 Aqui**
> *Substitua o link pela imagem do terminal publicador disparando as mensagens citadas acima, preferencialmente lado a lado com o assinante os recebendo.*
> `![Terminal Publicando Mensagens](imagens/publisher.png)`

---

## 4. Testes Avançados: Mensagem Retida (Retained Message)

O recurso de **Mensagem Retida (flag `-r`)** diz ao Broker para armazenar a última mensagem publicada em um tópico específico. Mesmo que um *Subscriber* se conecte *depois* da publicação ter ocorrido, ele receberá imediatamente a informação que ficou "retida" no servidor.

Para validar esta funcionalidade, o seguinte teste foi executado:

**Publicando um aviso com retenção:**
```bash
mosquitto_pub -h localhost -t escola/turma1/aviso -m "Prova na sexta" -r
```

Logo após publicar e sem nenhum cliente escutando no momento, abriu-se um novo assinante requisitando o tópico:
```bash
mosquitto_sub -h localhost -t escola/turma1/aviso -v
```
**Resultado:** Imediatamente após a conexão, o assinante imprimiu a string `"Prova na sexta"`.

> **📸 Inserir Imagem 4 Aqui**
> *Substitua o link abaixo pela sua captura do terminal mostrando a publicação com a flag "-r" e o recebimento pelo consumidor.*
> `![Teste do Recurso Adicional - Mensagem Retida](imagens/retained.png)`

---

## 5. Conclusão
Esta atividade comprovou na prática o princípio do desacoplamento do protocolo MQTT. Observou-se com sucesso os papéis de *publisher*, *subscriber* e o roteamento operado pelo *broker* baseando-se em hierarquia de tópicos. Além disso, constatou-se a utilidade de armazenamento e preservação de estados oferecidos por *retained messages* — recurso amplamente usado em painéis IoT para exibir o último estado conhecido de um equipamento antes mesmo que ele publique seu próximo dado.
