/**
 * types.ts - Định nghĩa các kiểu dữ liệu TypeScript cho hệ thống quản lý bãi đỗ xe
 * Chứa interface và type definitions cho toàn bộ ứng dụng
 */

/**
 * Interface định nghĩa cấu trúc dữ liệu của một thẻ đỗ xe
 * Lưu trữ thông tin về trạng thái và thời gian của xe trong bãi
 */
export interface ParkingCard {
  uid: string;        // Mã định danh duy nhất của thẻ RFID (Unique ID)
  status: number;     // Trạng thái xe: 0 = ngoài bãi, 1 = trong bãi
  entry_time?: string;    // Thời gian vào bãi (ISO format, optional)
  exit_time?: string;     // Thời gian ra khỏi bãi (ISO format, optional)
  created_at: string;     // Thời gian tạo record đầu tiên (ISO format)
  
  /**
   * Thông tin thời gian đỗ xe được tính toán
   * Chỉ có khi xe đã ra khỏi bãi (status = 0 và có exit_time)
   */
  parking_duration?: {
    total_seconds: number;  // Tổng số giây đỗ xe
    hours: number;          // Số giờ đỗ xe  
    minutes: number;        // Số phút đỗ xe (sau khi trừ giờ)
    display: string;        // Chuỗi hiển thị định dạng "X giờ Y phút"
  };
}

/**
 * Interface generic cho tất cả API responses từ backend
 * Sử dụng Generic Type T để linh hoạt với nhiều loại dữ liệu khác nhau
 */
export interface ApiResponse<T> {
  cards?: Record<string, ParkingCard>;  // Object chứa danh sách thẻ (key = UID)
  total?: number;                       // Tổng số record (cho pagination)
  success?: boolean;                    // Trạng thái thành công của API call
  error?: string;                       // Thông báo lỗi (nếu có)
  message?: string;                     // Thông báo từ server
}