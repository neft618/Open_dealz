import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/client';
import StatusBadge from '../../components/ui/StatusBadge';

const AdminContractsPage = () => {
  const [contracts, setContracts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchContracts();
  }, []);

  const fetchContracts = async () => {
    try {
      const response = await api.get('/admin/contracts');
      setContracts(response.data.contracts);
    } catch (error) {
      console.error('Failed to fetch contracts');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Admin - Contracts</h1>
      <table className="w-full bg-white shadow rounded">
        <thead>
          <tr className="bg-gray-50">
            <th className="px-4 py-2">ID</th>
            <th className="px-4 py-2">Customer</th>
            <th className="px-4 py-2">Executor</th>
            <th className="px-4 py-2">Amount</th>
            <th className="px-4 py-2">Status</th>
            <th className="px-4 py-2">Created</th>
            <th className="px-4 py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {contracts.map((contract) => (
            <tr key={contract.id} className="border-t">
              <td className="px-4 py-2">{contract.id.slice(0, 8)}...</td>
              <td className="px-4 py-2">{contract.customer_id.slice(0, 8)}...</td>
              <td className="px-4 py-2">{contract.executor_id.slice(0, 8)}...</td>
              <td className="px-4 py-2">${contract.total_amount}</td>
              <td className="px-4 py-2"><StatusBadge status={contract.status} /></td>
              <td className="px-4 py-2">{new Date(contract.created_at).toLocaleDateString()}</td>
              <td className="px-4 py-2">
                <Link to={`/contracts/${contract.id}`} className="text-blue-600 hover:underline">View</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AdminContractsPage;