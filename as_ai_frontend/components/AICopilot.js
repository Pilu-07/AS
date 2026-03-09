import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, X, Sparkles, ChevronRight, MessageSquare, Target, Activity, Send, Mic, MicOff } from 'lucide-react';
import { asAiService } from '../services/api';

export default function AICopilot({ isOpen, setIsOpen }) {
    const [messages, setMessages] = useState([
        { role: 'ai', text: 'Hi! I am your AI Copilot. I can analyze anomalies, recommend models, or summarize datasets.' }
    ]);
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(false);
    const [isListening, setIsListening] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isOpen]);

    const handleAsk = async (text) => {
        if (!text.trim()) return;

        setMessages(prev => [...prev, { role: 'user', text }]);
        setQuery('');
        setLoading(true);

        try {
            const res = await asAiService.askQuestion(text);
            setMessages(prev => [...prev, {
                role: 'ai',
                text: res.data.answer
            }]);
        } catch (err) {
            setMessages(prev => [...prev, {
                role: 'ai',
                text: 'Error processing request.',
                error: true
            }]);
        } finally {
            setLoading(false);
        }
    };

    const toggleListen = () => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert('Your browser does not support voice input.');
            return;
        }

        if (isListening) return;

        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => setIsListening(true);
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            setQuery(transcript);
        };
        recognition.onerror = (event) => {
            console.error('Speech recognition error', event.error);
            setIsListening(false);
        };
        recognition.onend = () => {
            setIsListening(false);
        };

        recognition.start();
    };

    const quickActions = [
        { label: "Summarize active dataset", icon: <Target size={14} />, query: "Give me a summary of the active dataset." },
        { label: "Check for anomalies", icon: <Activity size={14} />, query: "Are there any anomalies in this dataset?" },
        { label: "Recommend an ML Model", icon: <Sparkles size={14} />, query: "What ML model should I train for this data?" }
    ];

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ x: '100%', opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    exit={{ x: '100%', opacity: 0 }}
                    transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                    className="fixed top-0 right-0 h-full w-96 bg-gray-900 border-l border-gray-800 shadow-2xl z-50 flex flex-col"
                >
                    {/* Header */}
                    <div className="flex items-center justify-between p-4 border-b border-gray-800 bg-gray-900/50 backdrop-blur">
                        <div className="flex items-center space-x-3">
                            <div className="p-2 bg-indigo-500/20 rounded-lg">
                                <Bot className="text-indigo-400 h-6 w-6" />
                            </div>
                            <div>
                                <h3 className="text-white font-bold tracking-wide flex items-center">
                                    AI Copilot <Sparkles className="h-3 w-3 ml-2 text-cyan-400" />
                                </h3>
                                <p className="text-xs text-gray-400">GPT-4 Turbo Engine</p>
                            </div>
                        </div>
                        <button
                            onClick={() => setIsOpen(false)}
                            className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition"
                        >
                            <X size={20} />
                        </button>
                    </div>

                    {/* Quick Actions */}
                    <div className="px-4 pt-4 pb-2">
                        <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">Suggested Actions</p>
                        <div className="space-y-2">
                            {quickActions.map((action, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAsk(action.query)}
                                    className="w-full text-left flex items-center justify-between p-2 rounded-lg bg-gray-800/50 hover:bg-gray-800 text-gray-300 hover:text-white border border-gray-700/50 hover:border-gray-600 transition"
                                    disabled={loading}
                                >
                                    <span className="flex items-center text-sm">{action.icon} <span className="ml-2">{action.label}</span></span>
                                    <ChevronRight size={14} className="text-gray-500" />
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Chat History */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        {messages.map((msg, idx) => (
                            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`max-w-[85%] p-3 rounded-2xl text-sm ${msg.role === 'user'
                                    ? 'bg-indigo-600 text-white rounded-tr-sm'
                                    : 'bg-gray-800 text-gray-200 border border-gray-700/50 rounded-tl-sm'
                                    } ${msg.error ? 'border-red-500/50 text-red-200 bg-red-900/20' : ''}`}>
                                    {msg.role === 'ai' && <Bot size={14} className="mb-1 text-indigo-400" />}
                                    <p className="whitespace-pre-wrap">{msg.text}</p>
                                </div>
                            </div>
                        ))}
                        {loading && (
                            <div className="flex justify-start">
                                <div className="bg-gray-800 border border-gray-700/50 p-3 rounded-2xl rounded-tl-sm flex space-x-1">
                                    <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce"></div>
                                    <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                    <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Area */}
                    <div className="p-4 border-t border-gray-800 bg-gray-900">
                        <form
                            onSubmit={(e) => { e.preventDefault(); handleAsk(query); }}
                            className="relative flex items-center"
                        >
                            <input
                                type="text"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                placeholder="Ask Copilot..."
                                className="w-full bg-gray-800 text-white placeholder-gray-500 border border-gray-700 rounded-full pl-4 pr-20 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm"
                                disabled={loading}
                            />
                            <div className="absolute right-2 flex items-center space-x-1">
                                <button
                                    type="button"
                                    onClick={toggleListen}
                                    className={`p-1.5 rounded-full transition ${isListening ? 'bg-red-500/20 text-red-500 animate-pulse' : 'text-gray-400 hover:text-white hover:bg-gray-700'}`}
                                    title="Voice Input"
                                >
                                    {isListening ? <MicOff size={16} /> : <Mic size={16} />}
                                </button>
                                <button
                                    type="submit"
                                    disabled={!query.trim() || loading}
                                    className="p-1.5 bg-indigo-600 text-white rounded-full hover:bg-indigo-500 disabled:opacity-50 transition"
                                >
                                    <Send size={16} />
                                </button>
                            </div>
                        </form>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
