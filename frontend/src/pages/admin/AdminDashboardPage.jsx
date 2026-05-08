import React, { useState, useEffect } from 'react';
import api from '../../api/client';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import Button from '../../components/ui/Button';
import toast from 'react-hot-toast';

const AdminDashboardPage = () => {
  const [metrics, setMetrics] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await api.get('/admin/metrics');
      setMetrics(response.data);
    } catch (error) {
      toast.error('Failed to fetch metrics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  const contractStatusData = [
    { name: 'Open', value: metrics.active_contracts },
    { name: 'In Progress', value: metrics.active_contracts },
    { name: 'Completed', value: metrics.completed_contracts },
    { name: 'Cancelled', value: metrics.cancelled_contracts },
  ];

  const disputeData = [
    { name: 'Open', value: metrics.open_disputes },
    { name: 'Resolved', value: metrics.resolved_disputes },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Admin Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded shadow">
          <h3 className="text-lg font-semibold">Total Contracts</h3>
          <p className="text-2xl font-bold">{metrics.total_contracts}</p>
        </div>
        <div className="bg-white p-6 rounded shadow">
          <h3 className="text-lg font-semibold">Active Disputes</h3>
          <p className={`text-2xl font-bold ${metrics.open_disputes > 0 ? 'text-red-600' : 'text-green-600'}`}>
            {metrics.open_disputes}
          </p>
        </div>
        <div className="bg-white p-6 rounded shadow">
          <h3 className="text-lg font-semibold">Total Commission</h3>
          <p className="text-2xl font-bold">${metrics.total_commission_collected?.toFixed(2)}</p>
        </div>
        <div className="bg-white p-6 rounded shadow">
          <h3 className="text-lg font-semibold">Success Rate</h3>
          <p className="text-2xl font-bold">{(metrics.success_rate * 100)?.toFixed(1)}%</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded shadow">
          <h3 className="text-lg font-semibold mb-4">Contracts by Status</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={contractStatusData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 rounded shadow">
          <h3 className="text-lg font-semibold mb-4">Disputes Overview</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={disputeData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} fill="#8884d8">
                {disputeData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.name === 'Open' ? '#ff7300' : '#00ff00'} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboardPage;