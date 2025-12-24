import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { MapPin, LogIn, Eye, EyeOff } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error('Please fill in all fields');
      return;
    }
    
    setLoading(true);
    try {
      await login(email, password);
      toast.success('Welcome back!');
      navigate('/dashboard');
    } catch (error) {
      const message = error.response?.data?.detail || 'Login failed';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left side - Image */}
      <div className="hidden lg:flex lg:w-1/2 auth-bg relative">
        <div className="absolute inset-0 bg-slate-950/80" />
        <div className="relative z-10 flex flex-col justify-center px-16">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 bg-indigo-600/20 rounded-xl border border-indigo-500/30">
                <MapPin className="h-8 w-8 text-indigo-400" />
              </div>
              <span className="font-mono text-2xl font-bold text-white tracking-tight">IIPS RoomFinder</span>
            </div>
            <h1 className="font-mono text-4xl font-bold text-white mb-4 tracking-tight">
              Find Empty Classrooms
            </h1>
            <p className="text-slate-400 text-lg max-w-md leading-relaxed">
              Locate available classrooms at IIPS DAVV instantly. 
              Use natural language to search and find the perfect space for your needs.
            </p>
          </motion.div>
        </div>
      </div>

      {/* Right side - Form */}
      <div className="w-full lg:w-1/2 bg-[#020617] flex items-center justify-center p-8">
        <motion.div 
          className="w-full max-w-md"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="lg:hidden flex items-center gap-3 mb-8 justify-center">
            <div className="p-2 bg-indigo-600/20 rounded-lg border border-indigo-500/30">
              <MapPin className="h-6 w-6 text-indigo-400" />
            </div>
            <span className="font-mono text-xl font-bold text-white">IIPS RoomFinder</span>
          </div>

          <div className="mb-8">
            <h2 className="font-mono text-3xl font-bold text-white tracking-tight mb-2">Welcome back</h2>
            <p className="text-slate-400">Sign in to find available classrooms</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-slate-300 text-sm uppercase tracking-wider">Email</Label>
              <Input
                id="email"
                type="email"
                data-testid="login-email-input"
                placeholder="your.email@iips.edu.in"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="h-12 bg-slate-900/50 border-slate-700 text-white placeholder:text-slate-500 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-slate-300 text-sm uppercase tracking-wider">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  data-testid="login-password-input"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="h-12 bg-slate-900/50 border-slate-700 text-white placeholder:text-slate-500 focus:ring-2 focus:ring-indigo-500 focus:border-transparent pr-12"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors"
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>

            <Button
              type="submit"
              data-testid="login-submit-button"
              disabled={loading}
              className="w-full h-12 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-lg shadow-lg shadow-indigo-500/20 transition-all active:scale-95"
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                  Signing in...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <LogIn className="h-5 w-5" />
                  Sign In
                </div>
              )}
            </Button>
          </form>

          <p className="mt-8 text-center text-slate-400">
            Don't have an account?{' '}
            <Link 
              to="/register" 
              data-testid="register-link"
              className="text-indigo-400 hover:text-indigo-300 font-medium transition-colors"
            >
              Create one
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
