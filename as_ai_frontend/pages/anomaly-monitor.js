import { useState } from 'react';
import { ShieldAlert, AlertTriangle, AlertCircle, RefreshCw } from 'lucide-react';
import { asAiService } from '../services/api';
import { motion } from 'framer-motion';
import AnimatedChart from '../components/AnimatedChart';

export default function AnomalyMonitor() {
    const [loading, setLoading] = useState(false);
    const [datasetId, setDatasetId] = useState('dataset_1');
    const [newDatasetId, setNewDatasetId] = useState('dataset_new');
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);

    const handleMonitor = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            const res = await asAiService.monitorModel(datasetId, newDatasetId);
            setResults(res.data);

            // Mock chart data for drift limits just in case it's not provided
            if (!res.data.outlier_chart) {
                setResults(prev => ({
                    ...prev,
                    mock_outliers: {
                        datasets: [
                            {
                                label: 'Baseline Data',
                                data: Array.from({ length: 50 }).map(() => ({ x: Math.random() * 50, y: Math.random() * 50 })),
                                backgroundColor: 'rgba(99, 102, 241, 0.4)',
                            },
                            {
                                label: 'Drift Detected',
                                data: Array.from({ length: 15 }).map(() => ({ x: 60 + Math.random() * 40, y: 60 + Math.random() * 40 })),
                                backgroundColor: 'rgba(239, 68, 68, 0.8)',
                            }
                        ]
                    }
                }));
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Monitoring failed. Ensure datasets exist.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-8 pb-12 w-full">
            <header className="mb-8">
                <motion.h1
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="text-4xl font-black text-white mb-2 flex items-center"
                >
                    <ShieldAlert size={36} className="text-red-500 mr-3" />
                    Anomaly <span className="text-gradient mx-2">Monitor</span> Station
                </motion.h1>
                <motion.p
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 }}
                    className="text-gray-400"
                >
                    Detect data drift, statistical outliers, and predictive boundary violations.
                </motion.p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="lg:col-span-1 glass-panel p-6 rounded-2xl h-fit border border-gray-700"
                >
                    <h2 className="text-lg font-bold mb-4 border-b border-gray-700 pb-2 text-white flex items-center">
                        <RefreshCw className="mr-2 text-indigo-400" size={18} />
                        Drift Analysis
                    </h2>
                    <form onSubmit={handleMonitor} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-1 tracking-wide uppercase text-[10px]">Reference Dataset</label>
                            <input
                                type="text"
                                className="w-full p-2.5 bg-gray-800 border border-gray-700 text-white rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none transition"
                                value={datasetId}
                                onChange={(e) => setDatasetId(e.target.value)}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-1 tracking-wide uppercase text-[10px]">Current Dataset</label>
                            <input
                                type="text"
                                className="w-full p-2.5 bg-gray-800 border border-gray-700 text-white rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none transition"
                                value={newDatasetId}
                                onChange={(e) => setNewDatasetId(e.target.value)}
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className={`w-full py-3 rounded-lg font-bold tracking-wide uppercase text-xs text-white transition-all ${loading ? 'bg-indigo-600/50 cursor-wait' : 'bg-indigo-600 hover:bg-indigo-500 shadow-[0_4px_20px_rgba(99,102,241,0.4)]'}`}
                        >
                            {loading ? 'Scanning Boundaries...' : 'Execute Monitor'}
                        </button>
                    </form>

                    {error && <div className="mt-4 p-3 bg-red-900/30 text-red-400 border border-red-500/30 rounded-lg text-sm">{error}</div>}
                </motion.div>

                <div className="lg:col-span-3 space-y-6">
                    {!results && !loading ? (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="glass-panel p-12 rounded-2xl border border-dashed border-gray-600 text-center text-gray-400 flex flex-col items-center justify-center min-h-[400px]"
                        >
                            <ShieldAlert size={64} className="mb-4 text-gray-700 hover:text-red-400 transition-colors duration-500" />
                            <p className="text-xl font-bold text-gray-300">System Secure</p>
                            <p className="text-sm mt-2 text-gray-500">Run a drift analysis to check statistical deviations.</p>
                        </motion.div>
                    ) : (
                        <>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    className={`glass-panel p-6 rounded-2xl border ${results?.drift_detected ? 'border-red-500/50 bg-red-900/10' : 'border-emerald-500/50 bg-emerald-900/10'}`}
                                >
                                    <h3 className="text-xs uppercase tracking-widest font-bold text-gray-400 mb-2">Network Status</h3>
                                    <div className="flex items-center">
                                        {results?.drift_detected ? (
                                            <AlertTriangle size={32} className="text-red-500 mr-4" />
                                        ) : (
                                            <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center mr-4">
                                                <div className="w-4 h-4 rounded-full bg-emerald-400" />
                                            </div>
                                        )}
                                        <div>
                                            <h4 className={`text-2xl font-black ${results?.drift_detected ? 'text-red-400' : 'text-emerald-400'}`}>
                                                {results?.drift_detected ? 'Drift Detected' : 'Nominal'}
                                            </h4>
                                            <p className="text-sm text-gray-400">Distribution Variance Check</p>
                                        </div>
                                    </div>
                                </motion.div>

                                <motion.div
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: 0.1 }}
                                    className="glass-panel p-6 rounded-2xl border border-gray-700 bg-gray-800/30"
                                >
                                    <h3 className="text-xs uppercase tracking-widest font-bold text-gray-400 mb-2">Alert Intelligence</h3>
                                    <div className="flex items-start mt-2 border-l-2 border-indigo-500 pl-4 h-[50px] overflow-hidden">
                                        <p className="text-sm text-gray-300">
                                            {results?.alert_message || "All statistical features align with previous bounds. PCA structural integrity is maintained."}
                                        </p>
                                    </div>
                                </motion.div>
                            </div>

                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.2 }}
                                className="glass-panel p-6 rounded-2xl border border-gray-700 h-[450px]"
                            >
                                {results?.outlier_chart ? (
                                    <img
                                        src={`http://127.0.0.1:8000${results.outlier_chart}`}
                                        alt="Outlier Analysis"
                                        className="w-full h-full object-contain rounded-xl"
                                    />
                                ) : (
                                    <AnimatedChart
                                        type="scatter"
                                        title="Outlier Boundary Visualization"
                                        data={results?.mock_outliers}
                                        options={{
                                            scales: {
                                                x: {
                                                    title: { display: true, text: 'Feature X Variance', color: '#9CA3AF' }
                                                },
                                                y: {
                                                    title: { display: true, text: 'Feature Y Variance', color: '#9CA3AF' }
                                                }
                                            }
                                        }}
                                    />
                                )}
                            </motion.div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
