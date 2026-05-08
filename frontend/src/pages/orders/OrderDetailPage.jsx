import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../../api/client';
import { useCurrentRole } from '../../hooks/useCurrentRole';
import Button from '../../components/ui/Button';
import StatusBadge from '../../components/ui/StatusBadge';
import Modal from '../../components/ui/Modal';
import Input from '../../components/ui/Input';
import toast from 'react-hot-toast';

const OrderDetailPage = () => {
  const { id } = useParams();
  const [order, setOrder] = useState(null);
  const [applications, setApplications] = useState([]);
  const [showApplyModal, setShowApplyModal] = useState(false);
  const [applyData, setApplyData] = useState({ cover_letter: '', proposed_price: '' });
  const currentRole = useCurrentRole();

  useEffect(() => {
    fetchOrder();
    if (currentRole === 'customer') {
      fetchApplications();
    }
  }, [id, currentRole]);

  const fetchOrder = async () => {
    try {
      const response = await api.get(`/orders/${id}`);
      setOrder(response.data);
    } catch (error) {
      toast.error('Failed to fetch order');
    }
  };

  const fetchApplications = async () => {
    try {
      const response = await api.get(`/orders/${id}/applications`);
      setApplications(response.data);
    } catch (error) {
      toast.error('Failed to fetch applications');
    }
  };

  const handleApply = async () => {
    try {
      await api.post(`/orders/${id}/applications`, applyData);
      setShowApplyModal(false);
      toast.success('Application submitted');
    } catch (error) {
      toast.error('Failed to apply');
    }
  };

  const handleAccept = async (appId) => {
    try {
      await api.post(`/orders/${id}/applications/${appId}/accept`);
      fetchOrder();
      toast.success('Application accepted');
    } catch (error) {
      toast.error('Failed to accept application');
    }
  };

  if (!order) return <div>Loading...</div>;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="bg-white p-6 rounded shadow">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-2xl font-bold">{order.title}</h1>
            <p className="text-gray-600">{order.description}</p>
            <p>Budget: ${order.budget}</p>
            <p>Deadline: {new Date(order.deadline).toLocaleDateString()}</p>
          </div>
          <StatusBadge status={order.status} />
        </div>

        {currentRole === 'customer' && order.status === 'open' && (
          <div>
            <h2 className="text-xl font-semibold mb-4">Applications</h2>
            {applications.map((app) => (
              <div key={app.id} className="border rounded p-4 mb-2">
                <p>Executor: {app.executor_id}</p>
                <p>Cover Letter: {app.cover_letter}</p>
                <p>Proposed Price: ${app.proposed_price}</p>
                <Button onClick={() => handleAccept(app.id)}>Accept</Button>
              </div>
            ))}
          </div>
        )}

        {currentRole === 'executor' && order.status === 'open' && (
          <Button onClick={() => setShowApplyModal(true)}>Apply to Order</Button>
        )}
      </div>

      <Modal isOpen={showApplyModal} onClose={() => setShowApplyModal(false)}>
        <h2 className="text-xl font-bold mb-4">Apply to Order</h2>
        <textarea
          placeholder="Cover letter"
          value={applyData.cover_letter}
          onChange={(e) => setApplyData({ ...applyData, cover_letter: e.target.value })}
          className="w-full p-2 border rounded mb-4"
          rows={4}
        />
        <Input
          type="number"
          placeholder="Proposed price"
          value={applyData.proposed_price}
          onChange={(e) => setApplyData({ ...applyData, proposed_price: e.target.value })}
        />
        <Button onClick={handleApply}>Submit Application</Button>
      </Modal>
    </div>
  );
};

export default OrderDetailPage;