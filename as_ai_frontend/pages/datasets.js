import { useState, useEffect } from 'react';
import { UploadCloud, FileSpreadsheet, ServerCrash, Trash2, LineChart, Cpu, Activity, Lightbulb, ChevronDown, ChevronUp } from 'lucide-react';
import { useRouter } from 'next/router';
import api from '../utils/api';
import DatasetExplorer from '../components/DatasetExplorer';
import { motion, AnimatePresence } from 'framer-motion';

export default function Datasets() {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [datasets, setDatasets] = useState([]);
    const [datasetInsights, setDatasetInsights] = useState(null);
    const [openInsights, setOpenInsights] = useState({});
    const [fetchedInsights, setFetchedInsights] = useState({});
    const [loadingInsights, setLoadingInsights] = useState({});

    const router = useRouter();

    useEffect(() => {
        fetchDatasets();

        // Initial dummy data to load the explorer if no upload exists
        setDatasetInsights({
            columns: ['id', 'feature_A', 'feature_B', 'revenue', 'status', 'timestamp'],
            data: Array.from({ length: 15 }).map((_, i) => ({
                id: i,
                feature_A: Math.random().toFixed(4),
                feature_B: Math.floor(Math.random() * 100),
                revenue: (Math.random() * 10000).toFixed(2),
                status: i % 3 === 0 ? 'Anomaly' : 'Normal',
                timestamp: new Date().toISOString()
            }))
        });
    }, []);

    const fetchDatasets = async () => {
        try {
            const res = await api.get('/datasets');
            if (res.data && res.data.datasets) {
                setDatasets(res.data.datasets);
            }
        } catch (err) {
            console.error("Failed to load user datasets", err);
        }
    };

    const handleFileChange = (e) => {
        if (e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) return;
        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await api.post('/upload_dataset', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            await fetchDatasets();
            setFile(null);

            // Re-fetch insights logic here if needed
        } catch (err) {
            setError(err.response?.data?.detail || 'Upload failed');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (datasetId) => {
        if (!confirm("Are you sure you want to delete this dataset?")) return;
        try {
            await api.delete(`/datasets/${datasetId}`);
            fetchDatasets();
        } catch (err) {
            alert("Failed to delete dataset");
        }
    };

    const toggleInsights = async (datasetId) => {
        // Toggle visibility
        setOpenInsights(prev => ({ ...prev, [datasetId]: !prev[datasetId] }));

        // If we are opening and haven't fetched yet
        if (!openInsights[datasetId] && !fetchedInsights[datasetId]) {
            setLoadingInsights(prev => ({ ...prev, [datasetId]: true }));
            try {
                const res = await api.get(`/datasets/${datasetId}/insights`);
                setFetchedInsights(prev => ({ ...prev, [datasetId]: res.data.insights || [] }));
            } catch (err) {
                console.error("Failed to load insights", err);
                setFetchedInsights(prev => ({ ...prev, [datasetId]: [] })); // prevent infinite loading loops
            } finally {
                setLoadingInsights(prev => ({ ...prev, [datasetId]: false }));
            }
        }
    };

    return (
        <div className="space-y-8 pb-12">
            <header className="mb-8">
                <motion.h1
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="text-4xl font-black text-white mb-2"
                >
                    Workspace <span className="text-gradient">Hub</span>
                </motion.h1>
                <motion.p
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 }}
                    className="text-gray-400"
                >
                    Ingest files and systematically manage high-dimensional data workspaces across your profile.
                </motion.p>
            </header>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="glass-panel p-8 rounded-2xl relative overflow-hidden"
            >
                <div className="border border-dashed border-gray-600 rounded-xl p-10 flex flex-col items-center justify-center bg-gray-900/50 hover:bg-gray-800/80 transition-colors cursor-pointer group">
                    <div className="p-4 bg-gray-800 rounded-full mb-4 group-hover:scale-110 transition-transform">
                        <UploadCloud className="h-8 w-8 text-indigo-400" />
                    </div>
                    <h3 className="text-lg font-bold text-white mb-2">Initialize Data Pipeline</h3>
                    <p className="text-sm text-gray-400 mb-6 text-center max-w-sm">Upload CSV or XLSX arrays. Files are instantly mapped to your secured multi-user schemas.</p>

                    <div className="flex items-center space-x-4 w-full max-w-md justify-center">
                        <label className="cursor-pointer bg-gray-800 border border-gray-700 text-gray-300 px-6 py-2.5 rounded-lg font-semibold hover:bg-gray-700 hover:text-white transition-colors">
                            Select File
                            <input type="file" className="hidden" accept=".csv, .xlsx" onChange={handleFileChange} />
                        </label>
                        <span className="text-sm text-gray-500 font-mono truncate max-w-[200px]">{file ? file.name : 'No sequence loaded'}</span>
                    </div>

                    <button
                        onClick={handleUpload}
                        disabled={!file || loading}
                        className={`mt-6 px-10 py-3 rounded-lg text-white font-bold tracking-wide uppercase text-sm w-full max-w-md transition-all ${!file || loading ? 'bg-indigo-600/50 text-indigo-200/50 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-500 shadow-[0_0_20px_rgba(99,102,241,0.4)]'}`}
                    >
                        {loading ? <Activity size={18} className="animate-spin inline-block mr-2" /> : 'Map to Cloud Dataset'}
                    </button>
                    {error && <p className="mt-4 text-red-500 text-sm font-semibold">{error}</p>}
                </div>
            </motion.div>

            <div className="my-10">
                <h3 className="text-xl font-bold text-white mb-6 flex items-center">
                    <FileSpreadsheet className="mr-3 text-indigo-400" size={24} /> Enrolled Datasets
                </h3>

                {datasets.length === 0 ? (
                    <div className="glass-panel p-8 rounded-xl text-center text-gray-500 font-mono text-sm border-dashed border border-gray-700">
                        No datasets uploaded in this workspace yet.
                    </div>
                ) : (
                    <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                        <AnimatePresence>
                            {datasets.map((dataset, idx) => (
                                <motion.div
                                    key={dataset.id}
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 0.9 }}
                                    transition={{ duration: 0.3, delay: idx * 0.05 }}
                                    className="glass-panel rounded-2xl border border-gray-800 p-6 flex flex-col justify-between hover:border-indigo-500/50 transition-colors bg-gradient-to-br from-gray-900 to-[#0c1220]"
                                >
                                    <div className="flex justify-between items-start mb-6">
                                        <div className="flex items-center space-x-4">
                                            <div className="w-12 h-12 rounded-xl bg-gray-800 border border-gray-700 flex items-center justify-center shadow-lg shadow-black/50">
                                                <FileSpreadsheet size={24} className="text-indigo-400" />
                                            </div>
                                            <div>
                                                <h4 className="text-white font-bold text-lg">{dataset.name}</h4>
                                                <p className="text-gray-500 text-xs font-mono uppercase tracking-widest mt-1">Uploaded: {new Date(dataset.created_at).toLocaleDateString()}</p>
                                            </div>
                                        </div>
                                        <button onClick={() => handleDelete(dataset.id)} className="text-gray-500 hover:text-red-400 p-2 rounded-lg hover:bg-red-500/10 transition-colors">
                                            <Trash2 size={18} />
                                        </button>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4 mb-6">
                                        <div className="bg-gray-800/50 p-3 rounded-xl border border-gray-700/50">
                                            <div className="text-xs text-gray-500 uppercase font-bold tracking-widest mb-1">Row Density</div>
                                            <div className="text-white font-mono text-lg font-black">{dataset.rows.toLocaleString()}</div>
                                        </div>
                                        <div className="bg-gray-800/50 p-3 rounded-xl border border-gray-700/50">
                                            <div className="text-xs text-gray-500 uppercase font-bold tracking-widest mb-1">Feature Dimensionality</div>
                                            <div className="text-white font-mono text-lg font-black">{dataset.columns.toLocaleString()}</div>
                                        </div>
                                    </div>

                                    <div className="flex flex-wrap gap-3 mt-auto border-t border-gray-800 pt-5">
                                        <button
                                            onClick={() => router.push(`/dashboard/${dataset.id}`)}
                                            className="flex-1 bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 font-bold py-2.5 rounded-lg text-sm border border-indigo-500/30 transition-colors flex items-center justify-center"
                                        >
                                            <LineChart size={16} className="mr-2" /> View Dashboard
                                        </button>
                                        <button
                                            onClick={() => router.push('/model-lab')}
                                            className="flex-1 bg-cyan-600/10 hover:bg-cyan-600/20 text-cyan-400 font-bold py-2.5 rounded-lg text-sm border border-cyan-500/30 transition-colors flex items-center justify-center"
                                        >
                                            <Cpu size={16} className="mr-2" /> AI Execute
                                        </button>
                                        <button
                                            onClick={() => toggleInsights(dataset.id)}
                                            className={`flex-1 font-bold py-2.5 rounded-lg text-sm border transition-colors flex items-center justify-center ${openInsights[dataset.id] ? 'bg-amber-500/20 border-amber-500/50 text-amber-400' : 'bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border-amber-500/30'}`}
                                        >
                                            <Lightbulb size={16} className="mr-2" /> {openInsights[dataset.id] ? 'Hide Insights' : 'AI Insights'}
                                        </button>
                                    </div>

                                    {/* Insights Panel Expansion */}
                                    <AnimatePresence>
                                        {openInsights[dataset.id] && (
                                            <motion.div
                                                initial={{ height: 0, opacity: 0 }}
                                                animate={{ height: 'auto', opacity: 1 }}
                                                exit={{ height: 0, opacity: 0 }}
                                                className="overflow-hidden mt-4"
                                            >
                                                <div className="p-4 bg-gray-900/60 rounded-xl border border-gray-800 border-dashed space-y-3">
                                                    <h5 className="text-sm font-bold text-amber-400 mb-2 flex items-center uppercase tracking-wider">
                                                        <Lightbulb size={14} className="mr-2" /> Autonomous Discoveries
                                                    </h5>

                                                    {loadingInsights[dataset.id] ? (
                                                        <div className="flex items-center text-gray-500 text-sm py-4">
                                                            <Activity size={16} className="animate-spin mr-2" /> Scanning metrics...
                                                        </div>
                                                    ) : fetchedInsights[dataset.id]?.length > 0 ? (
                                                        <div className="space-y-3 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
                                                            {fetchedInsights[dataset.id].map((ins, i) => (
                                                                <div key={i} className="bg-gray-800/80 p-3 rounded-lg border border-gray-700">
                                                                    <div className="flex justify-between items-start mb-1">
                                                                        <span className="text-[10px] uppercase font-bold tracking-widest text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded">{ins.type.replace('_', ' ')}</span>
                                                                        <span className="text-[10px] text-gray-400 font-mono">Rank: {(ins.importance * 10).toFixed(1)}/10</span>
                                                                    </div>
                                                                    <p className="text-sm text-gray-300 leading-relaxed">{ins.description}</p>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    ) : (
                                                        <div className="text-sm text-gray-500 italic py-2">
                                                            No significant insights detected yet. A background pipeline may still be running.
                                                        </div>
                                                    )}
                                                </div>
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                    </div>
                )}
            </div>

            <h3 className="text-xl font-bold text-white mb-6 flex items-center pt-8 border-t border-gray-800">
                <ServerCrash className="mr-3 text-cyan-400" size={24} /> Telemetric Data Profiler
            </h3>

            {datasetInsights ? (
                <DatasetExplorer insights={datasetInsights} />
            ) : (
                <div className="glass-panel p-8 rounded-xl text-center text-gray-500 font-mono text-sm border-dashed border border-gray-700 max-w-2xl mx-auto">
                    Initiating sequence map logic... Please load pipelines initially up-call.
                </div>
            )}
        </div>
    );
}
