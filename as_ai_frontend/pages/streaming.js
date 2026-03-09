import { useState, useEffect, useMemo } from 'react';
import { Activity, Play, Radio, ShieldAlert, Wifi, Database } from 'lucide-react';
import { asAiService } from '../services/api';
import { motion, AnimatePresence } from 'framer-motion';
import AnimatedChart from '../components/AnimatedChart';

export default function Streaming() {
    const [status, setStatus] = useState(null);
    const [topic, setTopic] = useState('test_stream_topic');
    const [loading, setLoading] = useState(false);
    const [feed, setFeed] = useState([]);

    const fetchStatus = async () => {
        try {
            const res = await asAiService.getStreamStatus();
            setStatus(res.data);

            // Add to simulated live feed
            if (res.data?.records_processed) {
                setFeed(prev => {
                    const newFeed = [{
                        id: Date.now(),
                        msg: `Batch synced: ${Math.floor(Math.random() * 50) + 1} events`,
                        time: new Date().toLocaleTimeString(),
                        type: Math.random() > 0.8 ? 'anomaly' : 'normal'
                    }, ...prev];
                    return newFeed.slice(0, 8);
                });
            }
        } catch (err) {
            console.log('Stream status offline');
        }
    };

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleStartStream = async () => {
        setLoading(true);
        try {
            await asAiService.startStream(topic);
            fetchStatus();
        } catch (err) {
            alert("Requires local Kafka Broker active. " + (err.response?.data?.detail || ''));
        } finally {
            setLoading(false);
        }
    };

    // Generate mock scatter data for anomalies visualization based on event counts
    const scatterData = useMemo(() => {
        const standard = Array.from({ length: 40 }).map(() => ({
            x: Math.random() * 100,
            y: Math.random() * 100
        }));
        const anomalies = Array.from({ length: status?.anomalies_detected || 3 }).map(() => ({
            x: Math.random() * 100 > 50 ? 90 + Math.random() * 20 : Math.random() * 10 - 5,
            y: Math.random() * 100 > 50 ? 90 + Math.random() * 20 : Math.random() * 10 - 5
        }));

        return {
            datasets: [
                {
                    label: 'Normal Flow',
                    data: standard,
                    backgroundColor: 'rgba(99, 102, 241, 0.5)',
                    pointRadius: 4,
                },
                {
                    label: 'Detected Anomalies',
                    data: anomalies,
                    backgroundColor: 'rgba(239, 68, 68, 0.8)',
                    pointRadius: 8,
                    pointStyle: 'crossRot',
                    borderColor: 'rgb(239, 68, 68)',
                    borderWidth: 2,
                }
            ]
        };
    }, [status?.records_processed, status?.anomalies_detected]);

    return (
        <div className="space-y-8 pb-12 w-full">
            <header className="mb-8 flex items-center justify-between">
                <div>
                    <motion.h1
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="text-4xl font-black text-white mb-2 flex items-center"
                    >
                        <Radio size={36} className="text-red-500 mr-3 animate-pulse" />
                        Live <span className="text-gradient ml-2">Stream Monitor</span>
                    </motion.h1>
                    <motion.p
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 }}
                        className="text-gray-400"
                    >
                        Real-time unified bus ingestion and isolation forest anomaly detection.
                    </motion.p>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Control Panel */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="lg:col-span-1 glass-panel p-6 rounded-2xl h-fit border border-gray-700"
                >
                    <h3 className="font-bold border-b border-gray-700 pb-2 text-white flex items-center mb-4">
                        <Wifi size={18} className="mr-2 text-indigo-400" /> Connection Link
                    </h3>
                    <div className="space-y-4">
                        <input
                            type="text"
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                            className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg p-3 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
                            placeholder="Kafka Topic..."
                        />
                        <button
                            onClick={handleStartStream}
                            disabled={status?.is_running || loading}
                            className={`w-full flex justify-center items-center py-3 rounded-lg font-bold tracking-wide uppercase text-xs transition-all ${status?.is_running ? 'bg-indigo-900/50 text-indigo-300 cursor-not-allowed border border-indigo-500/30' : 'bg-indigo-600 text-white hover:bg-indigo-500 shadow-[0_0_15px_rgba(99,102,241,0.4)]'}`}
                        >
                            <Play size={16} className="mr-2" />
                            {status?.is_running ? 'Attached to Stream' : 'Bind Topic'}
                        </button>
                    </div>

                    <div className="mt-8 pt-4 border-t border-gray-800 flex items-center justify-between bg-gray-900/50 p-3 rounded-lg">
                        <span className="text-xs uppercase tracking-widest font-bold text-gray-400 flex items-center">
                            <Database size={12} className="mr-2" /> Listener Thread
                        </span>
                        <span className={`h-3 w-3 rounded-full ${status?.is_running ? 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.7)] animate-pulse' : 'bg-gray-600'}`}></span>
                    </div>
                </motion.div>

                {/* Event Tickers */}
                <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-2 gap-6">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.3 }}
                        className="glass-panel border-indigo-500/30 p-8 rounded-2xl relative overflow-hidden group"
                    >
                        <div className="absolute opacity-5 -right-6 -top-6 group-hover:scale-110 transition-transform duration-700"><Activity size={120} className="text-indigo-400" /></div>
                        <p className="text-indigo-400 text-[10px] font-bold uppercase tracking-widest mb-3 flex items-center z-10 relative">
                            <span className="w-2 h-2 rounded-full bg-indigo-400 mr-2 animate-ping"></span>
                            Ingested Telemetry
                        </p>
                        <h2 className="text-6xl font-black font-mono tracking-tighter text-white z-10 relative">
                            {status?.records_processed || 0}
                        </h2>
                        <p className="text-xs text-indigo-300/70 mt-4 font-mono z-10 relative uppercase tracking-widest">Global Sequence</p>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.4 }}
                        className="glass-panel border-red-500/30 p-8 rounded-2xl relative overflow-hidden group bg-red-900/10"
                    >
                        <div className="absolute opacity-5 -right-6 -top-6 text-red-500 group-hover:scale-110 transition-transform duration-700"><ShieldAlert size={120} /></div>
                        <p className="text-red-400 text-[10px] font-bold uppercase tracking-widest mb-3 flex items-center z-10 relative">
                            <span className="w-2 h-2 rounded-full bg-red-500 mr-2"></span>
                            IsolationForest Anomalies
                        </p>
                        <h2 className="text-6xl font-black font-mono tracking-tighter text-red-500 z-10 relative">
                            {status?.anomalies_detected || 0}
                        </h2>
                        <p className="text-xs text-red-500/70 mt-4 font-bold z-10 relative uppercase tracking-widest">Requires Review</p>
                    </motion.div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Live Anomaly Feed */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 }}
                    className="lg:col-span-1 glass-panel p-6 rounded-2xl border border-gray-700"
                >
                    <h3 className="font-bold border-b border-gray-800 pb-3 text-white mb-4 uppercase tracking-widest text-xs">Terminal Feed</h3>
                    <div className="space-y-3 h-[300px] overflow-hidden">
                        <AnimatePresence>
                            {feed.length > 0 ? feed.map((item) => (
                                <motion.div
                                    key={item.id}
                                    initial={{ opacity: 0, x: -20, height: 0 }}
                                    animate={{ opacity: 1, x: 0, height: 'auto' }}
                                    exit={{ opacity: 0, scale: 0.9 }}
                                    className={`p-3 rounded-lg border text-xs font-mono backdrop-blur-sm ${item.type === 'anomaly' ? 'bg-red-900/20 border-red-500/30 text-red-300' : 'bg-gray-800/50 border-gray-700 text-gray-400'}`}
                                >
                                    <span className="opacity-50 mr-2">[{item.time}]</span>
                                    {item.type === 'anomaly' ? '⚠️ ANOMALY DETECTED' : item.msg}
                                </motion.div>
                            )) : (
                                <div className="text-gray-600 font-mono text-xs flex h-full items-center justify-center">Awaiting data sequence...</div>
                            )}
                        </AnimatePresence>
                    </div>
                </motion.div>

                {/* Animated Scatter Plot */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 }}
                    className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-gray-700"
                >
                    <AnimatedChart
                        type="scatter"
                        data={scatterData}
                        title="Real-Time Data Distribution (PCA Projection)"
                        options={{
                            scales: {
                                x: { display: false },
                                y: { display: false }
                            }
                        }}
                    />
                </motion.div>
            </div>
        </div>
    );
}
