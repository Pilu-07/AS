import { motion } from 'framer-motion';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    Title,
    Tooltip,
    Legend,
    Filler
} from 'chart.js';
import zoomPlugin from 'chartjs-plugin-zoom';
import { Line, Bar, Scatter } from 'react-chartjs-2';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    Title,
    Tooltip,
    Legend,
    Filler,
    zoomPlugin
);

export default function AnimatedChart({ type = 'line', data, options = {}, title }) {
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 1000,
            easing: 'easeOutQuart',
        },
        plugins: {
            legend: {
                labels: { color: '#9CA3AF' }
            },
            tooltip: {
                backgroundColor: 'rgba(17, 24, 39, 0.9)',
                titleColor: '#F3F4F6',
                bodyColor: '#D1D5DB',
                borderColor: 'rgba(99, 102, 241, 0.5)',
                borderWidth: 1,
                padding: 12,
                boxPadding: 6,
                usePointStyle: true,
            },
            zoom: {
                pan: {
                    enabled: true,
                    mode: 'x',
                },
                zoom: {
                    wheel: { enabled: true },
                    pinch: { enabled: true },
                    mode: 'x',
                }
            }
        },
        scales: {
            x: {
                grid: { color: 'rgba(255, 255, 255, 0.05)' },
                ticks: { color: '#6B7280' }
            },
            y: {
                grid: { color: 'rgba(255, 255, 255, 0.05)' },
                ticks: { color: '#6B7280' }
            }
        },
        ...options
    };

    const renderChart = () => {
        switch (type) {
            case 'bar':
                return <Bar data={data} options={defaultOptions} />;
            case 'scatter':
                return <Scatter data={data} options={defaultOptions} />;
            case 'line':
            default:
                return <Line data={data} options={defaultOptions} />;
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
            className="w-full h-full relative"
        >
            {title && <h3 className="text-gray-300 font-semibold mb-4 tracking-wide text-sm uppercase">{title}</h3>}
            <div className="w-full" style={{ height: title ? 'calc(100% - 2rem)' : '100%' }}>
                {renderChart()}
            </div>
        </motion.div>
    );
}
