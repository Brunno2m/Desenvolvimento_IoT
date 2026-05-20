#include <WiFi.h>
#include <PubSubClient.h>
#include <DHTesp.h>

const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "broker.hivemq.com";
const char* topic_temp = "logistica/frio/temperatura";
const char* topic_status = "logistica/frio/status";
const char* topic_command = "logistica/frio/comando";

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

  if (receivedTopic == topic_command) {
    if (message == "ON") {
      applyActuatorState(true);
      client.publish(topic_status, "COMANDO_ON", true);
    } else if (message == "OFF") {
      applyActuatorState(false);
      client.publish(topic_status, "COMANDO_OFF", true);
    } else if (message == "PING") {
      client.publish(topic_status, "PING_OK", true);
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
    String clientId = "wokwi-esp32-" + String((uint32_t)ESP.getEfuseMac(), HEX);
    if (client.connect(clientId.c_str())) {
      Serial.println("ok");
      client.subscribe(topic_command);
      client.publish(topic_status, "ONLINE", true);
    } else {
      Serial.print("falhou, rc=");
      Serial.println(client.state());
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
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
    client.publish(topic_temp, tempString, false);
    Serial.print("Temperatura publicada: ");
    Serial.println(tempString);

    if (!coolingOn) {
      bool alert = data.temperature > 8.0;
      digitalWrite(LED_RED, alert ? HIGH : LOW);
      digitalWrite(LED_GREEN, alert ? LOW : HIGH);
      client.publish(topic_status, alert ? "ALERTA" : "NORMAL", true);
    }
  }
}
