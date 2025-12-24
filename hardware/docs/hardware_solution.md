# 🔧 GIẢI PHÁP HARDWARE CHO CAPACITIVE LOADING

## ⚡ Option 1: Buffer Driver (KHUYẾN NGHỊ)

### Sử dụng 74HC14 Schmitt Trigger Buffer

```
ESP32 Pin 12 ----[74HC14]----+---- HC-SR04 #1 TRIG
                             +---- HC-SR04 #2 TRIG  
                             +---- HC-SR04 #3 TRIG
                             +---- HC-SR04 #4 TRIG
                             +---- HC-SR04 #5 TRIG
                             +---- HC-SR04 #6 TRIG
```

**Ưu điểm:**
- ✅ Drive current: 25mA (đủ cho 6 sensors)
- ✅ Sharp edges: Schmitt trigger tạo signal sắc nét
- ✅ Noise immunity: Giảm nhiễu
- ✅ Cost: ~$0.50

**Wiring:**
```
ESP32 Pin 12 → 74HC14 Pin 1 (Input)
74HC14 Pin 2 (Output) → All 6 HC-SR04 TRIG pins
74HC14 VCC → 5V
74HC14 GND → GND
```

---

## 🎯 Option 2: Individual TRIG Lines

### Dùng 74HC595 để control riêng từng TRIG

```cpp
// Thay vì SHARED TRIG, dùng individual control
#define TRIG_LATCH_PIN 4    // ST_CP của 74HC595 #2
#define TRIG_CLOCK_PIN 2    // SH_CP của 74HC595 #2  
#define TRIG_DATA_PIN 15    // DS của 74HC595 #2

void batTRIG(int qNumber) {
  byte trigPattern = (1 << (qNumber-1));  // Q1=0x01, Q2=0x02, Q3=0x04...
  
  digitalWrite(TRIG_LATCH_PIN, LOW);
  shiftOut(TRIG_DATA_PIN, TRIG_CLOCK_PIN, MSBFIRST, trigPattern);
  digitalWrite(TRIG_LATCH_PIN, HIGH);
}

void tatTatCaTRIG() {
  digitalWrite(TRIG_LATCH_PIN, LOW);
  shiftOut(TRIG_DATA_PIN, TRIG_CLOCK_PIN, MSBFIRST, 0x00);
  digitalWrite(TRIG_LATCH_PIN, HIGH);
}
```

**Ưu điểm:**
- ✅ Mỗi sensor có TRIG riêng → không có capacitive loading
- ✅ Control chính xác timing từng sensor
- ✅ Dùng thêm 1 chip 74HC595

**Nhược điểm:**
- ❌ Cần thêm hardware
- ❌ Phức tạp hơn

---

## 🔋 Option 3: Power Supply Improvement

### Cải thiện nguồn điện

```
5V Supply ----[100µF]----[10µF]----[0.1µF]---- HC-SR04 VCC
              Bulk       Decoupling  Bypass
```

**Thêm capacitors:**
- **100µF electrolytic:** Bulk power reservoir
- **10µF tantalum:** Fast response  
- **0.1µF ceramic:** High frequency bypass (gần từng sensor)

**Ưu điểm:**
- ✅ Ổn định nguồn điện
- ✅ Giảm voltage drop
- ✅ Giảm nhiễu switching

---

## 📐 Option 4: Timing Optimization (Software)

### Extreme timing cho capacitive load

```cpp
float docKhoangCachCM(int echoPin, int qNumber) {
  // CLEAR state cực lâu
  digitalWrite(chanTrig, LOW);
  delay(1000);  // 1 giây để discharge hoàn toàn
  
  // Multiple STRONG pulses
  for (int i = 0; i < 5; i++) {
    digitalWrite(chanTrig, HIGH);
    delayMicroseconds(100);  // Pulse dài 100μs
    digitalWrite(chanTrig, LOW);
    delayMicroseconds(100);  // Nghỉ 100μs
  }
  
  // Settle time CỰC LỚN
  delay(500);
  
  // Timeout CỰC LỚN 
  long thoiGian = pulseIn(echoPin, HIGH, 500000);  // 500ms timeout
  
  if (thoiGian == 0) return -1;
  return thoiGian / 29.1 / 2;
}
```

---

## 🏆 KẾT LUẬN

**Thứ tự ưu tiên:**

1. **74HC14 Buffer** (quickest fix, $0.50)
2. **Individual TRIG với 74HC595** (best long-term)
3. **Power supply capacitors** (supporting improvement)
4. **Extreme software timing** (last resort)

**Khuyến nghị:** Thêm 74HC14 buffer trước, nếu vẫn có vấn đề thì chuyển sang individual TRIG lines.