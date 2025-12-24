/**
 * index.tsx - Entry point của React application
 * Chức năng: Khởi tạo và render toàn bộ ứng dụng vào DOM
 * File này được webpack sử dụng làm điểm bắt đầu build process
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';     // Global CSS styles
import App from './App';  // Root component của ứng dụng

/**
 * Tạo React root element
 * Sử dụng React 18+ createRoot API thay vì ReactDOM.render cũ
 * Target element: <div id="root"> trong public/index.html
 */
const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

/**
 * Render ứng dụng vào DOM
 * - React.StrictMode: Enable strict mode để detect potential problems
 * - App: Root component chứa toàn bộ ứng dụng
 */
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);