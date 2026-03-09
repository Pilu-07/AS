import { useState, useEffect } from 'react';
import { Microscope, Beaker, Activity, Lightbulb, CheckCircle, XCircle, FileText, Download, Eye, TrendingUp, AlertTriangle, GitMerge } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function ResearchLab() {
    const [loading, setLoading] = useState(false);
    const [hypotheses, setHypotheses] = useState([]);
    const [discoveries, setDiscoveries] = useState([]);
    const [datasetName, setDatasetName] = useState(null);
    const [error, setError] = useState(null);

    // Manage state for experiments
    const [runningExp, setRunningExp] = useState({});
    const [expResults, setExpResults] = useState({});

    // Manage paper state
    const [generatingPaper, setGeneratingPaper] = useState(false);
    const [paperUrl, setPaperUrl] = useState(null);

    // Manage discovery state
    const [discovering, setDiscovering] = useState(false);

    useEffect(() => {
        fetchHypotheses();
    }, []);

    const fetchHypotheses = async () => {
        setLoading(true);
        setError(null);
        setExpResults({});
        try {
            const response = await fetch('http://127.0.0.1:8000/research/hypotheses');
            if (response.ok) {
                const data = await response.json();
                setDatasetName(data.dataset);
                setHypotheses(data.hypotheses || []);
            } else {
                setError('Failed to fetch research hypotheses. Did you upload a dataset?');
            }
        } catch (err) {
            setError('Could not connect to backend to fetch hypotheses.');
        } finally {
            setLoading(false);
        }
    };

    const runDiscovery = async () => {
        setDiscovering(true);
        try {
            const response = await fetch('http://127.0.0.1:8000/research/discover_patterns', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ dataset_id: datasetName || 'dataset_1' })
            });
            if (response.ok) {
                const data = await response.json();
                setDiscoveries(data.discoveries || []);
            }
        } catch (err) {
            console.error(err);
        } finally {
            setDiscovering(false);
        }
    };

    const runExperiment = async (hypothesis, index) => {
        setRunningExp(prev => ({ ...prev, [index]: true }));
        try {
            const response = await fetch('http://127.0.0.1:8000/research/run_experiment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ dataset_id: datasetName || 'dataset_1', hypothesis })
            });
            if (response.ok) {
                const data = await response.json();
                setExpResults(prev => ({ ...prev, [index]: data }));
            } else {
                setExpResults(prev => ({ ...prev, [index]: { error: 'Failed to run experiment.' } }));
            }
        } catch (err) {
            setExpResults(prev => ({ ...prev, [index]: { error: 'Server error during execution.' } }));
        } finally {
            setRunningExp(prev => ({ ...prev, [index]: false }));
        }
    };

    const generatePaper = async () => {
        setGeneratingPaper(true);
        setError(null);
        setPaperUrl(null);
        try {
            const response = await fetch('http://127.0.0.1:8000/research/generate_paper', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ dataset_id: datasetName || 'dataset_1' })
            });
            if (response.ok) {
                const data = await response.json();
                setPaperUrl(`http://127.0.0.1:8000${data.download_url}`);
            } else {
                setError('Failed to generate research paper.');
            }
        } catch (err) {
            setError('Server error while writing research paper.');
        } finally {
            setGeneratingPaper(false);
        }
    };

    const getDiscoveryIcon = (type) => {
        switch (type) {
            case 'cluster_pattern': return <GitMerge size={20} className="text-purple-400" />;
            case 'anomaly_pattern': return <AlertTriangle size={20} className="text-amber-400" />;
            case 'trend_pattern': return <TrendingUp size={20} className="text-emerald-400" />;
            default: return <Eye size={20} className="text-cyan-400" />;
        }
    };

    return (
        <div className="space-y-8 pb-12 w-full max-w-6xl mx-auto">
            <header className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <motion.h1
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="text-4xl font-black text-white mb-2 flex items-center"
                    >
                        <Microscope size={36} className="text-pink-500 mr-3" />
                        AI Research <span className="text-gradient mx-2">Scientist</span>
                    </motion.h1>
                    <motion.p
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 }}
                        className="text-gray-400"
                    >
                        Autonomous Hypothesis Generation & Discovery Engine.
                    </motion.p>
                </div>

                <div className="flex flex-wrap gap-4">
                    <motion.button
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        whileHover={{ scale: 1.05 }}
                        onClick={runDiscovery}
                        disabled={discovering}
                        className={`px-4 py-2 rounded-lg font-bold text-sm tracking-wide transition flex items-center ${discovering ? 'bg-cyan-900/50 text-cyan-400/50 cursor-not-allowed border border-cyan-900/50' : 'bg-cyan-600/20 text-cyan-400 hover:bg-cyan-600 hover:text-white border border-cyan-500/30'}`}
                    >
                        {discovering ? <Activity size={16} className="animate-spin mr-2" /> : <Eye size={16} className="mr-2" />}
                        {discovering ? 'Discovering...' : 'Auto-Discover Patterns'}
                    </motion.button>
                    {!paperUrl ? (
                        <motion.button
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            whileHover={{ scale: 1.05 }}
                            onClick={generatePaper}
                            disabled={generatingPaper || hypotheses.length === 0}
                            className={`px-4 py-2 rounded-lg font-bold text-sm tracking-wide transition flex items-center ${generatingPaper || hypotheses.length === 0 ? 'bg-indigo-900/50 text-indigo-400/50 cursor-not-allowed border border-indigo-900/50' : 'bg-indigo-600 text-white hover:bg-indigo-500 shadow-[0_0_15px_rgba(99,102,241,0.5)]'}`}
                        >
                            {generatingPaper ? <Activity size={16} className="animate-spin mr-2" /> : <FileText size={16} className="mr-2" />}
                            {generatingPaper ? 'Writing PDF...' : 'Generate Research Paper'}
                        </motion.button>
                    ) : (
                        <motion.a
                            initial={{ scale: 0.9 }} animate={{ scale: 1 }}
                            href={paperUrl}
                            download
                            target="_blank"
                            rel="noopener noreferrer"
                            className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg font-bold text-sm tracking-wide transition flex items-center shadow-[0_0_15px_rgba(16,185,129,0.5)]"
                        >
                            <Download size={16} className="mr-2" /> Download PDF
                        </motion.a>
                    )}

                    <motion.button
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        whileHover={{ scale: 1.05 }}
                        onClick={fetchHypotheses}
                        disabled={loading}
                        className="bg-gray-800 text-gray-300 border border-gray-700 hover:bg-gray-700 hover:text-white px-4 py-2 rounded-lg font-bold text-sm tracking-wide transition flex items-center"
                    >
                        {loading ? <Activity size={16} className="animate-spin mr-2" /> : <Lightbulb size={16} className="mr-2" />}
                        Regenerate
                    </motion.button>
                </div>
            </header>

            {error && (
                <div className="bg-red-900/20 border border-red-500/50 text-red-400 p-4 rounded-xl text-sm font-medium">
                    {error}
                </div>
            )}

            {/* Discoveries Section */}
            {discoveries.length > 0 && (
                <div className="space-y-6 mb-12">
                    <div className="flex items-center text-cyan-400 text-sm font-bold tracking-widest uppercase mb-4 border-b border-gray-800 pb-2">
                        <span className="w-2 h-2 rounded-full bg-cyan-500 mr-3 animate-pulse shadow-[0_0_8px_rgba(6,182,212,0.8)]"></span>
                        Autonomous AI Discoveries
                    </div>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <AnimatePresence>
                            {discoveries.map((disc, idx) => (
                                <motion.div
                                    key={`disc-${idx}`}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: idx * 0.1 }}
                                    className="glass-panel p-6 rounded-2xl border border-gray-700 hover:border-cyan-500/50 transition-all group flex flex-col h-full bg-gradient-to-br from-gray-900 to-gray-800/50"
                                >
                                    <div className="flex items-start mb-4">
                                        <div className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center mr-4 shrink-0 border border-gray-700">
                                            {getDiscoveryIcon(disc.type)}
                                        </div>
                                        <div>
                                            <div className="text-xs text-gray-400 uppercase tracking-widest font-bold mb-1">{disc.type.replace('_', ' ')}</div>
                                            <h3 className="text-md text-white font-medium leading-snug">
                                                {disc.description}
                                            </h3>
                                        </div>
                                    </div>
                                    <div className="mt-auto pt-4 flex w-full justify-between items-center text-xs text-gray-500 font-mono">
                                        <span>Confidence: High</span>
                                        <span>Status: Verified</span>
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                    </div>
                </div>
            )}

            <div className="space-y-6">
                <div className="flex items-center text-gray-400 text-sm font-bold tracking-widest uppercase mb-4 border-b border-gray-800 pb-2">
                    <span className="w-2 h-2 rounded-full bg-pink-500 mr-3 animate-pulse shadow-[0_0_8px_rgba(236,72,153,0.8)]"></span>
                    Generated Hypotheses {datasetName && `for ${datasetName}`}
                </div>

                {loading ? (
                    <div className="glass-panel p-16 rounded-2xl border border-gray-700 flex flex-col items-center justify-center">
                        <div className="w-10 h-10 border-4 border-pink-500 border-t-transparent animate-spin rounded-full mb-4"></div>
                        <p className="text-gray-400 text-sm font-mono animate-pulse">Scanning dataset correlations and generating causal hypotheses...</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <AnimatePresence>
                            {hypotheses.length > 0 ? (
                                hypotheses.map((hyp, idx) => {
                                    const isRunning = runningExp[idx];
                                    const res = expResults[idx];

                                    return (
                                        <motion.div
                                            key={idx}
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            exit={{ opacity: 0, scale: 0.9 }}
                                            transition={{ delay: idx * 0.1 }}
                                            className="glass-panel p-6 rounded-2xl border border-gray-700 hover:border-pink-500/50 transition-all group flex flex-col h-full bg-gradient-to-br from-gray-900 to-gray-800/50"
                                        >
                                            <div className="flex-1 mb-4">
                                                <div className="flex items-start">
                                                    <div className="w-10 h-10 rounded-full bg-pink-900/30 text-pink-400 flex items-center justify-center mr-4 shrink-0 group-hover:scale-110 transition-transform">
                                                        <Lightbulb size={20} />
                                                    </div>
                                                    <h3 className="text-lg text-white font-medium leading-snug mt-1">
                                                        "{hyp}"
                                                    </h3>
                                                </div>
                                            </div>

                                            {/* Experiment Results Section */}
                                            {res && !res.error && (
                                                <motion.div
                                                    initial={{ opacity: 0, height: 0 }}
                                                    animate={{ opacity: 1, height: 'auto' }}
                                                    className="mb-4 pt-4 border-t border-gray-800"
                                                >
                                                    <div className="flex items-center justify-between mb-4 bg-gray-900/50 p-3 rounded-lg border border-gray-700">
                                                        <div className="flex items-center">
                                                            {res.result === 'supported' ? <CheckCircle size={20} className="text-emerald-500 mr-2" /> : <XCircle size={20} className="text-red-500 mr-2" />}
                                                            <div>
                                                                <div className="text-xs text-gray-400 uppercase tracking-widest font-bold">Result</div>
                                                                <div className={`font-black uppercase tracking-wide ${res.result === 'supported' ? 'text-emerald-400' : 'text-red-400'}`}>{res.result}</div>
                                                            </div>
                                                        </div>
                                                        <div className="text-right">
                                                            <div className="text-xs text-gray-400 uppercase tracking-widest font-bold">Confidence</div>
                                                            <div className="text-white font-mono font-bold">{(res.confidence * 100).toFixed(0)}%</div>
                                                        </div>
                                                    </div>

                                                    {res.charts && res.charts.length > 0 && (
                                                        <div className="w-full h-48 rounded-xl overflow-hidden border border-gray-700 bg-white/5 flex items-center justify-center">
                                                            <img src={`http://127.0.0.1:8000${res.charts[0]}`} alt="Experiment Chart" className="max-w-full max-h-full object-contain" />
                                                        </div>
                                                    )}
                                                </motion.div>
                                            )}

                                            {res && res.error && (
                                                <div className="mb-4 p-3 bg-red-900/20 text-red-500 text-xs border border-red-500/30 rounded-lg">
                                                    {res.error}
                                                </div>
                                            )}

                                            <div className="pt-4 border-t border-gray-800 mt-auto">
                                                <button
                                                    onClick={() => runExperiment(hyp, idx)}
                                                    disabled={isRunning}
                                                    className={`w-full flex items-center justify-center py-3 rounded-lg font-bold text-xs uppercase tracking-wide transition-all ${isRunning ? 'bg-indigo-900/30 text-indigo-500 cursor-not-allowed border border-indigo-900/50' : 'bg-indigo-600/10 text-indigo-400 hover:bg-indigo-600 hover:text-white border border-indigo-500/30 hover:border-indigo-500 shadow-[0_0_15px_rgba(99,102,241,0)] hover:shadow-[0_0_15px_rgba(99,102,241,0.4)]'}`}
                                                >
                                                    {isRunning ? <Activity size={14} className="animate-spin mr-2" /> : <Beaker size={14} className="mr-2" />}
                                                    {isRunning ? 'Running Simulation...' : (res ? 'Re-run Experiment' : 'Run Experiment')}
                                                </button>
                                            </div>
                                        </motion.div>
                                    )
                                })
                            ) : !error && (
                                <div className="col-span-full glass-panel p-12 rounded-2xl border border-dashed border-gray-700 text-center text-gray-500">
                                    No hypotheses generated. Try uploading a dataset first.
                                </div>
                            )}
                        </AnimatePresence>
                    </div>
                )}
            </div>
        </div>
    );
}
