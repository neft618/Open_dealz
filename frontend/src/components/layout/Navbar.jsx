import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useCurrentRole } from '../../hooks/useCurrentRole';
import { useNotificationStore } from '../../store/notificationStore';
import { Bell, User, Settings } from 'lucide-react';

const Navbar = () => {
  const { user, logout } = useAuth();
  const currentRole = useCurrentRole();
  const { unreadCount } = useNotificationStore();

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold text-gray-900">
              OpenDealz
            </Link>
          </div>
          <div className="flex items-center space-x-4">
            {user && (
              <>
                <select
                  value={currentRole}
                  onChange={(e) => {/* Switch role */}}
                  className="border rounded px-2 py-1"
                >
                  <option value="customer">Customer</option>
                  <option value="executor">Executor</option>
                  {user.role === 'admin' && <option value="admin">Admin</option>}
                </select>
                <Link to="/notifications" className="relative">
                  <Bell className="h-6 w-6" />
                  {unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                      {unreadCount}
                    </span>
                  )}
                </Link>
                <Link to="/profile">
                  <User className="h-6 w-6" />
                </Link>
                <button onClick={logout} className="text-gray-700 hover:text-gray-900">
                  Logout
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;