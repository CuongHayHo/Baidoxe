/**
 * LoginPage.tsx - Authentication login page for Electron desktop app
 * Handles user login with JWT token storage (no React Router)
 */

import React, { useState } from 'react';
import '../styles/LoginPage.css';

interface LoginPageProps {
  onLoginSuccess: (token: string, role?: string) => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      console.log('📡 Sending login request...');
      const response = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          password,
        }),
      });

      console.log('📊 Response status:', response.status);
      const data = await response.json();
      console.log('📦 Response data:', data);

      if (!response.ok) {
        setError(data.message || 'Đăng nhập thất bại');
        return;
      }

      console.log('✅ Login successful, token:', data.token);
      // Store token in localStorage
      localStorage.setItem('authToken', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));

      // Call callback to update parent component (App.tsx) with token and role
      onLoginSuccess(data.token, data.user?.role);
    } catch (err: any) {
      console.error('🔴 Login error:', err);
      setError(err.message || 'Lỗi kết nối đến server');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    console.log('🎮 Demo login clicked - using admin/admin123');
    setUsername('admin');
    setPassword('admin123');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: 'admin',
          password: 'admin123',
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.message || 'Đăng nhập thất bại');
        return;
      }

      console.log('✅ Demo login successful');
      // Store token in localStorage
      localStorage.setItem('authToken', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));

      // Call callback to update parent component with token and role
      onLoginSuccess(data.token, data.user?.role);
    } catch (err: any) {
      console.error('🔴 Demo login error:', err);
      setError(err.message || 'Lỗi kết nối đến server');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>🅿️ Parking Management System</h1>
          <p>Hệ thống quản lý bãi đỗ xe thông minh</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && <div className="login-error">{error}</div>}

          <div className="form-group">
            <label htmlFor="username">Tên tài khoản</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Nhập tên tài khoản"
              disabled={loading}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Mật khẩu</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Nhập mật khẩu"
              disabled={loading}
              required
            />
          </div>

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
          </button>
        </form>

      </div>
    </div>
  );
};

export default LoginPage;
