#include <Arduino.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include <WebServer.h>

// ================== CẤU HÌNH WIFI ==================
// Lựa chọn 1: WiFi AP (UNO R4 phát WiFi)
const char* ssid = "UNO-R4-AP";           // Kết nối vào WiFi của UNO R4
const char* password = "12345678";

// Cấu hình IP tĩnh cho ESP32
IPAddress local_IP(192, 168, 4, 5);      // IP tĩnh của ESP32
IPAddress gateway(192, 168, 4, 2);       // Gateway (UNO R4 WiFi)
IPAddress subnet(255, 255, 255, 0);      // Subnet mask

// Lựa chọn 2: Local WiFi (kết nối router)
// const char* ssid = "YOUR_SSID";         // // WiFi SSID của router
// const char* password = "YOUR_PASSWORD";  // // WiFi password
// IPAddress local_IP(192, 168, 1, 100);  // // IP tĩnh của ESP32
// IPAddress gateway(192, 168, 1, 1);     // // Gateway router
// IPAddress subnet(255, 255, 255, 0);    // // Subnet mask

// HTTP Server cho Pull Model
WebServer server(80);

// Dữ liệu hiện tại cho Pull Model
int currentDistances[6] = {-1, -1, -1, -1, -1, -1};

// WiFi reconnection management
unsigned long lastWiFiCheck = 0;
const unsigned long WIFI_CHECK_INTERVAL = 30000; // Check every 30 seconds
const unsigned long WIFI_RECONNECT_TIMEOUT = 10000; // 10s timeout for reconnect

// ================== CHÂN KẾT NỐI ==================
#define chanDuLieu   23   // DS của 74HC595
#define chanClock    18   // SH_CP của 74HC595
#define chanLatch    5    // ST_CP của 74HC595

// 74HC595 điều khiển MOSFET để ON/OFF nguồn VCC của từng sensor
// Q1-Q6 → MOSFET Gate → VCC switching cho từng HY-SRF05
// Chỉ 1 sensor có nguồn VCC tại 1 thời điểm!

// HY-SRF05 nối trực tiếp với ESP32 (TRIG/ECHO chung)
#define chanSensor1  13   // HY-SRF05 #1 (TRIG/ECHO) - VCC từ Q1→MOSFET
#define chanSensor2  14   // HY-SRF05 #2 (TRIG/ECHO) - VCC từ Q2→MOSFET
#define chanSensor3  27   // HY-SRF05 #3 (TRIG/ECHO) - VCC từ Q3→MOSFET
#define chanSensor4  26   // HY-SRF05 #4 (TRIG/ECHO) - VCC từ Q4→MOSFET
#define chanSensor5  25   // HY-SRF05 #5 (TRIG/ECHO) - VCC từ Q5→MOSFET
#define chanSensor6  33   // HY-SRF05 #6 (TRIG/ECHO) - VCC từ Q6→MOSFET

// ================== CẤU HÌNH POWER SWITCHING ==================
byte trangThai = 0;

// Mảng chứa các pin sensor (TRIG/ECHO)
int sensorPins[] = {chanSensor1, chanSensor2, chanSensor3, chanSensor4, chanSensor5, chanSensor6};

// Bit patterns để bật nguồn VCC cho từng sensor qua MOSFET
byte qPatterns[] = {
  0b00000010,  // Q1 HIGH → MOSFET ON → VCC cho sensor #1
  0b00000100,  // Q2 HIGH → MOSFET ON → VCC cho sensor #2  
  0b00001000,  // Q3 HIGH → MOSFET ON → VCC cho sensor #3
  0b00010000,  // Q4 HIGH → MOSFET ON → VCC cho sensor #4
  0b00100000,  // Q5 HIGH → MOSFET ON → VCC cho sensor #5
  0b01000000   // Q6 HIGH → MOSFET ON → VCC cho sensor #6
};

// ================== WIFI RECONNECTION ==================
void checkWiFiConnection() {
  unsigned long now = millis();
  
  // Check WiFi status every WIFI_CHECK_INTERVAL
  if (now - lastWiFiCheck >= WIFI_CHECK_INTERVAL) {
    lastWiFiCheck = now;
    
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("[WiFi] Connection lost! Attempting to reconnect...");
      reconnectWiFi();
    } else {
      // Optionally log connection status
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
  
  // Disconnect first
  WiFi.disconnect();
  delay(1000);
  
  // Reconfigure static IP
  if (!WiFi.config(local_IP, gateway, subnet)) {
    Serial.println("[WiFi] Failed to reconfigure static IP");
  }
  
  // Attempt to reconnect
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
    Serial.println("[WiFi] Attempts: " + String(attempts));
  } else {
    Serial.println();
    Serial.println("[WiFi] Reconnection failed after " + String(WIFI_RECONNECT_TIMEOUT/1000) + "s");
    Serial.println("[WiFi] Will retry in " + String(WIFI_CHECK_INTERVAL/1000) + "s");
  }
}

