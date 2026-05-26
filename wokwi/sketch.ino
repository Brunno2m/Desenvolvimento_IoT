#include <WiFi.h>
#include <PubSubClient.h>
#include <DHTesp.h>

const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "broker.hivemq.com";
// Altere este valor em cada copia do projeto no Wokwi web.
// Ex.: truck-01, truck-02, truck-03.
const char* device_id = "truck-01";
const char* broadcast_command_topic = "logistica/frio/comando";

String topic_temp;
String topic_status;
String topic_command;

#define DHT_PIN 15
#define LED_GREEN 4
#define LED_RED 2

WiFiClient espClient;
PubSubClient client(espClient);
DHTesp dht;

unsigned long lastMsg = 0;
bool coolingOn = false;

void applyActuatorState(bool on) {
  coolingOn = on;
  digitalWrite(LED_GREEN, on ? HIGH : LOW);
  digitalWrite(LED_RED, on ? LOW : HIGH);
}

void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  String receivedTopic = String(topic);
  String message;
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  message.trim();
  message.toUpperCase();

  if (receivedTopic == topic_command || receivedTopic == broadcast_command_topic) {
    if (message == "ON") {
      applyActuatorState(true);
      client.publish(topic_status.c_str(), "COMANDO_ON", true);
    } else if (message == "OFF") {
      applyActuatorState(false);
      client.publish(topic_status.c_str(), "COMANDO_OFF", true);
    } else if (message == "PING") {
      client.publish(topic_status.c_str(), "PING_OK", true);
    }
  }
}

void setup_wifi() {
  WiFi.mode(WIFI_STA);
  Serial.print("Conectando no Wi-Fi ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("Wi-Fi conectado");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Conectando MQTT...");
    String clientId = String("wokwi-esp32-") + device_id + "-" + String((uint32_t)ESP.getEfuseMac(), HEX);
    if (client.connect(clientId.c_str())) {
      Serial.println("ok");
      client.subscribe(topic_command.c_str());
      client.subscribe(broadcast_command_topic);
      client.publish(topic_status.c_str(), "ONLINE", true);
    } else {
      Serial.print("falhou, rc=");
      Serial.println(client.state());
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  topic_temp = String("logistica/frio/") + device_id + "/temperatura";
  topic_status = String("logistica/frio/") + device_id + "/status";
  topic_command = String("logistica/frio/") + device_id + "/comando";
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(onMqttMessage);
  dht.setup(DHT_PIN, DHTesp::DHT22);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  if (millis() - lastMsg > 3000) {
    lastMsg = millis();

    TempAndHumidity data = dht.getTempAndHumidity();
    if (isnan(data.temperature)) {
      Serial.println("Falha ao ler o DHT");
      return;
    }

    char tempString[8];
    dtostrf(data.temperature, 1, 2, tempString);
    client.publish(topic_temp.c_str(), tempString, false);
    Serial.print("Temperatura publicada: ");
    Serial.println(tempString);

    if (!coolingOn) {
      bool alert = data.temperature > 8.0;
      digitalWrite(LED_RED, alert ? HIGH : LOW);
      digitalWrite(LED_GREEN, alert ? LOW : HIGH);
      client.publish(topic_status.c_str(), alert ? "ALERTA" : "NORMAL", true);
    }
  }
}
