import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { GripVertical } from 'lucide-react';

const SortableClause = ({ clause }) => {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id: clause.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div ref={setNodeRef} style={style} className="flex items-center mb-2 p-2 bg-gray-50 rounded">
      <div {...attributes} {...listeners} className="cursor-grab mr-2">
        <GripVertical className="h-4 w-4" />
      </div>
      <span className="text-sm">{clause.clause_type.replace('_', ' ')}: {clause.content.substring(0, 50)}...</span>
    </div>
  );
};

export default SortableClause;