/**
 * API Client - Kết nối frontend với backend server
 * 
 * Chức năng chính:
 * - Smart detection để tự động phát hiện backend URL
 * - Fallback system khi connection thất bại
 * - Interceptors để log và retry requests
 * - Type-safe methods cho tất cả API endpoints
 */

import axios from 'axios';
import { ParkingCard, ApiResponse } from './types';

/**
 * Hàm thông minh để phát hiện URL backend
 * - Development: sử dụng localhost:5000
 * - Production: sử dụng cùng IP với frontend + port 5000
 */
const getApiBaseUrl = () => {
  // Kiểm tra nếu đang chạy development (localhost frontend)
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:5000'; // Thử localhost trước
  }
  
  // Nếu truy cập qua IP mạng, sử dụng cùng IP cho backend
  return `http://${window.location.hostname}:5000`;
};

/**
 * Danh sách URL fallback khi URL chính thất bại
 * Thử theo thứ tự ưu tiên từ trên xuống
 */
const FALLBACK_URLS = [
  'http://192.168.4.3:5000',  // IP backend đã được detect
  'http://127.0.0.1:5000',    // Local loopback
  'http://localhost:5000'     // Local hostname
];

// URL backend được phát hiện tự động
const API_BASE_URL = getApiBaseUrl();

/**
 * Tạo axios instance với cấu hình cơ bản
 * - Timeout: 10 giây
 * - Content-Type: JSON
 * - BaseURL: Tự động detect
 */
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request Interceptor - Ghi log mọi request để debug
 */
api.interceptors.request.use(request => {
  console.log('🚀 API Request:', `${API_BASE_URL}${request.url}`, request.method?.toUpperCase());
  return request;
});

/**
 * Response Interceptor - Xử lý response và retry logic
 * - Log thành công/thất bại
 * - Tự động thử fallback URLs khi connection lỗi
 */
api.interceptors.response.use(
  response => {
    console.log('✅ API Response:', response.config.url, response.status);
    return response;
  },
  async error => {
    console.error('❌ API Error:', error.config?.url, error.message);
    
    // Thử fallback URLs khi URL chính thất bại
    if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
      console.log('🔄 Đang thử các URL fallback...');
      
      for (const fallbackUrl of FALLBACK_URLS) {
        if (fallbackUrl === API_BASE_URL) continue; // Bỏ qua nếu trùng với URL hiện tại
        
        try {
          console.log(`🧪 Đang thử: ${fallbackUrl}`);
          const retryResponse = await axios({
            ...error.config,
            baseURL: fallbackUrl
          });
          console.log(`✅ Fallback thành công: ${fallbackUrl}`);
          return retryResponse;
        } catch (fallbackError) {
          console.log(`❌ Fallback thất bại: ${fallbackUrl}`);
        }
      }
    }
    
    return Promise.reject(error);
  }
);

/**
 * API Client Object - Tập hợp tất cả methods để giao tiếp với backend
 * Mỗi method tương ứng với 1 endpoint và có error handling
 */
export const parkingApi = {
  /**
   * Lấy danh sách tất cả thẻ từ server
   * @returns Record object với key là UID thẻ
   */
  getCards: async (): Promise<Record<string, ParkingCard>> => {
    const response = await api.get<{success: boolean, cards: ParkingCard[], count: number}>('/api/cards/');
    const cardsObject: Record<string, ParkingCard> = {};
    if (response.data.cards && Array.isArray(response.data.cards)) {
      response.data.cards.forEach(card => {
        cardsObject[card.uid] = card;
      });
    }
    return cardsObject;
  },

  /**
   * Thêm thẻ mới vào hệ thống
   * @param uid - ID duy nhất của thẻ
   * @param status - Trạng thái: 0=active, 1=parked  
   */
  addCard: async (uid: string, status: number = 0): Promise<boolean> => {
    const statusMap = { 0: 'active', 1: 'parked' };
    const apiStatus = statusMap[status as keyof typeof statusMap] || 'active';
    
    const response = await api.post<ApiResponse<any>>('/api/cards/', {
      id: uid,
      name: `Thẻ ${uid}`,
      status: apiStatus,
    });
    return response.data.success === true;
  },

  /**
   * Xóa thẻ khỏi hệ thống
   * @param uid - ID của thẻ cần xóa
   */
  deleteCard: async (uid: string): Promise<boolean> => {
    const response = await api.delete<ApiResponse<any>>(`/api/cards/${uid}`);
    return response.data.success === true;
  },

  /**
   * Reload dữ liệu thẻ từ file JSON
   * @returns Thông báo kết quả reload
   */
  reload: async (): Promise<string> => {
    const response = await api.post<ApiResponse<any>>('/api/reload');
    return response.data.message || 'Reloaded';
  },

  /**
   * Lấy danh sách thẻ lạ (chưa được đăng ký)
   * @returns Mảng các thẻ lạ
   */
  getUnknownCards: async (): Promise<any[]> => {
    const response = await api.get<{unknown_cards: any[]}>('/api/cards/unknown');
    return response.data.unknown_cards || [];
  },

  /**
   * Xóa tất cả thẻ lạ
   * @returns True nếu thành công
   */
  clearUnknownCards: async (): Promise<boolean> => {
    const response = await api.delete<ApiResponse<any>>('/api/cards/unknown');
    return response.data.success === true;
  },

  /**
   * Xóa 1 thẻ lạ cụ thể
   * @param uid - ID thẻ lạ cần xóa
   */
  removeUnknownCard: async (uid: string): Promise<boolean> => {
    const response = await api.delete<ApiResponse<any>>(`/api/cards/unknown/${uid}`);
    return response.data.success === true;
  },

  /**
   * Lấy thống kê tổng quan hệ thống
   * @returns Object chứa các metrics
   */
  getStatistics: async (): Promise<any> => {
    const response = await api.get<any>('/api/cards/statistics');
    return response.data;
  },

  /**
   * Lấy thông tin vị trí đỗ xe
   * @param endpoint - Custom endpoint (optional)
   */
  getParkingSlots: async (endpoint: string = '/api/parking-slots'): Promise<any> => {
    const response = await api.get<any>(endpoint);
    return response.data;
  },

  /**
   * Reset tất cả vị trí đỗ xe về trạng thái trống
   * @returns Thông báo kết quả reset
   */
  resetParkingSlots: async (): Promise<string> => {
    const response = await api.post<any>('/api/parking-slots/reset');
    return response.data.message || 'Reset completed';
  },

  /**
   * Lấy log hoạt động với các filter
   * @param params - Object chứa các tham số filter
   */
  getLogs: async (params?: {
    action?: string;    // Filter theo loại hành động
    card_id?: string;   // Filter theo ID thẻ
    limit?: number;     // Số lượng records tối đa
    offset?: number;    // Bỏ qua bao nhiêu records đầu
  }): Promise<any> => {
    const queryParams = new URLSearchParams();
    if (params?.action) queryParams.append('action', params.action);
    if (params?.card_id) queryParams.append('card_id', params.card_id);
    queryParams.append('limit', (params?.limit || 50).toString());
    queryParams.append('offset', (params?.offset || 0).toString());

    const response = await api.get<any>(`/api/cards/logs?${queryParams}`);
    return response.data;
  }
};

export default parkingApi;