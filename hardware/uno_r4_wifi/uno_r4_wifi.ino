/*
 * BÃI ĐỖ XE THÔNG MINH - ARDUINO UNO R4 WiFi
 * Dual RFID + Servo Barriers + WiFi AP
 */

#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>
#include <WiFiS3.h> // Arduino UNO R4 WiFi library
#include <string.h>

// RFID RC522 - DUAL READERS
// IN Reader
#define SS_PIN_IN 10
#define RST_PIN_IN 9
MFRC522 rfidIn(SS_PIN_IN, RST_PIN_IN);

// OUT Reader
#define SS_PIN_OUT 7
#define RST_PIN_OUT 8
MFRC522 rfidOut(SS_PIN_OUT, RST_PIN_OUT);

// SERVO MOTORS
Servo servoIn, servoOut;
#define SERVO_IN_PIN 5
#define SERVO_OUT_PIN 6

// Góc servo (có thể cần điều chỉnh theo hardware)
#define SERVO_CLOSED_ANGLE 0 // Đóng barrier
#define SERVO_OPEN_ANGLE 90  // Mở barrier

// ULTRASONIC SENSORS
#define TRIG_IN 3
#define ECHO_IN 4
#define TRIG_OUT 2
#define ECHO_OUT A0

// WIFI CONFIG
// Lựa chọn 1: WiFi AP (UNO R4 phát WiFi)
const char *apSsid = "UNO-R4-AP";
const char *apPassword = "12345678";
const int apChannel = 1;
String serverIP = "192.168.4.3"; // IP của Python server
uint16_t serverPort = 5000;

// Lựa chọn 2: Local WiFi (kết nối router)
// const char* apSsid = "YOUR_SSID";        // // WiFi SSID của router
// const char* apPassword = "YOUR_PASSWORD"; // // WiFi password
// String serverIP = "192.168.1.50";      // // IP backend trên local WiFi
// uint16_t serverPort = 5000;

// WEB SERVER cho health check
WiFiServer webServer(80);

//
// NON-BLOCKING STATE MACHINE - XỬ LÝ SONG SONG 2 BARRIERS
//
/**
 * Các trạng thái của barrier (không blocking):
 * - IDLE: Barrier đóng, sẵn sàng nhận lệnh
 * - OPENING: Servo đang mở (0.5s)
 * - WAITING_VEHICLE: Chờ phát hiện xe vào
 * - VEHICLE_PRESENT: Đã phát hiện xe, chờ xe đi qua
 * - CLOSING: Servo đang đóng (0.5s)
 * - TIMEOUT_CLOSING: Đóng do timeout an toàn
 */
enum BarrierState
{
  IDLE,            // Đóng, sẵn sàng
  OPENING,         // Đang mở servo
  WAITING_VEHICLE, // Chờ phát hiện xe
  VEHICLE_PRESENT, // Xe đã vào, chờ xe đi qua
  CLOSING,         // Đang đóng servo
  TIMEOUT_CLOSING  // Đóng do timeout
};

/**
 * Cấu trúc quản lý trạng thái mỗi barrier
 * Mỗi barrier (IN/OUT) có state machine riêng để xử lý song song
 */
struct BarrierControl
{
  BarrierState state;           // Trạng thái hiện tại
  unsigned long stateStartTime; // Thời điểm bắt đầu state
  int presentCount;             // Số lần liên tiếp phát hiện xe
  int absentCount;              // Số lần liên tiếp không phát hiện xe
  bool vehicleDetected;         // Flag xe đã được phát hiện
  Servo *servo;                 // Con trỏ tới servo motor
  int trigPin;                  // Chân TRIG của ultrasonic
  int echoPin;                  // Chân ECHO của ultrasonic
  String name;                  // Tên barrier ("IN" hoặc "OUT")
};

// Khởi tạo 2 barrier controllers
BarrierControl barrierIn;  // Controller cho barrier vào
BarrierControl barrierOut; // Controller cho barrier ra

