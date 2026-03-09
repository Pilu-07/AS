import { useState, useEffect } from 'react';
import { Users, UserPlus, Plus, Shield, Database, LayoutDashboard } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../utils/api';
import { useRouter } from 'next/router';

export default function Teams() {
    const [teams, setTeams] = useState([]);
    const [selectedTeam, setSelectedTeam] = useState(null);
    const [teamDatasets, setTeamDatasets] = useState([]);

    // Create Team
    const [newTeamName, setNewTeamName] = useState("");
    const [creatingTeam, setCreatingTeam] = useState(false);

    // Invite User
    const [inviteEmail, setInviteEmail] = useState("");
    const [inviteRole, setInviteRole] = useState("viewer");
    const [inviting, setInviting] = useState(false);

    const router = useRouter();

    useEffect(() => {
        fetchTeams();
    }, []);

    const fetchTeams = async () => {
        try {
            const res = await api.get('/teams');
            setTeams(res.data.teams || []);
        } catch (err) {
            console.error(err);
        }
    };

    const handleCreateTeam = async () => {
        if (!newTeamName) return;
        setCreatingTeam(true);
        try {
            await api.post('/teams/create', { name: newTeamName });
            setNewTeamName("");
            fetchTeams();
        } catch (err) {
            alert("Failed to create team.");
        } finally {
            setCreatingTeam(false);
        }
    };

    const fetchTeamDatasets = async (teamId) => {
        try {
            const res = await api.get(`/teams/${teamId}/datasets`);
            setTeamDatasets(res.data.datasets || []);
            const team = teams.find(t => t.id === teamId);
            setSelectedTeam(team);
        } catch (err) {
            console.error(err);
        }
    };

    const handleInvite = async () => {
        if (!selectedTeam || !inviteEmail) return;
        setInviting(true);
        try {
            await api.post(`/teams/${selectedTeam.id}/invite`, {
                email: inviteEmail,
                role: inviteRole
            });
            alert("User invited successfully!");
            setInviteEmail("");
        } catch (err) {
            alert(err.response?.data?.detail || "Failed to invite user");
        } finally {
            setInviting(false);
        }
    };

    return (
        <div className="space-y-8 pb-12">
            <header className="mb-8 flex justify-between items-end">
                <div>
                    <motion.h1
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="text-4xl font-black text-white mb-2"
                    >
                        Collaborative <span className="text-gradient">Teams</span>
                    </motion.h1>
                    <motion.p
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 }}
                        className="text-gray-400"
                    >
                        Create workspaces, invite colleagues, and run collaborative AI analysis.
                    </motion.p>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Col: Teams List & Creation */}
                <div className="space-y-6">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                        className="glass-panel p-6 rounded-2xl"
                    >
                        <h3 className="text-xl font-bold text-white mb-4 flex items-center">
                            <Plus size={20} className="mr-2 text-indigo-400" /> New Team Workspace
                        </h3>
                        <div className="flex flex-col space-y-3">
                            <input
                                type="text"
                                placeholder="Engineering Squad..."
                                value={newTeamName}
                                onChange={(e) => setNewTeamName(e.target.value)}
                                className="w-full bg-gray-900/50 border border-gray-700 rounded-lg px-4 py-2.5 text-white placeholder-gray-500 focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
                            />
                            <button
                                onClick={handleCreateTeam}
                                disabled={creatingTeam || !newTeamName}
                                className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-2.5 rounded-lg text-sm transition-all disabled:opacity-50"
                            >
                                {creatingTeam ? 'Deploying...' : 'Create Team'}
                            </button>
                        </div>
                    </motion.div>

                    <h3 className="text-lg font-bold text-white mt-8 mb-4 border-b border-gray-800 pb-2">Your Enrollments</h3>
                    <div className="space-y-3">
                        {teams.map(team => (
                            <div
                                key={team.id}
                                onClick={() => fetchTeamDatasets(team.id)}
                                className={`p-4 rounded-xl border transition-all cursor-pointer ${selectedTeam?.id === team.id ? 'border-indigo-500 bg-indigo-500/10' : 'border-gray-800 bg-gray-900/50 hover:bg-gray-800 shrink'}`}
                            >
                                <div className="flex justify-between items-center mb-1">
                                    <h4 className="text-white font-bold">{team.name}</h4>
                                    <span className="text-xs px-2 py-1 rounded bg-gray-800 text-gray-300 font-mono border border-gray-700 capitalize">{team.role}</span>
                                </div>
                                <div className="text-xs text-gray-500">ID: WKS-{team.id}</div>
                            </div>
                        ))}
                        {teams.length === 0 && <div className="text-sm text-gray-500 italic">You aren't in any teams yet.</div>}
                    </div>
                </div>

                {/* Right Col: Active Team Workspace */}
                <div className="lg:col-span-2">
                    {selectedTeam ? (
                        <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} className="glass-panel p-8 rounded-2xl h-full border border-indigo-500/20 shadow-[0_0_30px_rgba(99,102,241,0.05)]">
                            <div className="flex justify-between items-start mb-8">
                                <div>
                                    <h2 className="text-3xl font-black text-white">{selectedTeam.name} Space</h2>
                                    <p className="text-gray-400 mt-1">Manage collaborators and shared dataset operations.</p>
                                </div>
                                <div className="bg-indigo-500/10 text-indigo-400 px-3 py-1 rounded-full text-sm font-bold border border-indigo-500/30 flex items-center">
                                    <Shield size={16} className="mr-2" /> Role: {selectedTeam.role.toUpperCase()}
                                </div>
                            </div>

                            {/* Invitation Box */}
                            {['owner', 'editor'].includes(selectedTeam.role) && (
                                <div className="bg-gray-900/50 p-6 rounded-xl border border-gray-800 mb-8 border-dashed">
                                    <h4 className="text-white font-bold mb-3 flex items-center"><UserPlus size={18} className="mr-2 text-cyan-400" /> Invite Collaborator</h4>
                                    <div className="flex space-x-3">
                                        <input
                                            type="email"
                                            placeholder="colleague@example.com"
                                            value={inviteEmail}
                                            onChange={(e) => setInviteEmail(e.target.value)}
                                            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white outline-none focus:border-cyan-500"
                                        />
                                        <select
                                            value={inviteRole}
                                            onChange={(e) => setInviteRole(e.target.value)}
                                            className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white outline-none focus:border-cyan-500"
                                        >
                                            <option value="viewer">Viewer</option>
                                            <option value="editor">Editor</option>
                                        </select>
                                        <button
                                            onClick={handleInvite}
                                            disabled={inviting || !inviteEmail}
                                            className="bg-cyan-600 hover:bg-cyan-500 text-white font-bold px-6 py-2 rounded-lg transition-colors disabled:opacity-50"
                                        >
                                            Send Invite
                                        </button>
                                    </div>
                                </div>
                            )}

                            {/* Shared Datasets */}
                            <div>
                                <h4 className="text-white font-bold mb-4 flex items-center border-b border-gray-800 pb-2"><Database size={18} className="mr-2 text-indigo-400" /> Synced Datasets</h4>

                                {teamDatasets.length === 0 ? (
                                    <div className="text-center p-8 bg-gray-900/30 rounded-xl border border-gray-800 border-dashed text-gray-500">
                                        No datasets uploaded to this team workspace yet.
                                        {['owner', 'editor'].includes(selectedTeam.role) &&
                                            <div className="mt-2 text-sm text-indigo-400 cursor-pointer hover:underline" onClick={() => router.push('/datasets')}>Go to Datasets to upload</div>
                                        }
                                    </div>
                                ) : (
                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                        {teamDatasets.map(d => (
                                            <div key={d.id} className="bg-gray-800/80 p-5 rounded-xl border border-gray-700 hover:border-indigo-500/50 transition-colors">
                                                <h5 className="text-white font-bold mb-1 truncate">{d.name}</h5>
                                                <div className="text-xs text-gray-400 font-mono mb-4">{d.rows.toLocaleString()} rows • {d.columns} cols</div>
                                                <button
                                                    onClick={() => router.push('/auto-dashboard')}
                                                    className="w-full bg-indigo-600/20 text-indigo-400 hover:bg-indigo-600/40 font-bold py-2 rounded-lg text-sm transition-colors flex items-center justify-center"
                                                >
                                                    <LayoutDashboard size={16} className="mr-2" /> View Analysis
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    ) : (
                        <div className="h-full min-h-[400px] glass-panel rounded-2xl border border-gray-800 border-dashed flex items-center justify-center flex-col text-gray-500">
                            <Users size={48} className="mb-4 text-gray-600 opacity-50" />
                            <p className="font-medium text-lg text-gray-400">Select a Workspace</p>
                            <p className="max-w-xs text-center mt-2 text-sm">Choose an existing team or create a new one to manage collaboration.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
