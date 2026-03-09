import React from 'react';
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
    Filler
);

export default function DynamicChart({ config, data }) {
    if (!config || !data || data.length === 0) {
        return <div className="flex items-center justify-center h-full text-gray-500 font-mono text-sm">Waiting for telemetry...</div>;
    }

    const { type, x, y, title } = config;

    // Safety check just in case the dataset doesn't map cleanly
    if (!x) return <div className="text-gray-500">Invalid Chart Config: Missing X-Axis</div>;

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            },
            title: {
                display: false
            },
            tooltip: {
                backgroundColor: 'rgba(15, 23, 42, 0.9)',
                titleColor: '#fff',
                bodyColor: '#cbd5e1',
                borderColor: '#334155',
                borderWidth: 1,
                padding: 10,
                displayColors: true,
            }
        },
        scales: {
            x: {
                grid: {
                    color: 'rgba(255, 255, 255, 0.05)',
                },
                ticks: {
                    color: '#94a3b8',
                    font: { size: 10 }
                }
            },
            y: {
                grid: {
                    color: 'rgba(255, 255, 255, 0.05)',
                },
                ticks: {
                    color: '#94a3b8',
                    font: { size: 10 }
                }
            }
        }
    };

    const processData = () => {
        if (type === 'bar' || type === 'histogram') {
            // We aggregate counts if y is 'count', else we just map y
            if (y === 'count' || type === 'histogram') {
                const counts = {};
                data.forEach(row => {
                    const val = row[x];
                    if (val !== null && val !== undefined) {
                        counts[val] = (counts[val] || 0) + 1;
                    }
                });

                // Sort categories or numerical bins for better display
                const sortedKeys = Object.keys(counts).sort((a, b) => {
                    if (!isNaN(a) && !isNaN(b)) return Number(a) - Number(b);
                    return counts[b] - counts[a]; // Frequency sort for categorical
                }).slice(0, 50); // limit to top 50

                return {
                    labels: sortedKeys,
                    datasets: [{
                        label: 'Frequency',
                        data: sortedKeys.map(k => counts[k]),
                        backgroundColor: 'rgba(99, 102, 241, 0.5)',
                        borderColor: 'rgba(99, 102, 241, 1)',
                        borderWidth: 1,
                        borderRadius: 4
                    }]
                };
            }
        }

        if (type === 'line') {
            // Sort data by X axis (usually time)
            const sortedData = [...data].sort((a, b) => new Date(a[x]) - new Date(b[x]));
            // Limit to avoid crashing browser on massive lines
            const slicedData = sortedData.slice(0, 500);
            return {
                labels: slicedData.map(d => String(d[x]).slice(0, 10)),
                datasets: [{
                    label: y,
                    data: slicedData.map(d => d[y]),
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0
                }]
            };
        }

        if (type === 'scatter') {
            return {
                datasets: [{
                    label: `${x} vs ${y}`,
                    data: data.slice(0, 500).map(d => ({ x: d[x], y: d[y] })),
                    backgroundColor: 'rgba(52, 211, 153, 0.5)',
                    borderColor: 'rgba(52, 211, 153, 1)',
                    borderWidth: 1,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            };
        }

        // Default fallback (bar mapping literal x and y)
        return {
            labels: data.slice(0, 50).map(d => d[x]),
            datasets: [{
                label: y || 'Value',
                data: data.slice(0, 50).map(d => d[y]),
                backgroundColor: 'rgba(167, 139, 250, 0.5)',
                borderColor: 'rgba(167, 139, 250, 1)',
                borderWidth: 1
            }]
        };
    };

    const chartData = processData();

    return (
        <div className="w-full h-full relative">
            <h4 className="text-gray-300 font-bold text-sm mb-4 tracking-wide uppercase">{title || `${type} chart`}</h4>
            <div className="h-[250px] w-full">
                {type === 'line' && <Line options={chartOptions} data={chartData} />}
                {(type === 'bar' || type === 'histogram') && <Bar options={chartOptions} data={chartData} />}
                {type === 'scatter' &&
                    <Scatter
                        options={{
                            ...chartOptions,
                            scales: {
                                x: { ...chartOptions.scales.x, title: { display: true, text: x, color: '#94a3b8' } },
                                y: { ...chartOptions.scales.y, title: { display: true, text: y, color: '#94a3b8' } }
                            }
                        }}
                        data={chartData}
                    />
                }
            </div>
        </div>
    );
}
