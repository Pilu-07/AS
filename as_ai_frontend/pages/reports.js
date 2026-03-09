import { useState } from 'react';
import { FileText, Download } from 'lucide-react';
import { asAiService } from '../services/api';

export default function Reports() {
    const [loading, setLoading] = useState(false);
    const [reportUrl, setReportUrl] = useState(null);
    const [error, setError] = useState(null);

    const handleGenerate = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await asAiService.generateReport('dataset_1');
            if (res.data.pdf_report) {
                setReportUrl(`http://127.0.0.1:8000${res.data.pdf_report}`);
            }
        } catch (err) {
            setError('Failed to generate automatic executive report. Ensure models have trained on the dataset.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-3xl mx-auto space-y-6">
            <div className="text-center bg-gradient-to-br from-indigo-900 to-purple-800 p-12 rounded-2xl shadow-xl text-white">
                <FileText size={48} className="mx-auto mb-4 text-indigo-200" />
                <h1 className="text-3xl font-bold mb-2">Strategic AI PDF Reports</h1>
                <p className="text-indigo-200 mb-8 max-w-lg mx-auto">
                    Aggregate all charts, models, anomalous structures, and insights into a highly formulated multi-page PDF briefing.
                </p>

                <button
                    onClick={handleGenerate}
                    disabled={loading}
                    className="bg-white text-indigo-900 px-8 py-3 rounded-full font-bold shadow-lg hover:bg-gray-50 transition flex items-center justify-center mx-auto"
                >
                    {loading ? (
                        <span className="flex items-center"><div className="w-5 h-5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mr-3"></div> Assembling Document...</span>
                    ) : (
                        'Generate Executive Briefing'
                    )}
                </button>
            </div>

            {error && (
                <div className="bg-red-50 text-red-600 p-4 rounded-xl border border-red-100 text-center font-medium">
                    {error}
                </div>
            )}

            {reportUrl && (
                <div className="bg-white p-8 rounded-xl border border-gray-200 shadow-sm text-center">
                    <div className="bg-emerald-50 text-emerald-600 p-4 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                        <Download size={24} />
                    </div>
                    <h3 className="text-xl font-bold text-gray-800 mb-2">Report Compilation Successful</h3>
                    <p className="text-gray-500 mb-6">Your dataset evaluation has been mapped chronologically using ReportLab engines.</p>
                    <a
                        href={reportUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-block bg-indigo-50 border border-indigo-200 text-indigo-700 px-6 py-2 rounded-lg font-bold hover:bg-indigo-100 transition"
                    >
                        Download PDF Standard
                    </a>
                </div>
            )}
        </div>
    );
}
