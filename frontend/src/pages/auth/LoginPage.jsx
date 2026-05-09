import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import toast from 'react-hot-toast';

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
});

const LoginPage = () => {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
  });
  const { login } = useAuth();
  const navigate = useNavigate();

  const onSubmit = async (data) => {
    try {
      await login(data.email, data.password);
      navigate('/');
    } catch (error) {
      toast.error('Login failed');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-charcoal-900 via-cyan-900 to-blue-900 flex items-center justify-center p-8">
      <div className="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
        {/* Left side - Hero content */}
        <div className="space-y-8">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-cyan-400 rounded-full flex items-center justify-center text-charcoal-900 font-bold text-2xl">O</div>
            <h1 className="text-4xl font-bold text-white">OpenDealz</h1>
          </div>
          <div className="space-y-4">
            <h2 className="text-5xl font-extrabold text-white leading-tight">
              Secure Contracts,<br />
              <span className="text-cyan-400">Trusted Deals</span>
            </h2>
            <p className="text-xl text-gray-300 max-w-md">
              Platform for programmatic smart contracts, escrow, and dispute resolution in freelance marketplace.
            </p>
          </div>
          <div className="flex space-x-4">
            <div className="bg-cyan-400/20 border border-cyan-400/30 rounded-lg p-4">
              <div className="text-cyan-400 font-semibold">100%</div>
              <div className="text-gray-300 text-sm">Secure Escrow</div>
            </div>
            <div className="bg-cyan-400/20 border border-cyan-400/30 rounded-lg p-4">
              <div className="text-cyan-400 font-semibold">24/7</div>
              <div className="text-gray-300 text-sm">Dispute Resolution</div>
            </div>
          </div>
        </div>

        {/* Right side - Login form */}
        <div className="bg-charcoal-800/50 backdrop-blur-sm border border-cyan-400/20 rounded-2xl p-8 shadow-2xl">
          <div className="mb-8">
            <h3 className="text-3xl font-bold text-white mb-2">Welcome Back</h3>
            <p className="text-gray-400">Sign in to your account</p>
          </div>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
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
            <Button type="submit" className="w-full bg-cyan-400 hover:bg-cyan-500 text-charcoal-900 font-semibold py-3 rounded-lg transition-all">
              Sign In
            </Button>
          </form>
          <div className="mt-6 text-center">
            <p className="text-gray-400">
              Don't have an account?{' '}
              <Link to="/register" className="text-cyan-400 hover:text-cyan-300 font-semibold">
                Sign up
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;