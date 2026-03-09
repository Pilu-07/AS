import { useState, useMemo } from 'react';
import { FixedSizeList as List } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer';
import { Search, ArrowUpDown, Filter } from 'lucide-react';

export default function DatasetExplorer({ columns = [], data = [] }) {
    const [searchTerm, setSearchTerm] = useState('');
    const [sortConfig, setSortConfig] = useState(null);

    const sortedAndFilteredData = useMemo(() => {
        let processData = [...data];

        // Filter
        if (searchTerm) {
            processData = processData.filter(row =>
                columns.some(col =>
                    String(row[col] || '').toLowerCase().includes(searchTerm.toLowerCase())
                )
            );
        }

        // Sort
        if (sortConfig !== null) {
            processData.sort((a, b) => {
                if (a[sortConfig.key] < b[sortConfig.key]) {
                    return sortConfig.direction === 'ascending' ? -1 : 1;
                }
                if (a[sortConfig.key] > b[sortConfig.key]) {
                    return sortConfig.direction === 'ascending' ? 1 : -1;
                }
                return 0;
            });
        }

        return processData;
    }, [data, columns, searchTerm, sortConfig]);

    const requestSort = (key) => {
        let direction = 'ascending';
        if (sortConfig && sortConfig.key === key && sortConfig.direction === 'ascending') {
            direction = 'descending';
        }
        setSortConfig({ key, direction });
    };

    // If no real data, create dummy for preview
    const actualData = sortedAndFilteredData.length > 0 ? sortedAndFilteredData : Array.from({ length: 5000 }).map((_, i) => {
        const row = {};
        columns.forEach((c) => row[c] = `Value ${i} - ${c}`);
        return row;
    });

    const Row = ({ index, style }) => {
        const rowData = actualData[index];
        return (
            <div style={style} className={`flex items-center border-b border-gray-800 hover:bg-gray-800/50 transition-colors ${index % 2 === 0 ? 'bg-gray-900/30' : 'bg-transparent'}`}>
                {columns.map((col, idx) => (
                    <div key={idx} className="flex-1 min-w-[150px] px-4 py-3 text-sm text-gray-300 truncate font-mono">
                        {rowData[col]}
                    </div>
                ))}
            </div>
        );
    };

    if (!columns || columns.length === 0) {
        return <div className="p-4 text-gray-400">No columns available to display.</div>;
    }

    return (
        <div className="glass-panel rounded-2xl overflow-hidden flex flex-col h-[600px] border border-gray-700 w-full mt-8">
            {/* Header / Controls */}
            <div className="p-4 bg-gray-900 border-b border-gray-800 flex items-center justify-between">
                <div className="flex items-center space-x-2 text-white">
                    <Filter className="w-5 h-5 text-indigo-400" />
                    <h3 className="font-semibold">Dataset Preview</h3>
                    <span className="text-xs text-gray-500 ml-2">({actualData.length} rows limit)</span>
                </div>

                <div className="relative w-64">
                    <input
                        type="text"
                        placeholder="Search all columns..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full bg-gray-800 border border-gray-700 text-sm text-white rounded-full pl-10 pr-4 py-2 focus:outline-none focus:border-indigo-500"
                    />
                    <Search className="w-4 h-4 text-gray-400 absolute left-4 top-2.5" />
                </div>
            </div>

            {/* Table Header */}
            <div className="flex items-center bg-gray-800/80 border-b border-gray-700 font-semibold text-xs text-gray-400 uppercase tracking-wider backdrop-blur-md sticky top-0 z-10">
                {columns.map((col, idx) => (
                    <div key={idx} className="flex-1 min-w-[150px] px-4 py-3 cursor-pointer hover:text-white hover:bg-gray-700/50 transition-colors flex items-center justify-between group" onClick={() => requestSort(col)}>
                        <span className="truncate">{col}</span>
                        <ArrowUpDown className={`w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity ${sortConfig?.key === col ? 'opacity-100 text-indigo-400' : ''}`} />
                    </div>
                ))}
            </div>

            {/* Virtualized Rows */}
            <div className="flex-1 bg-gray-900">
                <AutoSizer>
                    {({ height, width }) => (
                        <List
                            className="List"
                            height={height}
                            itemCount={actualData.length}
                            itemSize={44}
                            width={width}
                            overscanCount={5}
                        >
                            {Row}
                        </List>
                    )}
                </AutoSizer>
            </div>
        </div>
    );
}