// ================== POWER CONTROL VIA 74HC595 ==================
void capNhat595() {
  digitalWrite(chanLatch, LOW);
  shiftOut(chanDuLieu, chanClock, MSBFIRST, trangThai);
  digitalWrite(chanLatch, HIGH);
}

void tatTatCaNguon() {
  trangThai = 0b00000000;  // Tất cả MOSFET OFF → không sensor nào có VCC
  capNhat595();
}

void batNguonSensor(int sensorNumber) {
  if (sensorNumber >= 1 && sensorNumber <= 6) {
    trangThai = qPatterns[sensorNumber - 1];  // Chỉ 1 MOSFET ON → 1 sensor có VCC
    capNhat595();
  }
}

// ================== ĐỌC SENSOR VỚI POWER SWITCHING ==================
long docKhoangCachCM(int sensorNumber) {
  if (sensorNumber < 1 || sensorNumber > 6) return -1;
  
  int sensorPin = sensorPins[sensorNumber - 1];
  
  // Đảm bảo sensor đã có nguồn VCC (MOSFET đã ON)
  // Đợi sensor khởi động (HY-SRF05 cần ~200ms sau khi có VCC)
  delay(200);
  
  // Cấu hình chân là OUTPUT để gửi TRIG pulse  
  pinMode(sensorPin, OUTPUT);
  
  // Clear state
  digitalWrite(sensorPin, LOW);
  delayMicroseconds(2);
  
  // Gửi TRIG pulse 10μs
  digitalWrite(sensorPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(sensorPin, LOW);
  
  // Chuyển chân thành INPUT để đọc ECHO
  pinMode(sensorPin, INPUT);
  
  // Đọc thời gian ECHO (timeout 40ms)
  long thoiGian = pulseIn(sensorPin, HIGH, 40000);
  
  if (thoiGian == 0) {
    return -1;  // timeout
  }
  
  return thoiGian / 29.1 / 2;
}

// ================== HTTP SERVER ENDPOINTS (PULL MODEL) ==================
void handleGetData() {
  // Trả về dữ liệu theo format cũ mà server expect
  DynamicJsonDocument doc(1024);
  
  // Format cũ - các field ở root level
  doc["success"] = true;
  doc["soIC"] = 1;  // Số IC 74HC595
  doc["totalSensors"] = 6;
  doc["timestamp"] = millis();
  
  // Data array ở root level (format cũ)
  JsonArray dataArray = doc.createNestedArray("data");
  for (int i = 0; i < 6; i++) {
    if (currentDistances[i] == -1) {
      dataArray.add(0);  // Lỗi = trống
    } else {
      dataArray.add(currentDistances[i] <= 15 ? 1 : 0);
    }
  }
  
  // WiFi info as bonus (không làm ảnh hưởng server)
  doc["wifi_connected"] = (WiFi.status() == WL_CONNECTED);
  doc["wifi_rssi"] = WiFi.RSSI();
  
  String response;
  serializeJson(doc, response);
  
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
  server.send(200, "application/json", response);
  
  // TIMER RESET REMOVED - Backend handles 30-minute polling
  Serial.println("Server requested data: " + response);
}

void handleDetect() {
  // Lệnh detect lại cảm biến (giống như reset)
  Serial.println("Server requested detect/reset");
  
  // Đọc lại tất cả cảm biến
  docTatCaCamBien();
  
  DynamicJsonDocument doc(1024);
  doc["success"] = true;
  doc["message"] = "Đã detect lại 6 cảm biến";
  doc["soIC"] = 1;
  doc["totalSensors"] = 6;
  doc["timestamp"] = millis();
  
  // Data array sau khi reset (format cũ)
  JsonArray dataArray = doc.createNestedArray("data");
  for (int i = 0; i < 6; i++) {
    if (currentDistances[i] == -1) {
      dataArray.add(0);  // Lỗi = trống
    } else {
      dataArray.add(currentDistances[i] <= 15 ? 1 : 0);
    }
  }
  
  // WiFi info as bonus
  doc["wifi_connected"] = (WiFi.status() == WL_CONNECTED);
  doc["wifi_rssi"] = WiFi.RSSI();
  
  String response;
  serializeJson(doc, response);
  
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
  server.send(200, "application/json", response);
  
  Serial.println("Detect completed");
}

void handleNotFound() {
  server.send(404, "text/plain", "Not Found");
}

// Handle CORS preflight
void handleCORS() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
  server.send(200);
}



