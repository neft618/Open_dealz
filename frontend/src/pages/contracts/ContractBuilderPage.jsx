import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { DndContext, closestCenter } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import api from '../../api/client';
import ClauseEditor from '../../components/contract/ClauseEditor';
import SortableClause from '../../components/contract/SortableClause';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import toast from 'react-hot-toast';

const steps = [
  { id: 1, title: 'Subject' },
  { id: 2, title: 'Timeline' },
  { id: 3, title: 'Payment' },
  { id: 4, title: 'Termination' },
  { id: 5, title: 'Mandatory Clauses' },
  { id: 6, title: 'Review & Sign' },
];

const ContractBuilderPage = () => {
  const { id } = useParams();
  const [contract, setContract] = useState(null);
  const [currentStep, setCurrentStep] = useState(1);
  const [clauses, setClauses] = useState([]);
  const [paymentType, setPaymentType] = useState('fixed');
  const [totalAmount, setTotalAmount] = useState('');
  const [confirmRead, setConfirmRead] = useState(false);
  const [agreeTerms, setAgreeTerms] = useState(false);

  useEffect(() => {
    fetchContract();
  }, [id]);

  const fetchContract = async () => {
    try {
      const response = await api.get(`/contracts/${id}`);
      setContract(response.data);
      setClauses(response.data.clauses);
      setPaymentType(response.data.payment_type);
      setTotalAmount(response.data.total_amount);
    } catch (error) {
      toast.error('Failed to fetch contract');
    }
  };

  const updateClause = (clauseId, content) => {
    setClauses(clauses.map(c => c.id === clauseId ? { ...c, content } : c));
  };

  const handleDragEnd = (event) => {
    const { active, over } = event;
    if (active.id !== over.id) {
      const oldIndex = clauses.findIndex(c => c.id === active.id);
      const newIndex = clauses.findIndex(c => c.id === over.id);
      const newClauses = [...clauses];
      const [removed] = newClauses.splice(oldIndex, 1);
      newClauses.splice(newIndex, 0, removed);
      setClauses(newClauses.map((c, i) => ({ ...c, position: i })));
    }
  };

  const saveClauses = async () => {
    try {
      await api.patch(`/contracts/${id}/clauses`, clauses.map(c => ({ id: c.id, content: c.content, position: c.position })));
      toast.success('Clauses updated');
    } catch (error) {
      toast.error('Failed to update clauses');
    }
  };

  const signContract = async () => {
    if (!confirmRead || !agreeTerms) {
      toast.error('Please confirm reading and agree to terms');
      return;
    }
    try {
      await api.post(`/contracts/${id}/sign`);
      toast.success('Contract signed');
      fetchContract();
    } catch (error) {
      toast.error('Failed to sign contract');
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <ClauseEditor
            clause={clauses.find(c => c.clause_type === 'subject_description')}
            onUpdate={updateClause}
          />
        );
      case 2:
        return <div>Timeline picker here</div>;
      case 3:
        return (
          <div>
            <select value={paymentType} onChange={(e) => setPaymentType(e.target.value)}>
              <option value="fixed">Fixed</option>
              <option value="hourly">Hourly</option>
              <option value="milestone">Milestone</option>
            </select>
            <Input label="Total Amount" value={totalAmount} onChange={(e) => setTotalAmount(e.target.value)} />
          </div>
        );
      case 4:
        return <ClauseEditor clause={clauses.find(c => c.clause_type === 'termination_conditions')} onUpdate={updateClause} />;
      case 5:
        return (
          <div>
            <ClauseEditor clause={clauses.find(c => c.clause_type === 'result_review_period')} onUpdate={updateClause} />
            <ClauseEditor clause={clauses.find(c => c.clause_type === 'refund_policy')} onUpdate={updateClause} />
            <ClauseEditor clause={clauses.find(c => c.clause_type === 'platform_commission')} onUpdate={updateClause} />
            <ClauseEditor clause={clauses.find(c => c.clause_type === 'ip_rights')} onUpdate={updateClause} />
            <ClauseEditor clause={clauses.find(c => c.clause_type === 'confidentiality')} onUpdate={updateClause} />
          </div>
        );
      case 6:
        return (
          <div>
            <DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
              <SortableContext items={clauses.map(c => c.id)} strategy={verticalListSortingStrategy}>
                {clauses.map((clause) => (
                  <SortableClause key={clause.id} clause={clause} />
                ))}
              </SortableContext>
            </DndContext>
            <Button onClick={saveClauses} className="mt-4">Reorder Clauses</Button>
            <div className="mt-4">
              <label>
                <input type="checkbox" checked={confirmRead} onChange={(e) => setConfirmRead(e.target.checked)} />
                I confirm I have read all contract terms
              </label>
              <br />
              <label>
                <input type="checkbox" checked={agreeTerms} onChange={(e) => setAgreeTerms(e.target.checked)} />
                I agree to platform terms of service
              </label>
            </div>
            <Button onClick={signContract} disabled={!confirmRead || !agreeTerms}>Sign Contract</Button>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex justify-between mb-4">
          {steps.map((step) => (
            <div key={step.id} className={`flex-1 text-center ${currentStep >= step.id ? 'text-blue-600' : 'text-gray-400'}`}>
              {step.title}
            </div>
          ))}
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${(currentStep / steps.length) * 100}%` }}></div>
        </div>
      </div>

      <div className="mb-8">
        {renderStep()}
      </div>

      <div className="flex justify-between">
        <Button onClick={() => setCurrentStep(currentStep - 1)} disabled={currentStep === 1}>
          Previous
        </Button>
        <Button onClick={() => setCurrentStep(currentStep + 1)} disabled={currentStep === steps.length}>
          Next
        </Button>
      </div>
    </div>
  );
};

export default ContractBuilderPage;