//
// CẤU HÌNH HỆ THỐNG
//
const int ULTRA_THRESHOLD_CM = 10;             // Ngưỡng phát hiện xe (10cm)
const int ULTRA_STABLE_COUNT = 3;              // Số lần đo ổn định (chống nhiễu)
const unsigned long SERVO_MAX_OPEN_MS = 30000; // Timeout mở tối đa (30 giây)
const unsigned long RFID_COOLDOWN_MS = 200;    // Cooldown giữa các lần đọc RFID (giảm từ 1000ms)

//
// BIẾN TOÀN CỤC - QUẢN LÝ RFID
//
unsigned long lastRfidTime = 0; // Thời điểm đọc RFID cuối cùng
String lastUID = "";            // UID thẻ vừa đọc (để tránh spam)

//
// KHAI BÁO CÁC HÀM CHÍNH
//
void initBarrier(BarrierControl &barrier, Servo *servo, int trigPin, int echoPin, const String &name);
void updateBarrier(BarrierControl &barrier);                       // Cập nhật state machine
long readDistanceCM(int trigPin, int echoPin);                     // Đọc khoảng cách ultrasonic
void openBarrier(BarrierControl &barrier);                         // Mở barrier
void closeBarrier(BarrierControl &barrier);                        // Đóng barrier
String readRFID(MFRC522 &reader, const String &readerName);        // Đọc RFID card
void sendRFIDToServer(const String &uid, const String &direction); // Gửi RFID lên server
bool containsNoCase(const String &haystack, const char *needle);   // Tìm chuỗi không phân biệt hoa/thường

void setup()
{
  Serial.begin(9600);
  Serial.println("System Starting...");

  // Khởi tạo RFID
  SPI.begin();
  rfidIn.PCD_Init();
  rfidOut.PCD_Init();

  // Khởi tạo Servo
  servoIn.attach(SERVO_IN_PIN);
  servoOut.attach(SERVO_OUT_PIN);

  // Test servo (đảm bảo hoạt động đúng)
  servoIn.write(SERVO_CLOSED_ANGLE);
  servoOut.write(SERVO_CLOSED_ANGLE);
  delay(500);
  servoIn.write(SERVO_OPEN_ANGLE);
  servoOut.write(SERVO_OPEN_ANGLE);
  delay(500);
  servoIn.write(SERVO_CLOSED_ANGLE);
  servoOut.write(SERVO_CLOSED_ANGLE);
  delay(500);

  // Khởi tạo Ultrasonic
  pinMode(TRIG_IN, OUTPUT);
  pinMode(ECHO_IN, INPUT);
  pinMode(TRIG_OUT, OUTPUT);
  pinMode(ECHO_OUT, INPUT);

  // Khởi tạo Barriers
  initBarrier(barrierIn, &servoIn, TRIG_IN, ECHO_IN, "IN");
  initBarrier(barrierOut, &servoOut, TRIG_OUT, ECHO_OUT, "OUT");
  closeBarrier(barrierIn);
  closeBarrier(barrierOut);

  // ===== Lựa chọn 1: WiFi AP (UNO R4 phát WiFi) =====
  IPAddress staticIP(192, 168, 4, 2); // IP tĩnh cho UNO R4
  IPAddress gateway(192, 168, 4, 2);  // Gateway = chính UNO R4 (vì UNO là AP)
  IPAddress subnet(255, 255, 255, 0); // Subnet mask

  // Đặt IP tĩnh trước khi khởi tạo AP
  WiFi.config(staticIP, gateway, subnet);

  if (WiFi.beginAP(apSsid, apPassword, apChannel) == WL_AP_LISTENING)
  {
    Serial.println("WiFi AP: " + String(apSsid));
    Serial.println("IP: " + WiFi.localIP().toString());

    // Khởi động web server port 80
    webServer.begin();
    Serial.println("Web server started");

    // ===== Lựa chọn 2: Local WiFi (kết nối router) =====
    // Serial.println("🔌 Khởi tạo WiFi...");
    //
    // // Cấu hình IP tĩnh cho local WiFi
    // IPAddress staticIP(192, 168, 1, 101);     // // IP UNO R4 trong local WiFi
    // IPAddress gateway(192, 168, 1, 1);        // // Gateway router
    // IPAddress subnet(255, 255, 255, 0);       // // Subnet mask
    //
    // WiFi.config(staticIP, gateway, subnet);
    // WiFi.begin(apSsid, apPassword);
    //
    // int attempts = 0;
    // while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    //   delay(500);
    //   Serial.print(".");
    //   attempts++;
    // }
    //
    // if (WiFi.status() == WL_CONNECTED) {
    //   Serial.println("WiFi connected: " + String(apSsid));
    //   Serial.println("IP: " + WiFi.localIP().toString());

    // Khởi động web server port 80
    webServer.begin();
    Serial.println("Web server started");
  }
  else
  {
    Serial.println("WiFi AP Failed");
  }

  Serial.println("System Ready");
}

