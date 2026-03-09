import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot } from 'lucide-react';
import Sidebar from './Sidebar';
import AICopilot from './AICopilot';

export default function Layout({ children }) {
    const [copilotOpen, setCopilotOpen] = useState(false);
    const [mounted, setMounted] = useState(false);
    const router = useRouter();

    useEffect(() => {
        setMounted(true);
        const token = localStorage.getItem('as_ai_token');
        if (!token && !['/login', '/register'].includes(router.pathname)) {
            router.push('/login');
        }
    }, [router.pathname]);

    if (!mounted) return null;

    // Do not render Sidebar and Copilot on Auth pages
    if (['/login', '/register'].includes(router.pathname)) {
        return <div className="min-h-screen bg-[#0B0F19]">{children}</div>;
    }

    return (
        <div className="flex h-screen bg-[var(--background)] text-gray-200 font-sans overflow-hidden">
            <Sidebar />
            <div className="flex-1 flex flex-col ml-64 relative">
                {/* Floating Copilot Toggle */}
                <button
                    onClick={() => setCopilotOpen(true)}
                    className={`absolute top-6 right-6 z-40 p-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-full shadow-[0_0_20px_rgba(99,102,241,0.4)] transition-transform hover:scale-105 ${copilotOpen ? 'hidden' : 'block'}`}
                >
                    <Bot size={24} />
                </button>

                <AICopilot isOpen={copilotOpen} setIsOpen={setCopilotOpen} />

                <main className="flex-1 overflow-x-hidden overflow-y-auto p-8 relative z-0">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={router.pathname}
                            initial={{ opacity: 0, y: 15 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -15 }}
                            transition={{ duration: 0.3, ease: 'easeOut' }}
                            className="max-w-7xl mx-auto h-full"
                        >
                            {children}
                        </motion.div>
                    </AnimatePresence>
                </main>
            </div>
        </div>
    );
}
