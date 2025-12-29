// ESP32 + 74HC595 (bit-bang) + HC-SR04 + WiFi + API
// Viết theo style sketch (.ino): pin #define + setup()/loop()
// Lưu ý: PlatformIO cần include Arduino.h trong file .cpp

#include <Arduino.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <WebServer.h>

// GPIO mapping (as provided)
#define PIN_TRIG 25
#define PIN_ECHO 26

// ================== CẤU HÌNH WIFI ==================
// SỬA THÀNH SSID VÀ PASSWORD WIFI THỰC TẾ
// WiFi dưới đây chỉ để mô phỏng trên Wokwi simulator
const char* ssid = "Wokwi-GUEST";           
const char* password = "";

// ===== Lựa chọn 1: WiFi AP (UNO R4 phát WiFi) =====
// Cấu hình IP tĩnh cho ESP32 (fallback)
IPAddress local_IP(192, 168, 4, 5);      
IPAddress gateway(192, 168, 4, 2);       
IPAddress subnet(255, 255, 255, 0);      

// HTTP Server cho Pull Model
WebServer server(80);

// Dữ liệu hiện tại cho Pull Model
int currentDistances[15] = {0};

// WiFi reconnection management
unsigned long lastWiFiCheck = 0;
const unsigned long WIFI_CHECK_INTERVAL = 30000; // Check every 30 seconds
const unsigned long WIFI_RECONNECT_TIMEOUT = 10000; // 10s timeout for reconnect

// ================== FORWARD DECLARATIONS ==================
void reconnectWiFi();
void handleGetData();
void handleDetect();

// CD74HC4067 (16:1 MUX) - đưa 1 trong 16 ECHO về PIN_ECHO
#define MUX_S0 12
#define MUX_S1 13
#define MUX_S2 14
#define MUX_S3 27



#define PIN_595_OE 33 // OE active LOW
#define PIN_595_MR 32 // MR active LOW
#define PIN_595_DS 23
#define PIN_595_SH 18
#define PIN_595_ST 5
#define PIN_595_Q7S 35 // Q7' của IC CUỐI chuỗi

// Nhiều module relay (kể cả trong mô phỏng) kích bằng mức LOW.
// Nếu bạn thấy tất cả echoUs=0 => rất hay là relay chưa hề đóng.
// Thử để 0 (active-HIGH). Nếu sau đó relay chạy sai, đổi về 1.
#define RELAY_ACTIVE_LOW 0

// 8 biến nhị phân 8-bit (mảng 1 chiều 9 phần tử)
// - Index 0: tất cả relay OFF
// - Index 1..8: bật 1 relay tương ứng Q0..Q7
#if RELAY_ACTIVE_LOW
const uint8_t BIT_8[9] = {
  0xFF, // all OFF (active-low)
  0xFE, // Q0 ON
  0xFD, // Q1 ON
  0xFB, // Q2 ON
  0xF7, // Q3 ON
  0xEF, // Q4 ON
  0xDF, // Q5 ON
  0xBF, // Q6 ON
  0x7F, // Q7 ON
};
#else
const uint8_t BIT_8[9] = {
  0b00000000,
  0b00000001,
  0b00000010,
  0b00000100,
  0b00001000,
  0b00010000,
  0b00100000,
  0b01000000,
  0b10000000,
};
#endif
int numbers[15]={0};
unsigned long echoUsArr[15] = {0};

// ===================== WiFi Management =====================
void checkWiFiConnection() {
  unsigned long now = millis();
  
  if (now - lastWiFiCheck >= WIFI_CHECK_INTERVAL) {
    lastWiFiCheck = now;
    
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("[WiFi] Connection lost! Attempting to reconnect...");
      reconnectWiFi();
    } else {
      static unsigned long lastStatusLog = 0;
      if (now - lastStatusLog >= 300000) { // Log every 5 minutes
        lastStatusLog = now;
        Serial.println("[WiFi] Connected - IP: " + WiFi.localIP().toString());
      }
    }
  }
}

void reconnectWiFi() {
  Serial.println("[WiFi] Starting reconnection process...");
  
  WiFi.disconnect();
  delay(1000);
  
  WiFi.mode(WIFI_STA);
  if (!WiFi.config(local_IP, gateway, subnet)) {
    Serial.println("[WiFi] Failed to configure static IP, using DHCP");
  }
  
  WiFi.begin(ssid, password);
  
  unsigned long startAttempt = millis();
  int attempts = 0;
  
  while (WiFi.status() != WL_CONNECTED && (millis() - startAttempt) < WIFI_RECONNECT_TIMEOUT) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("[WiFi] Reconnected successfully!");
    Serial.println("[WiFi] IP: " + WiFi.localIP().toString());
  } else {
    Serial.println();
    Serial.println("[WiFi] Reconnection failed after " + String(WIFI_RECONNECT_TIMEOUT/1000) + "s");
  }
}

