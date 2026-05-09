import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate, Link } from 'react-router-dom';
import api from '../../api/client';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import toast from 'react-hot-toast';

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
  confirmPassword: z.string(),
  fullName: z.string(),
  role: z.enum(['customer', 'executor']),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

const RegisterPage = () => {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
  });
  const navigate = useNavigate();

  const onSubmit = async (data) => {
    try {
      await api.post('/auth/register', data);
      navigate('/login');
      toast.success('Registration successful');
    } catch (error) {
      toast.error('Registration failed');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-charcoal-900 via-blue-900 to-cyan-900 flex items-center justify-center p-8">
      <div className="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
        {/* Left side - Hero content */}
        <div className="space-y-8">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-cyan-400 rounded-full flex items-center justify-center text-charcoal-900 font-bold text-2xl">O</div>
            <h1 className="text-4xl font-bold text-white">OpenDealz</h1>
          </div>
          <div className="space-y-4">
            <h2 className="text-5xl font-extrabold text-white leading-tight">
              Join the Platform<br />
              <span className="text-cyan-400">Build Trust</span>
            </h2>
            <p className="text-xl text-gray-300 max-w-md">
              Create your account and start building secure contracts with freelancers worldwide.
            </p>
          </div>
          <div className="flex space-x-4">
            <div className="bg-cyan-400/20 border border-cyan-400/30 rounded-lg p-4">
              <div className="text-cyan-400 font-semibold">Free</div>
              <div className="text-gray-300 text-sm">Registration</div>
            </div>
            <div className="bg-cyan-400/20 border border-cyan-400/30 rounded-lg p-4">
              <div className="text-cyan-400 font-semibold">Verified</div>
              <div className="text-gray-300 text-sm">Profiles</div>
            </div>
          </div>
        </div>

        {/* Right side - Register form */}
        <div className="bg-charcoal-800/50 backdrop-blur-sm border border-cyan-400/20 rounded-2xl p-8 shadow-2xl">
          <div className="mb-8">
            <h3 className="text-3xl font-bold text-white mb-2">Create Account</h3>
            <p className="text-gray-400">Join the freelance marketplace</p>
          </div>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <Input
                label="Full Name"
                {...register('fullName')}
                error={errors.fullName?.message}
                className="bg-charcoal-700 border-cyan-400/30 text-white placeholder-gray-400 focus:border-cyan-400"
              />
            </div>
            <div>
              <Input
                label="Email"
                type="email"
                {...register('email')}
                error={errors.email?.message}
                className="bg-charcoal-700 border-cyan-400/30 text-white placeholder-gray-400 focus:border-cyan-400"
              />
            </div>
            <div>
              <Input
                label="Password"
                type="password"
                {...register('password')}
                error={errors.password?.message}
                className="bg-charcoal-700 border-cyan-400/30 text-white placeholder-gray-400 focus:border-cyan-400"
              />
            </div>
            <div>
              <Input
                label="Confirm Password"
                type="password"
                {...register('confirmPassword')}
                error={errors.confirmPassword?.message}
                className="bg-charcoal-700 border-cyan-400/30 text-white placeholder-gray-400 focus:border-cyan-400"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Role</label>
              <select
                {...register('role')}
                className="w-full px-3 py-2 bg-charcoal-700 border border-cyan-400/30 text-white rounded-lg focus:border-cyan-400"
              >
                <option value="customer">Customer</option>
                <option value="executor">Executor</option>
              </select>
            </div>
            <Button type="submit" className="w-full bg-cyan-400 hover:bg-cyan-500 text-charcoal-900 font-semibold py-3 rounded-lg transition-all">
              Create Account
            </Button>
          </form>
          <div className="mt-6 text-center">
            <p className="text-gray-400">
              Already have an account?{' '}
              <Link to="/login" className="text-cyan-400 hover:text-cyan-300 font-semibold">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;