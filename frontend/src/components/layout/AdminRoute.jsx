import React from 'react';
import { Navigate } from 'react-router-dom';
import { useCurrentRole } from '../../hooks/useCurrentRole';

const AdminRoute = ({ children }) => {
  const role = useCurrentRole();
  return role === 'admin' ? children : <Navigate to="/" />;
};

export default AdminRoute;