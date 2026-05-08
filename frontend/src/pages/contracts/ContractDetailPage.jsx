import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../../api/client';
import { useCurrentRole } from '../../hooks/useCurrentRole';
import EscrowStatus from '../../components/contract/EscrowStatus';
import MilestoneList from '../../components/contract/MilestoneList';
import FileUpload from '../../components/ui/FileUpload';
import Button from '../../components/ui/Button';
import StatusBadge from '../../components/ui/StatusBadge';
import toast from 'react-hot-toast';

const ContractDetailPage = () => {
  const { id } = useParams();
  const [contract, setContract] = useState(null);
  const [milestoneData, setMilestoneData] = useState({ title: '', description: '', amount: '', deadline: '' });
  const currentRole = useCurrentRole();

  useEffect(() => {
    fetchContract();
  }, [id]);

  const fetchContract = async () => {
    try {
      const response = await api.get(`/contracts/${id}`);
      setContract(response.data);
    } catch (error) {
      toast.error('Failed to fetch contract');
    }
  };

  const handleAccept = async () => {
    try {
      await api.post(`/contracts/${id}/accept`);
      toast.success('Work accepted');
      fetchContract();
    } catch (error) {
      toast.error('Failed to accept work');
    }
  };

  const handleReject = async () => {
    try {
      await api.post(`/contracts/${id}/reject`);
      toast.success('Dispute opened');
      fetchContract();
    } catch (error) {
      toast.error('Failed to reject work');
    }
  };

  const handleUploadDeliverable = async (files) => {
    if (files.length === 0) return;
    const formData = new FormData();
    formData.append('file', files[0]);
    formData.append('description', 'Deliverable upload');
    try {
      await api.post(`/contracts/${id}/deliverables`, formData);
      toast.success('Deliverable uploaded');
      fetchContract();
    } catch (error) {
      toast.error('Failed to upload deliverable');
    }
  };

  const handleDownload = async (deliverableId) => {
    try {
      const response = await api.get(`/contracts/${id}/deliverables/${deliverableId}/download`);
      window.open(response.data.url, '_blank');
    } catch (error) {
      toast.error('Failed to download deliverable');
    }
  };

  const handleAddMilestone = async () => {
    try {
      await api.post(`/contracts/${id}/milestones`, milestoneData);
      setMilestoneData({ title: '', description: '', amount: '', deadline: '' });
      fetchContract();
      toast.success('Milestone added');
    } catch (error) {
      toast.error('Failed to add milestone');
    }
  };

  const handleUpdateMilestone = async (milestoneId, status) => {
    try {
      await api.patch(`/contracts/${id}/milestones/${milestoneId}`, { status });
      fetchContract();
      toast.success('Milestone updated');
    } catch (error) {
      toast.error('Failed to update milestone');
    }
  };

  if (!contract) return <div>Loading...</div>;

  const canEditMilestones = currentRole === 'executor' && contract.status === 'in_progress';
  const canAcceptReject = currentRole === 'customer' && contract.status === 'in_progress';
  const canUpload = currentRole === 'executor' && contract.status === 'in_progress';

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Contract Details</h1>
          <StatusBadge status={contract.status} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <EscrowStatus contract={contract} />

        <MilestoneList
          milestones={contract.milestones}
          onUpdateStatus={handleUpdateMilestone}
          onAddMilestone={canEditMilestones ? handleAddMilestone : null}
          canEdit={canEditMilestones}
        />
      </div>

      {canEditMilestones && (
        <div className="mt-8 p-4 bg-gray-50 rounded">
          <h3 className="text-lg font-medium mb-4">Add Milestone</h3>
          <input
            type="text"
            placeholder="Title"
            value={milestoneData.title}
            onChange={(e) => setMilestoneData({ ...milestoneData, title: e.target.value })}
            className="border rounded px-3 py-2 mr-2"
          />
          <input
            type="number"
            placeholder="Amount"
            value={milestoneData.amount}
            onChange={(e) => setMilestoneData({ ...milestoneData, amount: e.target.value })}
            className="border rounded px-3 py-2 mr-2"
          />
          <input
            type="date"
            value={milestoneData.deadline}
            onChange={(e) => setMilestoneData({ ...milestoneData, deadline: e.target.value })}
            className="border rounded px-3 py-2 mr-2"
          />
          <Button onClick={handleAddMilestone}>Add</Button>
        </div>
      )}

      <div className="mt-8">
        <h3 className="text-lg font-medium mb-4">Deliverables</h3>
        {contract.deliverables.map((deliverable) => (
          <div key={deliverable.id} className="border rounded p-4 mb-2 flex justify-between">
            <div>
              <p>{deliverable.file_name}</p>
              <p className="text-sm text-gray-600">{deliverable.description}</p>
            </div>
            <Button onClick={() => handleDownload(deliverable.id)}>Download</Button>
          </div>
        ))}
        {canUpload && <FileUpload onFileSelect={handleUploadDeliverable} />}
      </div>

      {canAcceptReject && (
        <div className="mt-8 flex space-x-4">
          <Button onClick={handleAccept} variant="success">Accept Work</Button>
          <Button onClick={handleReject} variant="danger">Open Dispute</Button>
        </div>
      )}
    </div>
  );
};

export default ContractDetailPage;