// ===================== Send Data to API =====================
void handleGetData() {
  // Trả về dữ liệu theo format cũ mà server expect
  DynamicJsonDocument doc(1024);
  
  // Format - các field ở root level
  doc["success"] = true;
  doc["soIC"] = 2;  // Số IC 74HC595
  doc["totalSensors"] = 15;
  doc["timestamp"] = millis();
  
  // Data array ở root level
  JsonArray dataArray = doc.createNestedArray("data");
  for (int i = 0; i < 15; i++) {
    if (currentDistances[i] == -1) {
      dataArray.add(0);  // Lỗi = trống
    } else {
      dataArray.add(currentDistances[i] <= 15 ? 1 : 0);
    }
  }
  
  // WiFi info
  doc["wifi_connected"] = (WiFi.status() == WL_CONNECTED);
  doc["wifi_rssi"] = WiFi.RSSI();
  
  String response;
  serializeJson(doc, response);
  
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
  server.send(200, "application/json", response);
  
  Serial.println("Server requested GET /data: " + response);
}

void handleDetect() {
  // Lệnh detect lại cảm biến (reset)
  Serial.println("Server requested POST /detect - Rescanning all sensors...");
  
  // Đọc lại tất cả cảm biến
  shiftbyteICs();
  
  DynamicJsonDocument doc(1024);
  doc["success"] = true;
  doc["message"] = "Đã detect lại 15 cảm biến";
  doc["soIC"] = 2;
  doc["totalSensors"] = 15;
  doc["timestamp"] = millis();
  
  // Data array sau khi reset
  JsonArray dataArray = doc.createNestedArray("data");
  for (int i = 0; i < 15; i++) {
    if (currentDistances[i] == -1) {
      dataArray.add(0);
    } else {
      dataArray.add(currentDistances[i] <= 15 ? 1 : 0);
    }
  }
  
  // WiFi info
  doc["wifi_connected"] = (WiFi.status() == WL_CONNECTED);
  doc["wifi_rssi"] = WiFi.RSSI();
  
  String response;
  serializeJson(doc, response);
  
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
  server.send(200, "application/json", response);
  
  Serial.println("Detect completed: " + response);
}

void handleCORS() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
  server.send(200);
}

void handleNotFound() {
  server.send(404, "text/plain", "Not Found");
}
void muxInit() {
  pinMode(MUX_S0, OUTPUT);
  pinMode(MUX_S1, OUTPUT);
  pinMode(MUX_S2, OUTPUT);
  pinMode(MUX_S3, OUTPUT);
}

void muxSelect(uint8_t channel) {
  digitalWrite(MUX_S0, (channel >> 0) & 1);
  digitalWrite(MUX_S1, (channel >> 1) & 1);
  digitalWrite(MUX_S2, (channel >> 2) & 1);
  digitalWrite(MUX_S3, (channel >> 3) & 1);
  delayMicroseconds(10); // Ổn định MUX (tối thiểu)
}

unsigned long readEchoPulseUsMux(uint8_t muxChannel, uint32_t timeoutUs = 30000) {
  muxSelect(muxChannel);
  
  // Gửi xung TRIG
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  // Chờ ECHO lên (chờ tối đa timeoutUs)
  unsigned long timeout = micros() + timeoutUs;
  while (digitalRead(PIN_ECHO) == LOW && micros() < timeout) {
    // Chờ tín hiệu
  }

  if (micros() >= timeout) {
    return 0; // Timeout → không có xung
  }

  unsigned long echoStart = micros();
  timeout = micros() + timeoutUs;

  // Chờ ECHO hạ
  while (digitalRead(PIN_ECHO) == HIGH && micros() < timeout) {
    // Đếm thời gian
  }

  unsigned long echoUs = micros() - echoStart;

  if (micros() >= timeout) {
    return 0; // Timeout
  }

  return echoUs;
}

long readDistanceCmMux(uint8_t muxChannel) {
  unsigned long echoUs = readEchoPulseUsMux(muxChannel, 30000);
  
  if (echoUs == 0) {
    return -1; // Lỗi
  }
  
  long distance = (long)(echoUs * 0.034 / 2);
  return distance;
}

// Hàm đo khoảng cách trực tiếp từ PIN_TRIG=25 và PIN_ECHO=26
long tinhKhoangCachCM() {
  unsigned long duration = 0;
  long distance;

  // Gửi xung TRIG
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  // Chờ ECHO lên (chờ tối đa 30ms)
  unsigned long timeout = micros() + 30000;
  while (digitalRead(PIN_ECHO) == LOW && micros() < timeout) {
    // Chờ tín hiệu
  }

  if (micros() >= timeout) {
    Serial.println("[ERR] ECHO không lên!");
    return -1; // Timeout
  }

  unsigned long echoStart = micros();
  timeout = micros() + 30000;

  // Chờ ECHO hạ
  while (digitalRead(PIN_ECHO) == HIGH && micros() < timeout) {
    // Đếm thời gian
  }

  duration = micros() - echoStart;

  if (micros() >= timeout) {
    Serial.println("[ERR] ECHO không hạ!");
    return -1; // Timeout
  }

  // Tính khoảng cách (cm)
  distance = (long)(duration * 0.034 / 2);

  return distance;
}

