import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import api from '../../api/client';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import toast from 'react-hot-toast';

const schema = z.object({
  title: z.string().min(1),
  description: z.string().min(1),
  budget: z.number().positive(),
  deadline: z.string(),
});

const CreateOrderPage = () => {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
  });
  const navigate = useNavigate();

  const onSubmit = async (data) => {
    try {
      const response = await api.post('/orders', data);
      navigate(`/orders/${response.data.id}`);
      toast.success('Order created');
    } catch (error) {
      toast.error('Failed to create order');
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-md">
      <h1 className="text-2xl font-bold mb-6">Create Order</h1>
      <form onSubmit={handleSubmit(onSubmit)}>
        <Input label="Title" {...register('title')} error={errors.title?.message} />
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea
            {...register('description')}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={4}
          />
          {errors.description && <p className="text-red-500 text-sm mt-1">{errors.description.message}</p>}
        </div>
        <Input label="Budget" type="number" step="0.01" {...register('budget', { valueAsNumber: true })} error={errors.budget?.message} />
        <Input label="Deadline" type="date" {...register('deadline')} error={errors.deadline?.message} />
        <Button type="submit">Create Order</Button>
      </form>
    </div>
  );
};

export default CreateOrderPage;