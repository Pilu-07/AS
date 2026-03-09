import { useState } from 'react';
import { Send, Bot, User, BarChart2 } from 'lucide-react';
import { asAiService } from '../services/api';

export default function Chat() {
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(false);
    const [messages, setMessages] = useState([
        { role: 'ai', text: 'Hello! I am your AS-AI Data Scientist. Ask me anything about the datasets you have uploaded.' }
    ]);

    const handleAsk = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        const userMessage = { role: 'user', text: query };
        setMessages(prev => [...prev, userMessage]);
        setQuery('');
        setLoading(true);

        try {
            const res = await asAiService.askQuestion(userMessage.text);
            setMessages(prev => [...prev, {
                role: 'ai',
                text: res.data.answer,
                chart: res.data.chart
            }]);
        } catch (err) {
            setMessages(prev => [...prev, {
                role: 'ai',
                text: 'Sorry, I encountered an error running that query securely.',
                error: true
            }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-6rem)]">
            <div className="mb-4">
                <h1 className="text-2xl font-bold text-gray-800">AI Data Scientist</h1>
                <p className="text-gray-500">Ask natural language questions to filter, analyze, or plot your dataset.</p>
            </div>

            <div className="flex-1 overflow-y-auto bg-white rounded-t-xl border border-gray-200 p-6 space-y-6">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`flex max-w-3xl ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>

                            <div className={`flex-shrink-0 h-10 w-10 rounded-full flex items-center justify-center ${msg.role === 'user' ? 'bg-indigo-600 ml-4' : 'bg-emerald-500 mr-4'}`}>
                                {msg.role === 'user' ? <User className="text-white h-6 w-6" /> : <Bot className="text-white h-6 w-6" />}
                            </div>

                            <div className={`p-4 rounded-2xl shadow-sm ${msg.role === 'user' ? 'bg-indigo-600 text-white rounded-tr-none' : 'bg-gray-100 text-gray-800 rounded-tl-none border border-gray-200'}`}>
                                <p className={`whitespace-pre-wrap ${msg.error ? 'text-red-500 font-medium' : ''}`}>
                                    {msg.text}
                                </p>
                                {msg.chart && (
                                    <div className="mt-4 bg-white p-2 rounded-lg border border-gray-200">
                                        <div className="flex items-center text-gray-500 text-xs mb-2 font-medium">
                                            <BarChart2 className="w-4 h-4 mr-1" />
                                            GENERATED CHART
                                        </div>
                                        {/* Render chart straight from backend mount! */}
                                        <img src={`http://127.0.0.1:8000${msg.chart}`} alt="AI Output" className="max-w-full rounded-md" />
                                    </div>
                                )}
                            </div>

                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex justify-start">
                        <div className="flex flex-row max-w-2xl">
                            <div className="flex-shrink-0 h-10 w-10 rounded-full bg-emerald-500 mr-4 flex items-center justify-center">
                                <Bot className="text-white h-6 w-6" />
                            </div>
                            <div className="p-4 bg-gray-100 rounded-2xl rounded-tl-none border border-gray-200 flex space-x-2 items-center">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            <div className="bg-white p-4 rounded-b-xl border border-t-0 border-gray-200">
                <form onSubmit={handleAsk} className="flex relative items-center">
                    <input
                        type="text"
                        className="flex-1 bg-gray-50 border border-gray-300 rounded-full px-6 py-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all shadow-inner"
                        placeholder="E.g., What is the average loan amount by gender? Plot a histogram..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={!query.trim() || loading}
                        className="absolute right-2 p-3 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 disabled:opacity-50 transition-colors shadow-md"
                    >
                        <Send className="h-5 w-5" />
                    </button>
                </form>
            </div>
        </div>
    );
}
