import { useState } from 'react';
import { useRouter } from 'next/router';
import { Shield, BrainCircuit, Activity, Lock, Mail, ArrowRight, UserPlus } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Register() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const router = useRouter();

    const handleRegister = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await fetch('http://127.0.0.1:8000/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });

            if (response.ok) {
                // Instantly login upon successful registration
                const loginResponse = await fetch('http://127.0.0.1:8000/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password }),
                });

                if (loginResponse.ok) {
                    const data = await loginResponse.json();
                    localStorage.setItem('as_ai_token', data.access_token);
                    router.push('/');
                } else {
                    router.push('/login');
                }
            } else {
                const errData = await response.json();
                setError(errData.detail || 'Registration failed.');
            }
        } catch (err) {
            setError('Could not connect to server.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#0B0F19] flex relative overflow-hidden items-center justify-center p-4">
            {/* Background elements */}
            <div className="absolute top-[-20%] right-[-10%] w-[50%] h-[50%] bg-cyan-600/20 blur-[120px] rounded-full pointer-events-none"></div>
            <div className="absolute bottom-[-20%] left-[-10%] w-[50%] h-[50%] bg-indigo-600/20 blur-[120px] rounded-full pointer-events-none"></div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="glass-panel w-full max-w-md p-8 rounded-3xl z-10 border border-gray-800/60 shadow-2xl relative"
            >
                <div className="flex flex-col items-center mb-8">
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-400 flex items-center justify-center shadow-lg shadow-cyan-500/20 mb-4 to-indigo-500">
                        <BrainCircuit size={32} className="text-white" />
                    </div>
                    <h1 className="text-2xl font-black text-white text-center">Join AS-AI</h1>
                    <p className="text-gray-400 text-sm mt-2 text-center">Create your intelligent workspace account</p>
                </div>

                {error && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mb-6 p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-lg text-center">
                        {error}
                    </motion.div>
                )}

                <form onSubmit={handleRegister} className="space-y-5">
                    <div>
                        <label className="block text-xs font-bold tracking-widest text-gray-400 uppercase mb-2">Email Address</label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Mail size={16} className="text-gray-500" />
                            </div>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="bg-gray-900/50 border border-gray-700 text-white text-sm rounded-lg focus:ring-cyan-500 focus:border-cyan-500 block w-full pl-10 p-3 transition-colors"
                                placeholder="scientist@as-ai.com"
                                required
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs font-bold tracking-widest text-gray-400 uppercase mb-2">Password</label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Lock size={16} className="text-gray-500" />
                            </div>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="bg-gray-900/50 border border-gray-700 text-white text-sm rounded-lg focus:ring-cyan-500 focus:border-cyan-500 block w-full pl-10 p-3 transition-colors"
                                placeholder="••••••••"
                                required
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full text-white bg-gradient-to-r from-cyan-600 to-indigo-500 hover:from-cyan-500 hover:to-indigo-400 shadow-[0_0_20px_rgba(6,182,212,0.4)] hover:shadow-[0_0_25px_rgba(6,182,212,0.6)] focus:ring-4 focus:outline-none focus:ring-cyan-300 font-bold rounded-xl text-sm px-5 py-3.5 text-center flex items-center justify-center transition-all disabled:opacity-70 disabled:cursor-not-allowed mt-4"
                    >
                        {loading ? <Activity size={18} className="animate-spin mr-2" /> : <UserPlus size={18} className="mr-2" />}
                        {loading ? 'Creating Account...' : 'Register Account'}
                    </button>

                    <div className="text-center mt-6">
                        <p className="text-sm text-gray-400">
                            Already have an account?{' '}
                            <button type="button" onClick={() => router.push('/login')} className="text-cyan-400 hover:text-cyan-300 font-bold transition-colors">
                                Sign in <ArrowRight size={12} className="inline ml-1" />
                            </button>
                        </p>
                    </div>
                </form>
            </motion.div>
        </div>
    );
}