void shiftbyteICs()
{
  int a = 1, b = 0, count = 0;
  while (b != 9)
  {
    if (a == 9)
    {
      a = 0;
      b = 1;
    }
    
    // Reset MR
    digitalWrite(PIN_595_ST, LOW);
    digitalWrite(PIN_595_MR, LOW);
    digitalWrite(PIN_595_MR, HIGH);
    digitalWrite(PIN_595_OE, HIGH);
    
    // Shift ra: b trước, rồi a
    shiftOut(PIN_595_DS, PIN_595_SH, MSBFIRST, BIT_8[b]);
    shiftOut(PIN_595_DS, PIN_595_SH, MSBFIRST, BIT_8[a]);
    
    // Latch + Enable output
    digitalWrite(PIN_595_ST, HIGH);
    digitalWrite(PIN_595_OE, LOW);

    // Chờ relay ổn định + delay mỗi sensor 1s
    delay(1000);
    
    // Tính channel từ (a, b): (b==0) ? (a-1) : (7+b)
    uint8_t channel = (b == 0) ? (a - 1) : (7 + b);
    
    if (count < 15) {
      // Đo khoảng cách qua MUX
      long distance = readDistanceCmMux(channel);
      currentDistances[count] = distance;
      Serial.print("Sensor ");
      Serial.print(count + 1);
      Serial.print(" (ch=");
      Serial.print(channel);
      Serial.print("): ");
      Serial.print(distance);
      Serial.println(" cm");
    }
    
    count++;
    if (a != 0) a++;
    if (b != 0) b++;
  }
  digitalWrite(PIN_595_ST, LOW);
}

void setup()
{
  Serial.begin(115200);
  Serial.println("\n\nESP32 Parking Sensors - Pull Model");

  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  digitalWrite(PIN_TRIG, LOW);

  pinMode(PIN_595_DS, OUTPUT);
  pinMode(PIN_595_SH, OUTPUT);
  pinMode(PIN_595_ST, OUTPUT);
  pinMode(PIN_595_OE, OUTPUT);
  pinMode(PIN_595_MR, OUTPUT);

  digitalWrite(PIN_595_DS, LOW);
  digitalWrite(PIN_595_SH, LOW);
  digitalWrite(PIN_595_ST, LOW);

  // Enable output + release reset (active LOW)
  digitalWrite(PIN_595_MR, HIGH);
  digitalWrite(PIN_595_OE, LOW);
  
  // Init MUX
  muxInit();
  
  // ================== SETUP WiFi ==================
  Serial.println("\n[WiFi] Configuring...");
  
  WiFi.mode(WIFI_STA);
  if (!WiFi.config(local_IP, gateway, subnet)) {
    Serial.println("[WiFi] Failed to configure static IP, using DHCP");
  } else {
    Serial.println("[WiFi] Static IP configured: " + local_IP.toString());
  }
  
  WiFi.begin(ssid, password);
  Serial.print("[WiFi] Connecting to: ");
  Serial.println(ssid);
  
  int wifiAttempts = 0;
  while (WiFi.status() != WL_CONNECTED && wifiAttempts < 20) {
    delay(1000);
    Serial.print(".");
    wifiAttempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("[WiFi] Connected successfully!");
    Serial.println("[WiFi] IP: " + WiFi.localIP().toString());
    Serial.println("[WiFi] Signal: " + String(WiFi.RSSI()) + " dBm");
  } else {
    Serial.println();
    Serial.println("[WiFi] Connection FAILED!");
    Serial.println("[WiFi] Will attempt to reconnect in loop");
  }
  
  // Khởi động HTTP Server cho Pull Model
  server.on("/data", HTTP_GET, handleGetData);
  server.on("/detect", HTTP_POST, handleDetect);
  server.on("/data", HTTP_OPTIONS, handleCORS);
  server.on("/detect", HTTP_OPTIONS, handleCORS);
  server.onNotFound(handleNotFound);
  server.begin();
  
  Serial.println("[HTTP] Server started on port 80");
  Serial.println("[HTTP] Endpoints:");
  Serial.println("  GET  http://" + WiFi.localIP().toString() + "/data   - Get sensor data");
  Serial.println("  POST http://" + WiFi.localIP().toString() + "/detect - Rescan sensors");
  
  Serial.println("[System] Ready - Pull model (Backend will poll every 30 minutes)\n");
}

void loop()
{
  // Kiểm tra WiFi connection
  checkWiFiConnection();
  
  // Xử lý HTTP requests từ backend (Pull Model)
  server.handleClient();
  
  // Small delay for system stability
  delay(100);
}
