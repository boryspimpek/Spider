#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <ArduinoJson.h>

// Konfiguracja Access Point
const char* ap_ssid = "SpiderRobot";     // Nazwa sieci AP
const char* ap_password = "12345678";          // Hasło AP (minimum 8 znaków)

// UDP
WiFiUDP udp;
const int udpPort = 8888;

// PCA9685
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// Parametry serw MG90S
const int SERVOMIN = 150;  // Minimalna wartość PWM (około 0.6ms)
const int SERVOMAX = 600;  // Maksymalna wartość PWM (około 2.4ms)

void setup() {
  Serial.begin(115200);
  
  // Inicjalizacja I2C
  Wire.begin();
  
  // Inicjalizacja PCA9685
  pwm.begin();
  pwm.setPWMFreq(50);  // 50 Hz dla serw
  
  Serial.println();
  Serial.println("Uruchamianie Access Point...");
  
  // Konfiguracja Access Point
  WiFi.mode(WIFI_AP);
  
  // Opcjonalnie: ustaw statyczny IP dla AP
  IPAddress local_IP(192, 168, 4, 1);
  IPAddress gateway(192, 168, 4, 1);
  IPAddress subnet(255, 255, 255, 0);
  WiFi.softAPConfig(local_IP, gateway, subnet);
  
  // Uruchom Access Point
  bool ap_success = WiFi.softAP(ap_ssid, ap_password);
  
  if (ap_success) {
    Serial.println("Access Point uruchomiony pomyślnie!");
    Serial.print("Nazwa sieci (SSID): ");
    Serial.println(ap_ssid);
    Serial.print("Hasło: ");
    Serial.println(ap_password);
    Serial.print("IP Access Point: ");
    Serial.println(WiFi.softAPIP());
  } else {
    Serial.println("Błąd uruchamiania Access Point!");
  }
  
  // Uruchomienie UDP
  udp.begin(udpPort);
  Serial.printf("Serwer UDP uruchomiony na porcie: %d\n", udpPort);
  
  // Ustaw serwa w pozycji początkowej (90°)
  setServoAngle(3, 90);
  setServoAngle(4, 90);
  
  Serial.println("System gotowy do pracy!");
  Serial.println("Połącz się z siecią WiFi: " + String(ap_ssid));
  Serial.println("Wysyłaj komendy UDP na adres: " + WiFi.softAPIP().toString() + ":" + String(udpPort));
}

void loop() {
  // Sprawdź czy są dane UDP
  int packetSize = udp.parsePacket();
  if (packetSize) {
    // Odczytaj dane
    char incomingPacket[256];
    int len = udp.read(incomingPacket, 255);
    if (len > 0) {
      incomingPacket[len] = '\0';
    }
    
    Serial.printf("Otrzymano UDP od %s: %s\n", udp.remoteIP().toString().c_str(), incomingPacket);
    
    // Parsuj i wykonaj komendę
    parseAndExecuteCommand(incomingPacket);
    
    // Wyślij potwierdzenie
    udp.beginPacket(udp.remoteIP(), udp.remotePort());
    udp.write("OK");
    udp.endPacket();
  }
  
  // Opcjonalnie: wyświetl liczbę połączonych klientów
  static unsigned long lastClientCheck = 0;
  if (millis() - lastClientCheck > 10000) {  // Co 10 sekund
    Serial.printf("Połączonych klientów: %d\n", WiFi.softAPgetStationNum());
    lastClientCheck = millis();
  }
  
  delay(10);
}

void parseAndExecuteCommand(const char* command) {
  DynamicJsonDocument doc(512);
  DeserializationError error = deserializeJson(doc, command);
  
  if (error) {
    Serial.print("Błąd parsowania JSON: ");
    Serial.println(error.c_str());
    return;
  }
  
  // Sprawdź czy to komenda set_servo
  if (doc.containsKey("set_servo")) {
    JsonObject servos = doc["set_servo"];
    
    Serial.println("Ustawianie serw:");
    
    // Przejdź przez wszystkie serwa w komendzie
    for (JsonPair kv : servos) {
      int channel = atoi(kv.key().c_str());
      int angle = kv.value();
      
      Serial.printf("  Servo kanał %d -> %d°\n", channel, angle);
      setServoAngle(channel, angle);
    }
  }
}

void setServoAngle(int channel, int angle) {
  // Ogranicz kąt do 0-180°
  angle = constrain(angle, 0, 180);
  
  // Przelicz kąt na wartość PWM
  int pwmValue = map(angle, 0, 180, SERVOMIN, SERVOMAX);
  
  // Ustaw PWM
  pwm.setPWM(channel, 0, pwmValue);
  
  Serial.printf("Kanał %d ustawiony na %d° (PWM: %d)\n", channel, angle, pwmValue);
}

int angleToPWM(int angle) {
  return map(angle, 0, 180, SERVOMIN, SERVOMAX);
}
