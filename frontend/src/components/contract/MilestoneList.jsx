import React from 'react';
import StatusBadge from '../ui/StatusBadge';
import Button from '../ui/Button';

const MilestoneList = ({ milestones, onUpdateStatus, onAddMilestone, canEdit }) => (
  <div>
    <h3 className="text-lg font-medium mb-4">Milestones</h3>
    {milestones.map((milestone) => (
      <div key={milestone.id} className="border rounded p-4 mb-2">
        <div className="flex justify-between items-center">
          <div>
            <h4 className="font-medium">{milestone.title}</h4>
            <p className="text-sm text-gray-600">{milestone.description}</p>
            <p className="text-sm">Amount: ${milestone.amount}</p>
            <StatusBadge status={milestone.status} />
          </div>
          {canEdit && (
            <div className="space-x-2">
              <Button onClick={() => onUpdateStatus(milestone.id, 'in_progress')} size="sm">Start</Button>
              <Button onClick={() => onUpdateStatus(milestone.id, 'approved')} size="sm">Approve</Button>
              <Button onClick={() => onUpdateStatus(milestone.id, 'rejected')} size="sm" variant="danger">Reject</Button>
            </div>
          )}
        </div>
      </div>
    ))}
    {canEdit && <Button onClick={onAddMilestone}>Add Milestone</Button>}
  </div>
);

export default MilestoneList;