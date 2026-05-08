import React from 'react';
import Badge from './Badge';

const StatusBadge = ({ status }) => {
  const statusConfig = {
    open: { variant: 'default', label: 'Open' },
    in_progress: { variant: 'warning', label: 'In Progress' },
    completed: { variant: 'success', label: 'Completed' },
    cancelled: { variant: 'danger', label: 'Cancelled' },
    disputed: { variant: 'danger', label: 'Disputed' },
    draft: { variant: 'default', label: 'Draft' },
    signed: { variant: 'warning', label: 'Signed' },
  };

  const config = statusConfig[status] || { variant: 'default', label: status };
  return <Badge variant={config.variant}>{config.label}</Badge>;
};

export default StatusBadge;