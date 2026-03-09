import { useState, useEffect, useRef } from 'react';
import { Code, Send, Database, BarChart, Terminal, Loader2, Image as ImageIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../utils/api';

export default function AIAnalyst() {
    const [datasets, setDatasets] = useState([]);
    const [selectedDataset, setSelectedDataset] = useState("");
    const [query, setQuery] = useState("");

    const [conversations, setConversations] = useState([]);
    const [loading, setLoading] = useState(false);

    const chatEndRef = useRef(null);

    useEffect(() => {
        fetchDatasets();
    }, []);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [conversations, loading]);

    const fetchDatasets = async () => {
        try {
            // Merge both user's and team datasets into single list for selector
            const res = await api.get('/datasets');
            let allSets = res.data.datasets || [];

            const tr = await api.get('/teams');
            for (let t of tr.data.teams) {
                const tds = await api.get(`/teams/${t.id}/datasets`);
                allSets = [...allSets, ...(tds.data.datasets || [])];
            }
            // Unique
            const uniqueSets = Array.from(new Set(allSets.map(a => a.id)))
                .map(id => {
                    return allSets.find(a => a.id === id)
                });

            setDatasets(uniqueSets);
            if (uniqueSets.length > 0) setSelectedDataset(uniqueSets[0].id.toString());
        } catch (err) {
            console.error("Failed loading datasets", err);
        }
    };

    const handleSend = async () => {
        if (!query.trim() || !selectedDataset) return;

        const userMessage = { role: 'user', content: query };
        setConversations(prev => [...prev, userMessage]);
        setQuery("");
        setLoading(true);

        try {
            const res = await api.post('/ai_analyst/chat', {
                dataset_id: selectedDataset,
                question: userMessage.content
            });

            const aiMessage = {
                role: 'assistant',
                summary: res.data.analysis_summary,
                code: res.data.generated_code,
                charts: res.data.chart_data || [],
                detailed: res.data.detailed_output,
                extracted: res.data.extracted_data
            };
            setConversations(prev => [...prev, aiMessage]);
        } catch (err) {
            setConversations(prev => [...prev, {
                role: 'system',
                content: `Execution failed: ${err.response?.data?.detail || err.message}`
            }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex h-[calc(100vh-4rem)] space-x-6 pb-6">

            {/* Left Panel: Dataset Selection */}
            <div className="w-64 flex-shrink-0 flex flex-col space-y-4">
                <div className="glass-panel p-5 rounded-2xl h-full border border-gray-800">
                    <h3 className="text-white font-bold mb-4 flex items-center border-b border-gray-800 pb-3">
                        <Database size={18} className="mr-2 text-indigo-400" /> Active Context
                    </h3>

                    <div className="space-y-2">
                        <label className="text-xs text-gray-500 uppercase tracking-widest font-bold">Select Dataset</label>
                        <select
                            value={selectedDataset}
                            onChange={(e) => setSelectedDataset(e.target.value)}
                            className="w-full bg-gray-900 border border-indigo-500/30 text-white rounded-lg px-3 py-2.5 outline-none focus:border-indigo-500 cursor-pointer"
                        >
                            <option value="" disabled>-- Choose Dataset --</option>
                            {datasets.map(d => (
                                <option key={d.id} value={d.id}>{d.name} ({d.rows} rows)</option>
                            ))}
                        </select>
                    </div>
                </div>
            </div>

            {/* Center Panel: Chat */}
            <div className="flex-1 glass-panel rounded-2xl border border-gray-800 flex flex-col overflow-hidden relative">

                {/* Header */}
                <div className="p-4 border-b border-gray-800 bg-gray-900/50 flex items-center justify-between">
                    <div className="flex items-center">
                        <div className="p-2 bg-indigo-500/10 rounded-lg mr-3">
                            <Code className="text-indigo-400 h-5 w-5" />
                        </div>
                        <div>
                            <h2 className="text-white font-bold">Autonomous Analyst</h2>
                            <p className="text-xs text-gray-400">Generate, execute, and visualize code dynamically.</p>
                        </div>
                    </div>
                </div>

                {/* Chat Area */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {conversations.length === 0 && (
                        <div className="h-full flex flex-col items-center justify-center text-gray-500 space-y-4">
                            <Terminal size={48} className="opacity-20" />
                            <p>Ask a question about the selected dataset.</p>
                            <div className="flex space-x-2 text-xs">
                                <span className="bg-gray-800 px-3 py-1.5 rounded-full cursor-pointer hover:text-white" onClick={() => setQuery("Show me the correlation between numerical features.")}>"Show numerical correlations"</span>
                                <span className="bg-gray-800 px-3 py-1.5 rounded-full cursor-pointer hover:text-white" onClick={() => setQuery("Plot the distribution of the status column.")}>"Plot column distributions"</span>
                            </div>
                        </div>
                    )}

                    {conversations.map((msg, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div className={`max-w-[85%] rounded-2xl p-5 ${msg.role === 'user' ? 'bg-indigo-600 text-white' : msg.role === 'system' ? 'bg-red-500/10 border border-red-500/30 text-red-200' : 'bg-gray-800/80 border border-gray-700'}`}>

                                {msg.role === 'user' && <p>{msg.content}</p>}
                                {msg.role === 'system' && <p className="font-mono text-sm">{msg.content}</p>}

                                {msg.role === 'assistant' && (
                                    <div className="space-y-4">
                                        <div className="prose prose-invert max-w-none text-sm leading-relaxed">
                                            {msg.summary}
                                        </div>

                                        {msg.charts && msg.charts.length > 0 && (
                                            <div className="mt-4 pt-4 border-t border-gray-700">
                                                <div className="text-xs text-gray-400 mb-3 flex items-center uppercase tracking-widest font-bold"><ImageIcon size={14} className="mr-1" /> Generated Visualizations</div>
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                    {msg.charts.map((chartPath, idx) => (
                                                        <a href={`http://127.0.0.1:8000${chartPath}`} target="_blank" rel="noreferrer" key={idx}>
                                                            <div className="rounded-lg overflow-hidden border border-gray-700 bg-white p-1 hover:border-indigo-500 transition-colors cursor-pointer">
                                                                <img src={`http://127.0.0.1:8000${chartPath}`} alt="generated chart" className="w-full h-auto object-contain" />
                                                            </div>
                                                        </a>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {msg.code && (
                                            <div className="mt-4 pt-4 border-t border-gray-700">
                                                <div className="text-xs text-gray-500 mb-2 font-mono">Executed Logic Pattern:</div>
                                                <pre className="bg-gray-900 border border-gray-700 p-4 rounded-xl overflow-x-auto text-xs font-mono text-emerald-400">
                                                    {msg.code}
                                                </pre>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    ))}

                    {loading && (
                        <div className="flex justify-start">
                            <div className="bg-gray-800/80 border border-gray-700 rounded-2xl p-4 flex items-center space-x-3 text-indigo-400 font-mono text-sm">
                                <Loader2 size={16} className="animate-spin" />
                                <span>Generating Executable Pipeline...</span>
                            </div>
                        </div>
                    )}
                    <div ref={chatEndRef} />
                </div>

                {/* Input Area */}
                <div className="p-4 bg-gray-900/80 border-t border-gray-800 relative z-10">
                    <form
                        onSubmit={(e) => { e.preventDefault(); handleSend(); }}
                        className="flex items-center space-x-3 bg-gray-800 border border-gray-700 focus-within:border-indigo-500/50 rounded-xl p-2 transition-all"
                    >
                        <input
                            type="text"
                            disabled={loading || !selectedDataset}
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder={!selectedDataset ? "Select a dataset first..." : "Ask the AI Analyst to plot trends..."}
                            className="flex-1 bg-transparent px-3 py-2 text-white outline-none placeholder-gray-500 disabled:opacity-50"
                        />
                        <button
                            type="submit"
                            disabled={loading || !query.trim() || !selectedDataset}
                            className="p-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-700 text-white rounded-lg transition-colors flex-shrink-0"
                        >
                            <Send size={18} />
                        </button>
                    </form>
                </div>

            </div>
        </div>
    );
}
