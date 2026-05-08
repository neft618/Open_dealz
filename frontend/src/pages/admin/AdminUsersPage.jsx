import React, { useState, useEffect } from 'react';
import api from '../../api/client';
import StatusBadge from '../../components/ui/StatusBadge';
import Button from '../../components/ui/Button';

const AdminUsersPage = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await api.get('/admin/users');
      setUsers(response.data.users);
    } catch (error) {
      console.error('Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (userId) => {
    try {
      await api.patch(`/admin/users/${userId}/verify`);
      fetchUsers();
    } catch (error) {
      console.error('Failed to verify user');
    }
  };

  const handleDeactivate = async (userId) => {
    try {
      await api.patch(`/admin/users/${userId}/deactivate`);
      fetchUsers();
    } catch (error) {
      console.error('Failed to deactivate user');
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Admin - Users</h1>
      <table className="w-full bg-white shadow rounded">
        <thead>
          <tr className="bg-gray-50">
            <th className="px-4 py-2">ID</th>
            <th className="px-4 py-2">Email</th>
            <th className="px-4 py-2">Role</th>
            <th className="px-4 py-2">Verified</th>
            <th className="px-4 py-2">Active</th>
            <th className="px-4 py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id} className="border-t">
              <td className="px-4 py-2">{user.id.slice(0, 8)}...</td>
              <td className="px-4 py-2">{user.email}</td>
              <td className="px-4 py-2">{user.role}</td>
              <td className="px-4 py-2">{user.is_verified ? 'Yes' : 'No'}</td>
              <td className="px-4 py-2">{user.is_active ? 'Yes' : 'No'}</td>
              <td className="px-4 py-2">
                {!user.is_verified && <Button onClick={() => handleVerify(user.id)} className="mr-2">Verify</Button>}
                {user.is_active && <Button onClick={() => handleDeactivate(user.id)} variant="danger">Deactivate</Button>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AdminUsersPage;