//
// HÀM KHỞI TẠO BARRIER STATE MACHINE
//
/**
 * Khởi tạo cấu hình cho một barrier controller
 * @param barrier: Reference tới barrier cần khởi tạo
 * @param servo: Con trỏ tới servo motor điều khiển barrier
 * @param trigPin: Chân TRIG của cảm biến siêu âm
 * @param echoPin: Chân ECHO của cảm biến siêu âm
 * @param name: Tên barrier ("IN" hoặc "OUT")
 */
void initBarrier(BarrierControl &barrier, Servo *servo, int trigPin, int echoPin, const String &name)
{
  barrier.state = IDLE;              // Bắt đầu ở trạng thái đóng
  barrier.stateStartTime = millis(); // Ghi nhận thời gian bắt đầu
  barrier.presentCount = 0;          // Reset bộ đếm phát hiện xe
  barrier.absentCount = 0;           // Reset bộ đếm mất xe
  barrier.vehicleDetected = false;   // Chưa phát hiện xe
  barrier.servo = servo;             // Gán servo motor
  barrier.trigPin = trigPin;         // Gán chân TRIG
  barrier.echoPin = echoPin;         // Gán chân ECHO
  barrier.name = name;               // Gán tên barrier
}

// Vòng lặp chính - xử lý non-blocking
void loop()
{
  //  SONG SONG: Cập nhật cả 2 barrier mỗi loop
  updateBarrier(barrierIn);
  updateBarrier(barrierOut);

  //  DUAL RFID: Kiểm tra cả 2 readers với cooldown riêng biệt
  static unsigned long lastRfidTimeIN = 0;
  static unsigned long lastRfidTimeOUT = 0;
  static String lastUID_IN = "";
  static String lastUID_OUT = "";

  // Kiểm tra RFID IN reader (mỗi 100ms)
  if (millis() - lastRfidTimeIN > (RFID_COOLDOWN_MS / 2))
  {
    String uidIn = readRFID(rfidIn, "IN");
    if (uidIn != "" && uidIn != lastUID_IN)
    {
      lastUID_IN = uidIn;
      lastRfidTimeIN = millis();
      Serial.print("📡 UID IN: ");
      Serial.println(uidIn);
      sendRFIDToServer(uidIn, "IN");
    }
    // Reset lastUID_IN sau 3s để cho phép đọc lại
    if (millis() - lastRfidTimeIN > 3000)
    {
      lastUID_IN = "";
    }
  }

  // Kiểm tra RFID OUT reader (mỗi 100ms, độc lập với IN)
  if (millis() - lastRfidTimeOUT > (RFID_COOLDOWN_MS / 2))
  {
    String uidOut = readRFID(rfidOut, "OUT");
    if (uidOut != "" && uidOut != lastUID_OUT)
    {
      lastUID_OUT = uidOut;
      lastRfidTimeOUT = millis();
      Serial.print("📡 UID OUT: ");
      Serial.println(uidOut);
      sendRFIDToServer(uidOut, "OUT");
    }
    // Reset lastUID_OUT sau 3s để cho phép đọc lại
    if (millis() - lastRfidTimeOUT > 3000)
    {
      lastUID_OUT = "";
    }
  }

  // 🌐 Web server: Xử lý HTTP requests đơn giản
  WiFiClient client = webServer.available();
  if (client)
  {
    String request = "";
    while (client.connected() && client.available())
    {
      char c = client.read();
      request += c;
      if (request.endsWith("\r\n\r\n"))
        break; // End of HTTP header
    }

    // Simple health check response
    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: application/json");
    client.println("Connection: close");
    client.println();
    client.println("{\"status\":\"ok\",\"device\":\"UNO R4 WiFi\",\"ip\":\"192.168.4.2\"}");
    client.stop();
  }

  delay(10); // Main loop delay nhỏ để responsive (giảm từ 50ms)
}

