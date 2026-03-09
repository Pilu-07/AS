import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { Activity, LayoutDashboard, Database, ArrowLeft } from 'lucide-react';
import { motion } from 'framer-motion';
import api from '../../utils/api';
import DynamicChart from '../../components/DynamicChart';

export default function DashboardView() {
    const router = useRouter();
    const { id } = router.query;

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [config, setConfig] = useState(null);
    const [dataRows, setDataRows] = useState([]);

    useEffect(() => {
        if (!id) return;

        const fetchDashboardData = async () => {
            setLoading(true);
            try {
                // Fetch UI config and underlying raw data in parallel
                const [configRes, dataRes] = await Promise.all([
                    api.get(`/datasets/${id}/dashboard`),
                    api.get(`/datasets/${id}/data?limit=1000`)
                ]);

                setConfig(configRes.data);
                setDataRows(dataRes.data.data || []);
            } catch (err) {
                console.error("Failed to fetch dashboard", err);
                setError(err.response?.data?.detail || "Failed to load dashboard data. Ensure the dataset exists.");
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, [id]);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-screen space-y-4">
                <Activity size={40} className="animate-spin text-indigo-500" />
                <p className="text-gray-400 font-mono animate-pulse">Assembling Analytical Dashboard...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-8">
                <button onClick={() => router.push('/datasets')} className="flex items-center text-gray-400 hover:text-white mb-6 transition-colors">
                    <ArrowLeft size={16} className="mr-2" /> Back to Workspaces
                </button>
                <div className="glass-panel p-8 rounded-xl border-red-500/30 text-center">
                    <h2 className="text-xl font-bold text-red-400 mb-2">Dashboard Error</h2>
                    <p className="text-gray-400">{error}</p>
                </div>
            </div>
        );
    }

    const hasKpis = config?.kpis && config.kpis.length > 0;
    const hasCharts = config?.charts && config.charts.length > 0;

    if (!hasKpis && !hasCharts) {
        return (
            <div className="p-8">
                <button onClick={() => router.push('/datasets')} className="flex items-center text-gray-400 hover:text-white mb-6 transition-colors">
                    <ArrowLeft size={16} className="mr-2" /> Back to Workspaces
                </button>
                <div className="glass-panel p-16 rounded-xl border-dashed border-gray-700 text-center max-w-2xl mx-auto">
                    <Database size={48} className="mx-auto text-gray-600 mb-4" />
                    <h2 className="text-xl font-bold text-gray-300 mb-2">No Dashboard Configured</h2>
                    <p className="text-gray-500">The background engine is still analyzing this dataset, or it did not contain enough numerical features to generate an autonomous dashboard. Please try again in to few seconds.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-8 pb-12">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center space-x-4">
                    <button onClick={() => router.push('/datasets')} className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-gray-400 hover:text-white transition-colors">
                        <ArrowLeft size={20} />
                    </button>
                    <div>
                        <h1 className="text-3xl font-black text-white flex items-center">
                            <LayoutDashboard className="mr-3 text-indigo-400" size={32} />
                            AI Generated <span className="text-gradient ml-2">Analytics</span>
                        </h1>
                        <p className="text-gray-400 text-sm mt-1">Autonomous intelligence extracted from dataset {id}</p>
                    </div>
                </div>
            </div>

            {/* KPIs Grid */}
            {hasKpis && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {config.kpis.map((kpi, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="glass-panel p-6 rounded-2xl border border-gray-800 bg-gradient-to-br from-indigo-900/20 to-gray-900/50"
                        >
                            <h3 className="text-gray-400 text-xs uppercase font-bold tracking-widest mb-2 truncate" title={kpi.label}>{kpi.label}</h3>
                            <p className="text-3xl font-black text-white truncate" title={String(kpi.value)}>{kpi.value}</p>
                        </motion.div>
                    ))}
                </div>
            )}

            {/* Charts Grid */}
            {hasCharts && (
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mt-8">
                    {config.charts.map((chartConfig, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.2 + (index * 0.1) }}
                            className="glass-panel p-6 rounded-2xl border border-gray-800 hover:border-indigo-500/30 transition-colors"
                        >
                            <DynamicChart config={chartConfig} data={dataRows} />
                        </motion.div>
                    ))}
                </div>
            )}
        </div>
    );
}
