# 3.2.3 Thiết kế mạch phần cứng ESP32

## Thành phần

- **ESP32 DevKit V4** – điều khiển chính của phần xử lý và hiển thị.
- **IC 74HC595** – mở rộng công xuất để điều khiển power switching tuần tự cho 15 cảm biến.
- **CD74HC4067 (16:1 MUX)** – chọn 1 trong 16 kênh ECHO từ các cảm biến.
- **15 cảm biến HC-SR04** – theo dõi trạng thái tuần tự 15 vị trí đỗ xe.
- **Tăng khueết dạt IRF9540N + 2N3904** – cấp nguồn VCC tuần tự cho từng cảm biến thông qua 74HC595.

## Bảng 3-2 Các thiết bị đầu nối với ESP32

| Linh kiện | ESP32 Pin | Mô tả |
|-----------|-----------|-------|
| HC-SR04 – TRIG (Trigger) | GPIO 25 | Gửi xung kích hoạt cảm biến |
| HC-SR04 – ECHO (Echo) | GPIO 26 | Nhận xung phản hồi từ cảm biến |
| CD74HC4067 – S0 | GPIO 12 | Bit 0 chọn kênh MUX |
| CD74HC4067 – S1 | GPIO 13 | Bit 1 chọn kênh MUX |
| CD74HC4067 – S2 | GPIO 14 | Bit 2 chọn kênh MUX |
| CD74HC4067 – S3 | GPIO 27 | Bit 3 chọn kênh MUX |
| 74HC595 – DS (Data) | GPIO 23 | Dữ liệu nối tiếp (SPI) |
| 74HC595 – SH_CP (Shift Clock) | GPIO 18 | Xung shift clock (SPI) |
| 74HC595 – ST_CP (Latch) | GPIO 5 | Xung latch |
| 74HC595 – OE (Output Enable) | GPIO 33 | Cho phép output (Active LOW) |
| 74HC595 – MR (Master Reset) | GPIO 32 | Reset (Active LOW) |

## Nguyên lý

- **ESP32 đọc dữ liệu từ 15 cảm biến HC-SR04 để xác định vị trí đỗ xe tương ứng.**
- **Thông tin được hiển thị qua:**
  - Giao diện Web (vị trí đỗ xe).
  - Nguồn của HC-SR04 được điều khiển bởi 74HC595 và mạch MOSFET.
  - MUX được sử dụng để chọn kênh ECHO của từng cảm biến.
  - Pull Model: Backend yêu cầu `/data` để lấy trạng thái hoặc `/detect` để quét lại cảm biến.