//
// HÀM CẬP NHẬT STATE MACHINE CHO BARRIER (NON-BLOCKING)
//
/**
 * Cập nhật state machine cho barrier theo trạng thái hiện tại
 * Thay thế hàm vehiclePassed() blocking cũ bằng state machine non-blocking
 *
 * Các trạng thái:
 * - IDLE: Barrier đóng, chờ lệnh mở
 * - WAITING_VEHICLE: Barrier đã mở, đang chờ xe đi qua
 * - VEHICLE_PASSING: Phát hiện xe, đợi xe đi qua hoàn toàn
 * - CLOSING: Đóng barrier sau khi xe đi qua
 *
 * @param barrier: Reference tới barrier cần cập nhật
 */
void updateBarrier(BarrierControl &barrier)
{
  unsigned long currentTime = millis();
  unsigned long elapsed = currentTime - barrier.stateStartTime;

  // Đọc cảm biến siêu âm để phát hiện xe
  long distance = readDistanceCM(barrier.trigPin, barrier.echoPin);
  bool isPresent = (distance > 0 && distance <= ULTRA_THRESHOLD_CM);

  switch (barrier.state)
  {

  case IDLE:
    // Barrier đóng - chờ lệnh mở từ server qua openBarrier()
    // Không làm gì, chỉ đợi openBarrier() được gọi khi có thẻ hợp lệ
    break;

  case OPENING:
    // Barrier đang mở - chuyển sang WAITING_VEHICLE sau khi servo mở hoàn toàn
    if (elapsed > 2000)
    { // 2s để servo mở hoàn toàn (90 độ)
      barrier.state = WAITING_VEHICLE;
      barrier.stateStartTime = currentTime;
      barrier.presentCount = 0;
      barrier.vehicleDetected = false;
    }
    break;

  case WAITING_VEHICLE:
    // Barrier đã mở - chờ phát hiện xe đi vào vùng cảm biến
    if (isPresent)
    {
      barrier.presentCount++;
      if (barrier.presentCount >= ULTRA_STABLE_COUNT)
      {
        barrier.state = VEHICLE_PRESENT;
        barrier.stateStartTime = currentTime;
        barrier.absentCount = 0;
        barrier.vehicleDetected = true;
      }
    }
    else
    {
      barrier.presentCount = 0; // Reset nếu không phát hiện
    }

    // Timeout: Tự động đóng nếu không có xe trong thời gian dài
    if (elapsed > SERVO_MAX_OPEN_MS)
    {
      Serial.println("Timeout barrier " + barrier.name);
      barrier.state = TIMEOUT_CLOSING;
      barrier.stateStartTime = currentTime;
      barrier.servo->write(SERVO_CLOSED_ANGLE); // Đóng barrier
    }
    break;

  case VEHICLE_PRESENT:
    // Đã phát hiện xe - chờ xe đi qua hoàn toàn khỏi cảm biến
    if (!isPresent)
    {
      barrier.absentCount++;
      if (barrier.absentCount >= ULTRA_STABLE_COUNT)
      {
        // AN TOÀN: Kiểm tra lần cuối trước khi đóng
        delay(200); // Đợi thêm 200ms
        long finalCheck = readDistanceCM(barrier.trigPin, barrier.echoPin);

        if (finalCheck > ULTRA_THRESHOLD_CM || finalCheck == -1)
        {
          // An toàn để đóng
          barrier.state = CLOSING;
          barrier.stateStartTime = currentTime;
          barrier.servo->write(SERVO_CLOSED_ANGLE); // Đóng barrier
        }
        else
        {
          // Vẫn có vật cản - không đóng
          barrier.absentCount = 0; // Reset để tiếp tục kiểm tra
        }
      }
    }
    else
    {
      barrier.absentCount = 0; // Reset nếu xe vẫn còn trong vùng
    }

    // Timeout: Đóng bắt buộc nếu xe ở lại quá lâu (khẩn cấp)
    if (elapsed > SERVO_MAX_OPEN_MS)
    {
      Serial.println("Emergency timeout barrier " + barrier.name);
      barrier.state = TIMEOUT_CLOSING;
      barrier.stateStartTime = currentTime;
      barrier.servo->write(SERVO_CLOSED_ANGLE); // Đóng barrier khẩn cấp
    }
    break;

  case CLOSING:
  case TIMEOUT_CLOSING:
    // Barrier đang đóng - chờ servo đóng hoàn toàn rồi chuyển về IDLE
    if (elapsed > 2000)
    { // 2s để servo đóng hoàn toàn (0 độ)
      barrier.state = IDLE;
      barrier.stateStartTime = currentTime;
    }
    break;
  }
}

