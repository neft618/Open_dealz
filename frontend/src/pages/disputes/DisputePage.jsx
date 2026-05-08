import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../../api/client';
import { useCurrentRole } from '../../hooks/useCurrentRole';
import FileUpload from '../../components/ui/FileUpload';
import Button from '../../components/ui/Button';
import StatusBadge from '../../components/ui/StatusBadge';
import Modal from '../../components/ui/Modal';
import toast from 'react-hot-toast';

const DisputePage = () => {
  const { id } = useParams();
  const [dispute, setDispute] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [files, setFiles] = useState([]);
  const [showResolveModal, setShowResolveModal] = useState(false);
  const [resolution, setResolution] = useState({ resolution: 'executor', comment: '' });
  const currentRole = useCurrentRole();

  useEffect(() => {
    fetchDispute();
  }, [id]);

  const fetchDispute = async () => {
    try {
      const response = await api.get(`/disputes/${id}`);
      setDispute(response.data);
      setMessages(response.data.messages);
    } catch (error) {
      toast.error('Failed to fetch dispute');
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;
    const formData = new FormData();
    formData.append('content', newMessage);
    if (files.length > 0) {
      formData.append('file', files[0]);
    }
    try {
      await api.post(`/disputes/${id}/messages`, formData);
      setNewMessage('');
      setFiles([]);
      fetchDispute();
      toast.success('Message sent');
    } catch (error) {
      toast.error('Failed to send message');
    }
  };

  const handleResolve = async () => {
    try {
      await api.post(`/disputes/${id}/resolve`, resolution);
      setShowResolveModal(false);
      fetchDispute();
      toast.success('Dispute resolved');
    } catch (error) {
      toast.error('Failed to resolve dispute');
    }
  };

  const handleSetUnderReview = async () => {
    try {
      await api.patch(`/disputes/${id}/status`, { status: 'under_review' });
      fetchDispute();
      toast.success('Status updated');
    } catch (error) {
      toast.error('Failed to update status');
    }
  };

  if (!dispute) return <div>Loading...</div>;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Dispute Details</h1>
        <StatusBadge status={dispute.status} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <div>
          <h2 className="text-xl font-semibold mb-4">Contract Summary</h2>
          <div className="bg-gray-50 p-4 rounded">
            <p>Amount: ${dispute.contract?.total_amount}</p>
            <p>Customer: {dispute.contract?.customer_id}</p>
            <p>Executor: {dispute.contract?.executor_id}</p>
          </div>
        </div>

        {currentRole === 'admin' && (
          <div>
            <h2 className="text-xl font-semibold mb-4">Admin Panel</h2>
            <Button onClick={handleSetUnderReview} className="mr-2">Set Under Review</Button>
            <Button onClick={() => setShowResolveModal(true)}>Resolve Dispute</Button>
          </div>
        )}
      </div>

      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Messages</h2>
        <div className="space-y-4">
          {messages.map((msg) => (
            <div key={msg.id} className="border rounded p-4">
              <p className="font-medium">{msg.author_id}</p>
              <p>{msg.content}</p>
              {msg.file_url && (
                <a href={msg.file_url} target="_blank" rel="noopener noreferrer" className="text-blue-600">
                  View Attachment
                </a>
              )}
              <p className="text-sm text-gray-500">{new Date(msg.created_at).toLocaleString()}</p>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-4">Send Message</h2>
        <textarea
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Type your message..."
          className="w-full p-2 border rounded mb-4"
          rows={4}
        />
        <FileUpload onFileSelect={setFiles} />
        <Button onClick={handleSendMessage} className="mt-4">Send Message</Button>
      </div>

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

export default DisputePage;