import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/layout/Navbar';
import ProtectedRoute from './components/layout/ProtectedRoute';
import AdminRoute from './components/layout/AdminRoute';
import Toast from './components/ui/Toast';

// Auth Pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';

// Order Pages
import OrdersListPage from './pages/orders/OrdersListPage';
import CreateOrderPage from './pages/orders/CreateOrderPage';
import OrderDetailPage from './pages/orders/OrderDetailPage';

// Contract Pages
import ContractBuilderPage from './pages/contracts/ContractBuilderPage';
import ContractDetailPage from './pages/contracts/ContractDetailPage';

// Dispute Pages
import DisputePage from './pages/disputes/DisputePage';

// Profile Pages
import ProfilePage from './pages/profile/ProfilePage';
import PublicProfilePage from './pages/profile/PublicProfilePage';

// Admin Pages
import AdminDashboardPage from './pages/admin/AdminDashboardPage';
import AdminContractsPage from './pages/admin/AdminContractsPage';
import AdminDisputesPage from './pages/admin/AdminDisputesPage';
import AdminUsersPage from './pages/admin/AdminUsersPage';
import AdminAuditLogPage from './pages/admin/AdminAuditLogPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="overflow-x-hidden w-full max-w-full">
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Protected Routes */}
            <Route path="/" element={<ProtectedRoute><OrdersListPage /></ProtectedRoute>} />
            <Route path="/orders" element={<ProtectedRoute><OrdersListPage /></ProtectedRoute>} />
            <Route path="/orders/create" element={<ProtectedRoute><CreateOrderPage /></ProtectedRoute>} />
            <Route path="/orders/:id" element={<ProtectedRoute><OrderDetailPage /></ProtectedRoute>} />
            <Route path="/contracts/:id" element={<ProtectedRoute><ContractDetailPage /></ProtectedRoute>} />
            <Route path="/contracts/:id/builder" element={<ProtectedRoute><ContractBuilderPage /></ProtectedRoute>} />
            <Route path="/disputes/:id" element={<ProtectedRoute><DisputePage /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
            <Route path="/users/:id" element={<ProtectedRoute><PublicProfilePage /></ProtectedRoute>} />

            {/* Admin Routes */}
            <Route path="/admin" element={<AdminRoute><AdminDashboardPage /></AdminRoute>} />
            <Route path="/admin/contracts" element={<AdminRoute><AdminContractsPage /></AdminRoute>} />
            <Route path="/admin/disputes" element={<AdminRoute><AdminDisputesPage /></AdminRoute>} />
            <Route path="/admin/users" element={<AdminRoute><AdminUsersPage /></AdminRoute>} />
            <Route path="/admin/audit-log" element={<AdminRoute><AdminAuditLogPage /></AdminRoute>} />

            {/* Default redirect */}
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </main>
        <Toast />
      </div>
    </Router>
  );
}

export default App;