//
// CÁC HÀM ĐIỀU KHIỂN BARRIER
//

/**
 * Mở barrier nếu đang ở trạng thái IDLE
 * @param barrier: Barrier cần mở
 */
void openBarrier(BarrierControl &barrier)
{
  if (barrier.state == IDLE)
  {
    barrier.servo->write(SERVO_OPEN_ANGLE); // Mở barrier (90°)
    delay(100);                             // Cho servo thời gian bắt đầu
    barrier.state = OPENING;
    barrier.stateStartTime = millis();
    Serial.println("Opening barrier " + barrier.name);
  }
  else if (barrier.state == CLOSING || barrier.state == TIMEOUT_CLOSING)
  {
    // Nếu đang đóng, force mở lại
    barrier.servo->write(SERVO_OPEN_ANGLE);
    delay(100);
    barrier.state = OPENING;
    barrier.stateStartTime = millis();
    Serial.println("Force opening barrier " + barrier.name);
  }
  else
  {
    // Force reset về IDLE nếu cần (emergency)
    if (barrier.state == VEHICLE_PRESENT || barrier.state == WAITING_VEHICLE)
    {
      barrier.state = IDLE;
      openBarrier(barrier); // Recursive call
    }
  }
}

/**
 * Đóng barrier ngay lập tức (emergency)
 * @param barrier: Barrier cần đóng
 */
void closeBarrier(BarrierControl &barrier)
{
  barrier.servo->write(SERVO_CLOSED_ANGLE); // Đóng barrier (0°)
  delay(100);                               // Cho servo thời gian bắt đầu
  barrier.state = CLOSING;
  barrier.stateStartTime = millis();
  Serial.println("Closing barrier " + barrier.name);
}

//
// HÀM ĐỌC CẢM BIẾN SIÊU ÂM
//
/**
 * Đọc khoảng cách từ cảm biến siêu âm HC-SR04
 * @param trigPin: Chân TRIG
 * @param echoPin: Chân ECHO
 * @return: Khoảng cách tính bằng cm, -1 nếu timeout
 */
long readDistanceCM(int trigPin, int echoPin)
{
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  long duration = pulseIn(echoPin, HIGH, 20000); // timeout 20ms
  if (duration == 0)
    return -1;                 // timeout
  return duration * 0.034 / 2; // Chuyển đổi thành cm
}

//
// CÁC HÀM XỬ LÝ DUAL RFID READERS
//
/**
 * Đọc thẻ RFID từ reader cụ thể
 * @param reader: Reference tới MFRC522 reader
 * @param readerName: Tên reader ("IN" hoặc "OUT") để debug
 * @return: UID của thẻ dạng hex string, "" nếu không có thẻ
 */
