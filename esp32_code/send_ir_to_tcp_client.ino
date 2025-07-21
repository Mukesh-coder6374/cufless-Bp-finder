#include <WiFi.h>
#include <Wire.h>
#include "MAX30105.h"
#include "spo2_algorithm.h"

const char* ssid = "ESP_32";
const char* password = "";
const char* serverIP = "192.168.64.297";
const uint16_t serverPort = 8888;

WiFiClient client;
MAX30105 particleSensor;

const long FINGER_THRESHOLD = 20000;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected.");
  Serial.println(WiFi.localIP());

  if (!particleSensor.begin()) {
    Serial.println("MAX30102 not found. Check wiring!");
    while (1);
  }

  particleSensor.setup();
}

void loop() {
  long irValue = particleSensor.getIR();
  bool fingerDetected = irValue > FINGER_THRESHOLD;

  if (!fingerDetected) {
    Serial.println("Please place your finger...");
    delay(1000);
    return;
  }

  // Connect to Python TCP server
  if (!client.connect(serverIP, serverPort)) {
    Serial.println("Connection to PC server failed.");
    delay(2000);
    return;
  }

  client.println(irValue);  // Send IR value
  Serial.print("Sent IR: ");
  Serial.println(irValue);

  // Receive predicted SP, DP
  String response = client.readStringUntil('\n');
  client.stop();

  Serial.print("Response: ");
  Serial.println(response);

  int comma = response.indexOf(',');
  if (comma > 0) {
    int sp = response.substring(0, comma).toInt();
    int dp = response.substring(comma + 1).toInt();
    int hr = calculateHeartRate();
    float spo2 = calculateSpO2();

    Serial.printf("HR: %d bpm\nSpO2: %.1f %%\nSP: %d mmHg\nDP: %d mmHg\n", hr, spo2, sp, dp);
  }

  delay(3000);
}

int calculateHeartRate() {
  int beatsPerMinute = 0;
  long lastBeat = 0;

  for (int i = 0; i < 100; i++) {
    long irData = particleSensor.getIR();
    if (checkForBeat(irData)) {
      long delta = millis() - lastBeat;
      lastBeat = millis();
      beatsPerMinute = 60 * 1000 / delta;
    }
    delay(20);
  }

  return beatsPerMinute;
}

float calculateSpO2() {
  const int BUFFER_SIZE = 100;
  uint32_t irBuffer[BUFFER_SIZE];
  uint32_t redBuffer[BUFFER_SIZE];
  int spo2, hr;

  for (int i = 0; i < BUFFER_SIZE; i++) {
    irBuffer[i] = particleSensor.getIR();
    redBuffer[i] = particleSensor.getRed();
    delay(20);
  }

  maxim_heart_rate_and_oxygen_saturation(irBuffer, redBuffer, BUFFER_SIZE, &hr, &spo2);
  return spo2;