// ================== ĐỌC TẤT CẢ SENSOR VỚI POWER SWITCHING ==================
void docTatCaCamBien() {
  Serial.println("Starting sensor scan with POWER SWITCHING (6 sensors)...");
  
  for (int s = 1; s <= 6; s++) {
    Serial.print("Reading Sensor #" + String(s) + ": ");
    
    // TẮT TẤT CẢ nguồn trước
    tatTatCaNguon();
    delay(100);  // Đợi tất cả sensor tắt hoàn toàn
    
    // BẬT NGUỒN cho sensor hiện tại qua MOSFET
    batNguonSensor(s);
    Serial.print("VCC ON → ");
    
    // Đọc sensor (đã có delay khởi động bên trong function)
    long kc = docKhoangCachCM(s);
    currentDistances[s-1] = kc;
    
    if (kc == -1) {
      Serial.println("TIMEOUT");
    } else {
      Serial.println(String(kc) + "cm");
    }
    
    // TẮT nguồn sensor này (tiết kiệm điện)
    tatTatCaNguon();
    delay(50);  // Delay nhỏ giữa các sensor
  }
  
  // Đảm bảo tất cả sensor đã tắt
  tatTatCaNguon();
  Serial.println("Power switching scan completed - Only 1 sensor powered at a time!");
}



// ================== SETUP ==================
void setup() {
  Serial.begin(115200);
  Serial.println("ESP32 Parking Sensors");
  
  // Cấu hình chân 74HC595
  pinMode(chanDuLieu, OUTPUT);
  pinMode(chanClock, OUTPUT);
  pinMode(chanLatch, OUTPUT);
  
  // Cấu hình chân sensor pins (sẽ chuyển đổi OUTPUT/INPUT khi đọc)
  for (int i = 0; i < 6; i++) {
    pinMode(sensorPins[i], OUTPUT);
    digitalWrite(sensorPins[i], LOW);
  }
  
  // Tắt tất cả nguồn sensor ban đầu (tất cả MOSFET OFF)
  tatTatCaNguon();
  delay(500);
  
  // Cấu hình IP tĩnh trước khi kết nối WiFi
  if (!WiFi.config(local_IP, gateway, subnet)) {
    Serial.println("Failed to configure static IP");
  }
  
  // Kết nối WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  Serial.println("Configuring static IP: " + local_IP.toString());
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(1000);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("WiFi connected successfully!");
    Serial.println("ESP32 IP: " + WiFi.localIP().toString() + " (Static)");
    Serial.println("Gateway: " + WiFi.gatewayIP().toString());
    Serial.println("Subnet: " + WiFi.subnetMask().toString());
  } else {
    Serial.println();
    Serial.println("WiFi connection FAILED!");
    Serial.println("Check: UNO R4 WiFi AP is running");
    Serial.println("Expected network: UNO-R4-AP");
    Serial.println("Static IP config: " + local_IP.toString());
  }
  
  // Khởi động HTTP Server cho Pull Model
  server.on("/data", HTTP_GET, handleGetData);
  server.on("/detect", HTTP_POST, handleDetect);
  server.on("/data", HTTP_OPTIONS, handleCORS);
  server.on("/detect", HTTP_OPTIONS, handleCORS);
  server.onNotFound(handleNotFound);
  server.begin();
  
  Serial.println("HTTP Server started on port 80");
  Serial.println("Endpoints:");
  Serial.println("  GET  http://" + WiFi.localIP().toString() + "/data   - Lấy dữ liệu cảm biến");
  Serial.println("  POST http://" + WiFi.localIP().toString() + "/detect - Reset/detect lại cảm biến");
  
  Serial.println("Ready - Pull model only (Backend will poll every 30 minutes)");
}

// ================== LOOP ==================
void loop() {
  // Check and maintain WiFi connection
  checkWiFiConnection();
  
  // Xử lý HTTP requests (Pull Model only)
  server.handleClient();
  
  // Small delay for system stability
  delay(100);
}