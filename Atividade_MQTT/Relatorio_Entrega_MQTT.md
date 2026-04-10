# Atividade Prática: Troca de mensagens MQTT em ambiente local

## Entrega da Atividade

### 1. Comandos Utilizados

**Iniciar o Broker Mosquitto em background no servidor local**
```bash
mosquitto -p 1883 &
```

**Assinar um tópico (Subscriber)**
```bash
mosquitto_sub -h localhost -t escola/turma1/teste -v
```

**Publicar mensagens em um tópico (Publisher)**
```bash
mosquitto_pub -h localhost -t escola/turma1/teste -m "Mensagem 1"
mosquitto_pub -h localhost -t escola/turma1/teste -m "Mensagem 2"
mosquitto_pub -h localhost -t escola/turma1/teste -m "Mensagem 3"
```

---

### 2. Conceitos: Broker, Publisher e Subscriber

- **Broker**: O MQTT é guiado pelo modelo publish-subscribe. O broker é o servidor central encarregado de receber todas as mensagens dos *publishers*, filtrar pelo assunto (tópico) e enviar essas mensagens para os respectivos *subscribers* (assinantes) que estão interessados naqueles tópicos.
- **Publisher**: É o atuador ou o cliente (software/dispositivo) que gera e *publica* as mensagens/dados direcionadas a um determinado "tópico". Ele não sabe quem vai receber essa informação.
- **Subscriber**: É o cliente (software/dispositivo) que deseja receber determinados dados. Para receber, ele *assina/inscreve* (subscribe) em um determinado tópico no broker. Quando os dados chegam ao broker nesse tópico, o broker os repassa para todos os *subscribers* inscritos nele.

---

### 3. Teste do Recurso Adicional

**Opção escolhida:** Mensagem retida (flag `-r`).

**Comandos executados:**
```bash
mosquitto_pub -h localhost -t escola/turma1/aviso -m "Prova na sexta" -r

# E depois da publicação, abrimos um assinante:
mosquitto_sub -h localhost -t escola/turma1/aviso -v
```

**Explicação do resultado obtido:**
Normalmente, no MQTT, um *subscriber* só começa a receber mensagens de um tópico **a partir do momento de sua conexão**. Se um *publisher* enviar algo e ninguém estiver escutando no exato milissegundo, a mensagem se perde.
Entretanto, ao utilizar a diretriz/parâmetro **`-r` (retained message)** na publicação, informamos ao broker que ele deve "reter/salvar" a última mensagem enviada para aquele tópico.
Deste modo, assim que um NOVO assinante se constectou (`mosquitto_sub -h localhost -t escola/turma1/aviso -v`) MESMO DEPOIS da mensagem ter sigo publicada, ele **imediatamente recebeu** a mensagem retida `"Prova na sexta"`. Este recurso é excelente para informar estados iniciais, avisos duradouros ou ultimas métricas assim que um dispositivo liga.

---
*Para gerar as evidências de prints que devem ser entregues junto com este documento (Prints do broker, publicador, assinante e teste adicional), você pode abrir instâncias do terminal em seu ambiente local (VScode, por exemplo) e rodar os comandos dispostos acima visíveis na mesma tela e tirar o print em conjunto.*
