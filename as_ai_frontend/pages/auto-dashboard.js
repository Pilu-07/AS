import { useState, useEffect } from 'react';
import { BarChart, RefreshCw, LayoutTemplate } from 'lucide-react';
import { asAiService } from '../services/api';

export default function AutoDashboard() {
    const [charts, setCharts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchDashboard = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await asAiService.generateDashboard();
            if (res.data.dashboard_charts) {
                setCharts(res.data.dashboard_charts);
            }
        } catch (err) {
            setError('Could not generate automatic dashboard (Please upload a dataset first!)');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDashboard();
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center bg-white p-6 rounded-xl border border-gray-200">
                <div className="flex items-center space-x-4">
                    <div className="bg-indigo-100 p-3 rounded-xl text-indigo-600">
                        <LayoutTemplate size={28} />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-gray-800">Autonomous Dashboard</h1>
                        <p className="text-gray-500 text-sm">AI-generated visualizations covering correlations, distributions, and cardinality.</p>
                    </div>
                </div>
                <button
                    onClick={fetchDashboard}
                    disabled={loading}
                    className="flex items-center px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition"
                >
                    <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                    {loading ? 'Generating...' : 'Regenerate'}
                </button>
            </div>

            {error && (
                <div className="bg-red-50 text-red-600 p-4 rounded-lg border border-red-200 shadow-sm">
                    {error}
                </div>
            )}

            {charts.length === 0 && !loading && !error && (
                <div className="bg-gray-50 border-2 border-dashed border-gray-300 p-12 text-center rounded-xl">
                    <BarChart className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900">No Analytics Discovered</h3>
                    <p className="text-gray-500 mt-1">Upload a dataset to generate visual correlations autonomously.</p>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {charts.map((chartPath, idx) => (
                    <div key={idx} className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition">
                        <div className="mb-3 flex justify-between items-center px-2">
                            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider bg-gray-100 px-3 py-1 rounded-full">
                                Auto-Discovery Viz
                            </span>
                        </div>
                        <img
                            src={`http://127.0.0.1:8000${chartPath}`}
                            alt={`Auto chart ${idx}`}
                            className="w-full h-auto rounded-lg"
                            loading="lazy"
                        />
                    </div>
                ))}
            </div>
        </div>
    );
}
