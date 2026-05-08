import React, { useState, useEffect } from 'react';
import api from '../../api/client';
import { Check } from 'lucide-react';

const AdminAuditLogPage = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      const response = await api.get('/admin/audit-log');
      setLogs(response.data.logs);
    } catch (error) {
      console.error('Failed to fetch audit logs');
    } finally {
      setLoading(false);
    }
  };

  const verifyHash = (txHash) => {
    // Placeholder for hash verification
    return true; // Assume verified for demo
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Admin - Audit Log</h1>
      <table className="w-full bg-white shadow rounded">
        <thead>
          <tr className="bg-gray-50">
            <th className="px-4 py-2">Entity</th>
            <th className="px-4 py-2">Action</th>
            <th className="px-4 py-2">User</th>
            <th className="px-4 py-2">Timestamp</th>
            <th className="px-4 py-2">TX Hash</th>
            <th className="px-4 py-2">Verified</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id} className="border-t">
              <td className="px-4 py-2">{log.entity_type}</td>
              <td className="px-4 py-2">{log.action}</td>
              <td className="px-4 py-2">{log.user_id?.slice(0, 8) || 'System'}...</td>
              <td className="px-4 py-2">{new Date(log.created_at).toLocaleString()}</td>
              <td className="px-4 py-2">
                <span className="font-mono text-sm">{log.tx_hash.slice(0, 16)}...</span>
                <button onClick={() => navigator.clipboard.writeText(log.tx_hash)} className="ml-2 text-blue-600">Copy</button>
              </td>
              <td className="px-4 py-2">
                {verifyHash(log.tx_hash) && <Check className="text-green-600" />}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AdminAuditLogPage;