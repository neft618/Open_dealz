import React from 'react';

const ClauseEditor = ({ clause, onUpdate }) => (
  <div className="mb-4">
    <label className="block text-sm font-medium text-gray-700 mb-1">
      {clause.clause_type.replace('_', ' ').toUpperCase()}
    </label>
    <textarea
      value={clause.content}
      onChange={(e) => onUpdate(clause.id, e.target.value)}
      className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
      rows={3}
    />
  </div>
);

export default ClauseEditor;