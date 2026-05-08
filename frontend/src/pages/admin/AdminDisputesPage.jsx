import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/client';
import StatusBadge from '../../components/ui/StatusBadge';
import Button from '../../components/ui/Button';
import Modal from '../../components/ui/Modal';

const AdminDisputesPage = () => {
  const [disputes, setDisputes] = useState([]);
  const [selectedDispute, setSelectedDispute] = useState(null);
  const [showResolveModal, setShowResolveModal] = useState(false);
  const [resolution, setResolution] = useState({ resolution: 'executor', comment: '' });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDisputes();
  }, []);

  const fetchDisputes = async () => {
    try {
      const response = await api.get('/admin/disputes');
      setDisputes(response.data.disputes);
    } catch (error) {
      console.error('Failed to fetch disputes');
    } finally {
      setLoading(false);
    }
  };

  const handleResolve = async () => {
    try {
      await api.post(`/disputes/${selectedDispute.id}/resolve`, resolution);
      setShowResolveModal(false);
      fetchDisputes();
    } catch (error) {
      console.error('Failed to resolve dispute');
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Admin - Disputes</h1>
      <table className="w-full bg-white shadow rounded">
        <thead>
          <tr className="bg-gray-50">
            <th className="px-4 py-2">ID</th>
            <th className="px-4 py-2">Contract</th>
            <th className="px-4 py-2">Initiated By</th>
            <th className="px-4 py-2">Status</th>
            <th className="px-4 py-2">Created</th>
            <th className="px-4 py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {disputes.map((dispute) => (
            <tr key={dispute.id} className="border-t">
              <td className="px-4 py-2">{dispute.id.slice(0, 8)}...</td>
              <td className="px-4 py-2">{dispute.contract_id.slice(0, 8)}...</td>
              <td className="px-4 py-2">{dispute.initiated_by_id.slice(0, 8)}...</td>
              <td className="px-4 py-2"><StatusBadge status={dispute.status} /></td>
              <td className="px-4 py-2">{new Date(dispute.created_at).toLocaleDateString()}</td>
              <td className="px-4 py-2">
                <Link to={`/disputes/${dispute.id}`} className="text-blue-600 hover:underline mr-2">View</Link>
                <Button onClick={() => { setSelectedDispute(dispute); setShowResolveModal(true); }}>Resolve</Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <Modal isOpen={showResolveModal} onClose={() => setShowResolveModal(false)}>
        <h2 className="text-xl font-bold mb-4">Resolve Dispute</h2>
        <select
          value={resolution.resolution}
          onChange={(e) => setResolution({ ...resolution, resolution: e.target.value })}
          className="border rounded px-3 py-2 mb-4 w-full"
        >
          <option value="executor">Executor Wins</option>
          <option value="customer">Customer Wins</option>
          <option value="shared">Split 50/50</option>
        </select>
        <textarea
          value={resolution.comment}
          onChange={(e) => setResolution({ ...resolution, comment: e.target.value })}
          placeholder="Resolution comment..."
          className="w-full p-2 border rounded mb-4"
          rows={4}
        />
        <Button onClick={handleResolve}>Resolve</Button>
      </Modal>
    </div>
  );
};

export default AdminDisputesPage;