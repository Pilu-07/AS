import { useState, useEffect } from 'react';
import { Download, FileText, Presentation as PresentationIcon, CheckCircle, ChevronRight, BarChart2, Zap, Target } from 'lucide-react';
import { asAiService } from '../services/api';
import { motion, AnimatePresence } from 'framer-motion';

export default function Storytelling() {
    const [loading, setLoading] = useState(false);
    const [storyData, setStoryData] = useState(null);
    const [presentationUrl, setPresentationUrl] = useState(null);
    const [error, setError] = useState(null);
    const [generating, setGenerating] = useState(false);
    const datasetId = 'dataset_1'; // Usually dynamically selected in the platform

    useEffect(() => {
        fetchStory();
    }, []);

    const fetchStory = async () => {
        setLoading(true);
        try {
            // Note: Since API might not be connected to API service layer yet, do an explicit fetch or assume it's added.
            // But we can just use native fetch if api.js lacks the method, or we mock if api.js is not editable this run.
            // The prompt says we added /executive_summary and /generate_presentation. Let's try native fetch for simplicity
            // to avoid needing to edit api.js, though editing api.js is cleaner.
            const response = await fetch('http://127.0.0.1:8000/executive_summary');
            if (response.ok) {
                const data = await response.json();
                setStoryData(data);
            } else {
                setError('Failed to load executive summary. Error ' + response.status);
            }
        } catch (err) {
            setError('Could not connect to backend to fetch story.');
        } finally {
            setLoading(false);
        }
    };

    const handleGeneratePresentation = async () => {
        setGenerating(true);
        setError(null);
        try {
            const response = await fetch('http://127.0.0.1:8000/generate_presentation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ dataset_id: datasetId })
            });
            if (response.ok) {
                const data = await response.json();
                setPresentationUrl(`http://127.0.0.1:8000${data.download_url}`);
            } else {
                setError('Failed to generate presentation. Error ' + response.status);
            }
        } catch (err) {
            setError('Server error during presentation generation.');
        } finally {
            setGenerating(false);
        }
    };

    const timelineSteps = [
        { title: "Data Overview", icon: <FileText size={20} />, text: "Profiled all schemas, mapped statistics, and parsed row metadata autonomously." },
        { title: "Patterns Found", icon: <BarChart2 size={20} />, text: "Correlation heatmaps calculated. Key trend vectors established across numeric clusters." },
        { title: "Models Trained", icon: <Target size={20} />, text: "Hyperparameters tuned across Random Forest & XGBoost. Leaderboard populated." },
        { title: "Insights Generated", icon: <Zap size={20} />, text: "SHAP Explainability interpreted global feature impacts and marginal contributions." },
        { title: "Business Recommendations", icon: <PresentationIcon size={20} />, text: "Converted numerical analysis into actionable executive intelligence." },
    ];

    return (
        <div className="space-y-8 pb-12 w-full max-w-6xl mx-auto">
            <header className="mb-8">
                <motion.h1
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="text-4xl font-black text-white mb-2 flex items-center"
                >
                    <PresentationIcon size={36} className="text-cyan-400 mr-3" />
                    AI Data <span className="text-gradient mx-2">Story</span> Engine
                </motion.h1>
                <motion.p
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 }}
                    className="text-gray-400"
                >
                    Autonomous transformation of analytical outputs into C-suite executive narratives.
                </motion.p>
            </header>

            {error && (
                <div className="bg-red-900/20 border border-red-500/50 text-red-400 p-4 rounded-xl text-sm font-medium">
                    {error}
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Narrative Cards */}
                <div className="lg:col-span-2 space-y-6">
                    {loading ? (
                        <div className="glass-panel p-12 rounded-2xl border border-gray-700 mt-6 flex justify-center py-20">
                            <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent animate-spin rounded-full"></div>
                        </div>
                    ) : storyData ? (
                        <>
                            {/* Executive Summary */}
                            <motion.div
                                initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
                                className="glass-panel p-8 rounded-2xl border border-gray-700 bg-gradient-to-br from-gray-900/50 to-indigo-900/20"
                            >
                                <h3 className="text-xs uppercase tracking-widest font-bold text-indigo-400 mb-4 flex items-center">
                                    <FileText size={16} className="mr-2" /> Executive Summary
                                </h3>
                                <p className="text-lg text-gray-200 leading-relaxed font-serif">
                                    "{storyData.summary}"
                                </p>
                            </motion.div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {/* Key Findings */}
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
                                    className="glass-panel p-6 rounded-2xl border border-gray-700"
                                >
                                    <h3 className="text-xs uppercase tracking-widest font-bold text-cyan-400 mb-4">Core Drivers</h3>
                                    <ul className="space-y-4">
                                        {storyData.key_findings?.map((finding, idx) => (
                                            <li key={idx} className="flex items-start">
                                                <Target size={16} className="text-cyan-500 shrink-0 mt-1 mr-3" />
                                                <span className="text-gray-300 text-sm">{finding}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </motion.div>

                                {/* Recommendations */}
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
                                    className="glass-panel p-6 rounded-2xl border border-emerald-500/30 bg-emerald-900/5"
                                >
                                    <h3 className="text-xs uppercase tracking-widest font-bold text-emerald-400 mb-4">Action Plan</h3>
                                    <ul className="space-y-4">
                                        {storyData.recommendations?.map((rec, idx) => (
                                            <li key={idx} className="flex items-start">
                                                <CheckCircle size={16} className="text-emerald-500 shrink-0 mt-1 mr-3" />
                                                <span className="text-gray-300 text-sm">{rec}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </motion.div>
                            </div>
                        </>
                    ) : null}
                </div>

                {/* Right Column: Timeline & Export */}
                <div className="space-y-6">
                    {/* PPTX Exporter */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }}
                        className="glass-panel p-6 rounded-2xl border border-indigo-500/30 bg-indigo-900/10 text-center"
                    >
                        <h3 className="text-white font-bold mb-2">Automated Pitch Deck</h3>
                        <p className="text-xs text-gray-400 mb-6">Compiles a 6-slide PowerPoint containing data overviews, charts, and recommendations.</p>

                        {!presentationUrl ? (
                            <button
                                onClick={handleGeneratePresentation}
                                disabled={generating || loading || !storyData}
                                className={`w-full py-3 rounded-lg font-bold tracking-wide uppercase text-xs text-white transition-all flex justify-center items-center ${generating ? 'bg-indigo-800/50 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-500 shadow-[0_0_15px_rgba(99,102,241,0.5)]'}`}
                            >
                                {generating ? <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div> : <Download size={16} className="mr-2" />}
                                {generating ? 'Generating Slides...' : 'Generate Presentation'}
                            </button>
                        ) : (
                            <motion.a
                                initial={{ scale: 0.9 }} animate={{ scale: 1 }}
                                href={presentationUrl}
                                download
                                className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold tracking-wide uppercase text-xs flex justify-center items-center shadow-[0_0_15px_rgba(16,185,129,0.5)] transition-all"
                            >
                                <Download size={16} className="mr-2" /> Download PPTX
                            </motion.a>
                        )}
                    </motion.div>

                    {/* Data Story Timeline */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
                        className="glass-panel p-6 rounded-2xl border border-gray-700"
                    >
                        <h3 className="text-xs uppercase tracking-widest font-bold text-gray-400 mb-6 font-mono">Telemetry Pipeline Progress</h3>
                        <div className="space-y-0 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-indigo-500 before:to-gray-800">
                            {timelineSteps.map((step, idx) => (
                                <motion.div
                                    key={idx}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: 0.6 + (idx * 0.1) }}
                                    className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active pb-6 last:pb-0"
                                >
                                    <div className="flex items-center justify-center w-10 h-10 rounded-full border border-gray-700 bg-gray-900 text-indigo-400 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10 group-hover:scale-110 transition-transform duration-300 group-hover:border-indigo-500 group-hover:bg-indigo-900/50">
                                        {step.icon}
                                    </div>
                                    <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] glass-panel p-4 rounded-xl border border-gray-800 hover:border-indigo-500/50 transition-colors">
                                        <div className="flex items-center justify-between mb-1">
                                            <div className="font-bold text-white text-sm">{step.title}</div>
                                            <div className="text-[10px] text-gray-500 font-mono">Step {idx + 1}</div>
                                        </div>
                                        <div className="text-xs text-gray-400">{step.text}</div>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>

                </div>
            </div>
        </div>
    );
}