String readRFID(MFRC522 &reader, const String &readerName)
{
  if (!reader.PICC_IsNewCardPresent())
    return "";
  if (!reader.PICC_ReadCardSerial())
    return "";

  String uid = "";
  for (byte i = 0; i < reader.uid.size; i++)
  {
    if (reader.uid.uidByte[i] < 0x10)
      uid += "0";
    uid += String(reader.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();

  reader.PICC_HaltA();      // Dừng giao tiếp với thẻ
  reader.PCD_StopCrypto1(); // Dừng mã hóa

  return uid;
}

//
// HÀM GIAO TIẾP VỚI PYTHON SERVER
//
/**
 * Gửi thông tin RFID tới Python server để kiểm tra thẻ
 * @param uid: UID của thẻ RFID
 * @param direction: Hướng di chuyển ("IN" hoặc "OUT")
 */
void sendRFIDToServer(const String &uid, const String &direction)
{
  WiFiClient client;

  Serial.println("Sending RFID - Direction: " + direction);
  Serial.println("UID: " + uid);

  if (client.connect(serverIP.c_str(), serverPort))
  {
    // Tạo JSON body theo format backend expect
    String jsonBody = "{\"card_id\":\"" + uid + "\",\"direction\":\"" + direction + "\",\"timestamp\":\"\"}";

    // Tạo HTTP POST request tới /api/cards/scan
    String httpRequest = "POST /api/cards/scan HTTP/1.1\r\n";
    httpRequest += "Host: " + serverIP + "\r\n";
    httpRequest += "Content-Type: application/json\r\n";
    httpRequest += "Content-Length: " + String(jsonBody.length()) + "\r\n";
    httpRequest += "Connection: close\r\n\r\n";
    httpRequest += jsonBody;

    client.print(httpRequest);

    // Đọc response với timeout ngắn để tránh blocking
    String response = "";
    unsigned long timeout = millis() + 1000; // 1s timeout

    while (client.connected() && millis() < timeout)
    {
      if (client.available())
      {
        response += client.readString();
        break;
      }
      delay(10);
    }
    client.stop();

    if (response.length() > 0)
    {
      // Trích xuất body từ HTTP response
      int bodyStart = response.indexOf("\r\n\r\n");
      String body = "";
      if (bodyStart > 0)
      {
        body = response.substring(bodyStart + 4);
        body.trim(); // Loại bỏ whitespace
      }
      else
      {
        body = response; // Fallback nếu không tìm được header
      }

      // LOGIC KIỂM TRA JSON RESPONSE từ /api/cards/scan
      // Ưu tiên kiểm tra JSON success thay vì HTTP status
      if (body.indexOf("\"success\":true") >= 0 || body.indexOf("\"success\": true") >= 0)
      {
        Serial.println("API response: Success");

        // Logic ĐÚNG: Mở barrier dựa trên reader nào phát hiện thẻ (direction)
        if (direction == "IN")
        {
          Serial.println("Opening IN barrier");
          openBarrier(barrierIn);
        }
        else if (direction == "OUT")
        {
          Serial.println("Opening OUT barrier");
          openBarrier(barrierOut);
        }
      }
      else if (body.indexOf("\"success\":false") >= 0 || body.indexOf("\"success\": false") >= 0)
      {
        Serial.println("API response: Failed");
      }
      else if (response.indexOf("HTTP/1.1 500") >= 0)
      {
        Serial.println("API error: 500");
      }
      else
      {
        Serial.println("API error: Unknown");
      }
    }
    else
    {
      Serial.println("API timeout");
    }
  }
  else
  {
    Serial.println("Connection failed");
  }
}

//
// CÁC HÀM HỖ TRỢ (HELPER FUNCTIONS)
//
/**
 * Tìm kiếm chuỗi con trong chuỗi lớn (không phân biệt hoa thường)
 * @param haystack: Chuỗi cần tìm kiếm trong đó
 * @param needle: Chuỗi con cần tìm
 * @return: true nếu tìm thấy, false nếu không
 */
bool containsNoCase(const String &haystack, const char *needle)
{
  size_t nLen = strlen(needle);
  if (nLen == 0)
    return true;
  for (size_t i = 0; i + nLen <= haystack.length(); ++i)
  {
    bool match = true;
    for (size_t j = 0; j < nLen; ++j)
    {
      char c1 = haystack.charAt(i + j);
      char c2 = needle[j];
      // Chuyển về chữ thường để so sánh
      if (c1 >= 'A' && c1 <= 'Z')
        c1 = c1 - 'A' + 'a';
      if (c2 >= 'A' && c2 <= 'Z')
        c2 = c2 - 'A' + 'a';
      if (c1 != c2)
      {
        match = false;
        break;
      }
    }
    if (match)
      return true;
  }
  return false;
}