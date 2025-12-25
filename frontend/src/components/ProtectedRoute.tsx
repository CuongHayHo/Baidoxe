/**
 * ProtectedRoute.tsx - Component để bảo vệ routes cần authentication
 */

import React from 'react';
import { Navigate } from 'react-router-dom';
import { parkingApi } from '../api';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'admin' | 'staff';
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requiredRole }) => {
  const isAuthenticated = parkingApi.isAuthenticated();
  const user = parkingApi.getCurrentUser();

  // Nếu không đăng nhập, redirect về login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Nếu cần role cụ thể, kiểm tra role của user
  if (requiredRole && user?.role !== requiredRole) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
