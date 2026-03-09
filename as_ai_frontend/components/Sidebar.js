import Link from 'next/link';
import { useRouter } from 'next/router';
import {
    LayoutDashboard,
    Database,
    MessageSquare,
    BarChart,
    Activity,
    FileText,
    BrainCircuit,
    Cpu,
    ShieldAlert,
    Presentation,
    Microscope,
    LogOut,
    Users,
    Code
} from 'lucide-react';

const Sidebar = () => {
    const router = useRouter();

    const navItems = [
        { name: 'Command Center', path: '/', icon: <LayoutDashboard size={20} /> },
        { name: 'Team Workspaces', path: '/teams', icon: <Users size={20} /> },
        { name: 'Data Hub', path: '/datasets', icon: <Database size={20} /> },
        { name: 'AI Analyst', path: '/ai-analyst', icon: <Code size={20} /> },
        { name: 'Auto Dashboard', path: '/auto-dashboard', icon: <BarChart size={20} /> },
        { name: 'Model Hub', path: '/model-lab', icon: <BrainCircuit size={20} /> },
        { name: 'Stream Monitor', path: '/streaming', icon: <Activity size={20} /> },
        { name: 'Anomaly Monitor', path: '/anomaly-monitor', icon: <ShieldAlert size={20} /> },
        { name: 'Story Engine', path: '/storytelling', icon: <Presentation size={20} /> },
        { name: 'Research Lab', path: '/research', icon: <Microscope size={20} /> },
        { name: 'Reports', path: '/reports', icon: <FileText size={20} /> },
    ];

    return (
        <div className="flex flex-col w-64 h-screen bg-[#0B0F19] border-r border-[#1f2937] text-gray-300 fixed z-10 glass-panel">
            <div className="flex items-center px-6 h-20 border-b border-gray-800/50 space-x-3">
                <div className="p-2 bg-gradient-to-br from-indigo-500 to-cyan-500 rounded-lg shadow-[0_0_15px_rgba(99,102,241,0.5)]">
                    <Cpu className="text-white h-6 w-6" />
                </div>
                <h1 className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400 tracking-tight">
                    AS-AI <span className="text-indigo-400 font-medium text-lg ml-1">OS</span>
                </h1>
            </div>
            <div className="flex-1 overflow-y-auto py-6">
                <div className="px-4 mb-2 text-xs font-bold text-gray-500 uppercase tracking-widest">Platform</div>
                <ul className="space-y-1 px-3">
                    {navItems.map((item) => (
                        <li key={item.path}>
                            <Link href={item.path}>
                                <div
                                    className={`flex items-center px-3 py-3 rounded-lg cursor-pointer transition-all duration-200 ${router.pathname === item.path
                                        ? 'bg-indigo-500/10 text-indigo-400 font-semibold border border-indigo-500/20 shadow-[inset_0_0_10px_rgba(99,102,241,0.1)]'
                                        : 'hover:bg-gray-800/50 hover:text-white border border-transparent'
                                        }`}
                                >
                                    <span className={`mr-3 ${router.pathname === item.path ? 'text-indigo-400' : 'text-gray-400'}`}>
                                        {item.icon}
                                    </span>
                                    <span>{item.name}</span>
                                </div>
                            </Link>
                        </li>
                    ))}
                </ul>
            </div>
            <div className="p-4 border-t border-gray-800/50 space-y-3">
                <div className="bg-gray-800/30 rounded-lg p-3 flex items-center space-x-3 border border-gray-700/30">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_5px_rgba(16,185,129,0.8)]"></div>
                    <span className="text-xs text-gray-400 font-medium tracking-wide">Kernel Online</span>
                </div>

                <button
                    onClick={() => {
                        localStorage.removeItem('as_ai_token');
                        router.push('/login');
                    }}
                    className="w-full flex items-center justify-center space-x-2 px-3 py-2 text-sm text-red-400 hover:text-white hover:bg-red-500/20 rounded-lg transition-colors border border-transparent hover:border-red-500/30"
                >
                    <LogOut size={16} />
                    <span className="font-semibold">Sign Out</span>
                </button>
            </div>
        </div>
    );
};

export default Sidebar;
