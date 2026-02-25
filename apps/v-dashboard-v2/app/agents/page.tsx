"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Shield,
    Zap,
    Cpu,
    ArrowLeft,
    Plus,
    Play,
    Square,
    Terminal as TerminalIcon,
    MoreVertical,
    Activity,
    Search as SearchIcon,
    MessageCircle,
    BrainCircuit,
    Settings2,
    Loader2
} from "lucide-react";
import { useRouter } from "next/navigation";
import { agentApi } from "@/lib/agents";
import { cn } from "@/lib/utils";

export default function AgentWarRoom() {
    const [agents, setAgents] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showForge, setShowForge] = useState(false);
    const [selectedSector, setSelectedSector] = useState("Travel CRM");
    const router = useRouter();

    // New Agent Form State
    const [newAgent, setNewAgent] = useState({
        name: "",
        agent_type: "GENERAL_SUPPORT",
        system_prompt: "",
    });

    const sectors = ["Travel CRM", "Real Estate", "Tech Sales", "Global Support"];

    useEffect(() => {
        fetchAgents();
    }, []);

    const fetchAgents = async () => {
        try {
            const data = await agentApi.list();
            setAgents(data);
        } catch (err) {
            console.error("Failed to fetch agents", err);
            setError("Communication link severed. Retry auth.");
        } finally {
            setLoading(false);
        }
    };

    const handleCreateAgent = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await agentApi.create(newAgent);
            setShowForge(false);
            setNewAgent({ name: "", agent_type: "GENERAL_SUPPORT", system_prompt: "" });
            fetchAgents();
        } catch (err) {
            alert("Failed to forge agent");
        }
    };

    const toggleAgent = async (agent: any) => {
        const action = agent.status === "RUNNING" ? "stop" : "start";
        try {
            await agentApi.control(agent.id, action);
            fetchAgents();
        } catch (err) {
            alert("Neural command failed");
        }
    };

    const deleteAgent = async (id: number) => {
        if (!confirm("Decommission this agent?")) return;
        try {
            await agentApi.delete(id);
            fetchAgents();
        } catch (err) {
            alert("Decommissioning failed");
        }
    };

    return (
        <main className="min-h-screen bg-black text-slate-100 font-mono relative overflow-hidden">
            {/* Background Grid Mesh */}
            <div className="fixed inset-0 bg-[linear-gradient(to_right,#161618_1px,transparent_1px),linear-gradient(to_bottom,#161618_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none opacity-50" />

            {/* Header */}
            <header className="relative z-20 border-b border-white/5 bg-black/50 backdrop-blur-md p-4">
                <div className="max-w-7xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => router.push("/")}
                            className="p-2 hover:bg-white/10 rounded-full transition-colors"
                        >
                            <ArrowLeft className="w-5 h-5 text-zinc-500" />
                        </button>
                        <div>
                            <h1 className="text-xl font-bold tracking-tighter uppercase italic flex items-center gap-2">
                                <Shield className="w-5 h-5 text-primary glow-green" />
                                Vortex <span className="text-zinc-500 font-normal ml-1">//</span> Agent War Room
                            </h1>
                            <p className="text-[10px] text-zinc-500 uppercase tracking-widest mt-0.5">Neural Deployment Console v2.4.0</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-6">
                        <div className="hidden md:flex flex-col text-right">
                            <span className="text-[10px] text-zinc-500 uppercase">Neural Status</span>
                            <span className="text-xs text-primary font-bold uppercase tracking-widest">Active Link</span>
                        </div>
                        <button
                            onClick={() => setShowForge(true)}
                            className="bg-primary text-black px-6 py-2 rounded-sm font-bold uppercase text-xs hover:bg-primary/90 transition-all flex items-center gap-2 shadow-[0_0_20px_-5px_rgba(34,197,94,0.5)]"
                        >
                            <Plus className="w-4 h-4" /> Forge New Agent
                        </button>
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto flex h-[calc(100vh-73px)] relative z-10">
                {/* Sidebar: Sectors */}
                <aside className="w-64 border-r border-white/5 p-6 space-y-8 bg-white/[0.01]">
                    <div>
                        <h3 className="text-[10px] uppercase font-bold text-zinc-500 tracking-[0.2em] mb-4">Neural Sectors</h3>
                        <div className="space-y-1">
                            {sectors.map((sector) => (
                                <button
                                    key={sector}
                                    onClick={() => setSelectedSector(sector)}
                                    className={cn(
                                        "w-full text-left px-4 py-3 text-xs rounded-sm transition-all flex items-center justify-between group",
                                        selectedSector === sector ? "bg-primary/10 border-l-2 border-primary text-primary" : "text-zinc-500 hover:bg-white/5"
                                    )}
                                >
                                    {sector}
                                    {selectedSector === sector && <Activity className="w-3 h-3 animate-pulse" />}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="pt-8 border-t border-white/5">
                        <div className="bg-zinc-900/50 p-4 rounded-sm border border-zinc-800">
                            <h4 className="text-[10px] font-bold uppercase text-zinc-400 mb-2">Global Heatmap</h4>
                            <div className="h-24 bg-black/50 rounded-sm flex items-center justify-center">
                                <span className="text-[9px] text-zinc-600 uppercase italic">Calibrating...</span>
                            </div>
                        </div>
                    </div>
                </aside>

                {/* Main: Swarm Grid */}
                <section className="flex-1 p-8 overflow-y-auto">
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h2 className="text-sm uppercase tracking-[0.3em] text-zinc-500 mb-1">Active Swarm grid</h2>
                            <p className="text-2xl font-bold tracking-tighter uppercase italic">{selectedSector} <span className="text-zinc-500">// Units</span></p>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="flex -space-x-2">
                                {[1, 2, 3].map(i => (
                                    <div key={i} className="w-8 h-8 rounded-full border-2 border-black bg-zinc-800 flex items-center justify-center text-[10px] font-bold">A{i}</div>
                                ))}
                            </div>
                            <span className="text-[10px] text-zinc-500 ml-2">86% Efficiency</span>
                        </div>
                    </div>

                    {loading ? (
                        <div className="h-64 flex flex-col items-center justify-center gap-4">
                            <Loader2 className="w-10 h-10 text-primary animate-spin" />
                            <p className="text-xs uppercase tracking-widest text-zinc-500">Syncing Neurons...</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                            {agents.length === 0 ? (
                                <div className="col-span-full h-64 border border-dashed border-zinc-800 rounded-sm flex flex-col items-center justify-center text-zinc-500 gap-4">
                                    <Cpu className="w-12 h-12 opacity-20" />
                                    <p className="text-xs uppercase tracking-[0.2em]">No agents deployed in this sector.</p>
                                    <button onClick={() => setShowForge(true)} className="text-primary text-[10px] font-bold uppercase hover:underline">Forge First Unit</button>
                                </div>
                            ) : (
                                agents.map((agent) => (
                                    <AgentCard key={agent.id} agent={agent} onToggle={() => toggleAgent(agent)} onDelete={() => deleteAgent(agent.id)} />
                                ))
                            )}
                        </div>
                    )}
                </section>

                {/* Intelligence Stream */}
                <aside className="w-96 border-l border-white/5 bg-black/80 backdrop-blur-xl p-6 flex flex-col">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-2">
                            <TerminalIcon className="w-4 h-4 text-primary" />
                            <h3 className="text-[10px] uppercase font-bold text-zinc-400 tracking-[0.2em]">Intelligence Stream</h3>
                        </div>
                        <div className="flex gap-1">
                            <div className="w-1 h-1 bg-primary rounded-full animate-ping" />
                            <span className="text-[9px] text-zinc-600 uppercase">Live</span>
                        </div>
                    </div>

                    <div className="flex-1 bg-black/90 rounded-sm border border-zinc-800 p-4 font-mono text-[10px] overflow-y-auto space-y-2 text-zinc-400">
                        <p className="text-primary/70">[17:42:01] System boot complete.</p>
                        <p className="text-zinc-600">[17:42:05] Establishing ZeroClaw neural bridge... OK</p>
                        <p className="text-secondary/70">[17:42:10] Sector '{selectedSector}' identified.</p>
                        <p className="text-zinc-600">[17:42:15] Monitoring 4 ingress channels.</p>
                        <p className="text-primary/70">[17:43:00] [CLOSER-1] Outbound burst scheduled.</p>
                        <p className="text-orange-500/70">[17:44:22] [WARNING] Latency spike detected in sector pulse.</p>
                        <p className="text-zinc-300">[17:45:01] [SCOUT-A] Scanned 12 targets. 3 marked for extraction.</p>
                        <div className="w-1.5 h-3 bg-primary/50 animate-pulse inline-block align-middle ml-1" />
                    </div>
                </aside>
            </div>

            {/* Forge Panel (Overlay) */}
            <AnimatePresence>
                {showForge && (
                    <>
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setShowForge(false)}
                            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-40"
                        />
                        <motion.div
                            initial={{ x: "100%" }}
                            animate={{ x: 0 }}
                            exit={{ x: "100%" }}
                            transition={{ type: "spring", damping: 25, stiffness: 200 }}
                            className="fixed top-0 right-0 h-full w-full max-w-lg bg-zinc-950 border-l border-white/10 p-10 z-50 overflow-y-auto"
                        >
                            <div className="flex items-center justify-between mb-12">
                                <div>
                                    <h2 className="text-2xl font-bold tracking-tighter uppercase italic text-primary italic">Forge Neural Unit</h2>
                                    <p className="text-[10px] text-zinc-500 uppercase tracking-widest mt-1">Configure Subagent Directive</p>
                                </div>
                                <button onClick={() => setShowForge(false)} className="text-zinc-500 hover:text-white transition-colors">Deactivate Forge [X]</button>
                            </div>

                            <form onSubmit={handleCreateAgent} className="space-y-8">
                                <div className="space-y-2">
                                    <label className="text-[10px] uppercase tracking-widest text-zinc-500">Unit Designation</label>
                                    <input
                                        type="text"
                                        required
                                        value={newAgent.name}
                                        onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
                                        className="w-full bg-white/[0.03] border border-zinc-800 p-4 rounded-sm text-sm focus:border-primary transition-colors outline-none font-mono"
                                        placeholder="e.g. SCOUT-MARK-1"
                                    />
                                </div>

                                <div className="space-y-2">
                                    <label className="text-[10px] uppercase tracking-widest text-zinc-500">Neural Class</label>
                                    <div className="grid grid-cols-2 gap-3">
                                        {[
                                            { id: "RESEARCHER", icon: BrainCircuit, label: "Researcher" },
                                            { id: "LEAD_FINDER", icon: SearchIcon, label: "Lead Scout" },
                                            { id: "CLOSER", icon: Zap, label: "Neural Closer" },
                                            { id: "GENERAL_SUPPORT", icon: MessageCircle, label: "Support Unit" },
                                        ].map((cls) => (
                                            <button
                                                key={cls.id}
                                                type="button"
                                                onClick={() => setNewAgent({ ...newAgent, agent_type: cls.id })}
                                                className={cn(
                                                    "p-4 border text-left rounded-sm transition-all group",
                                                    newAgent.agent_type === cls.id ? "bg-primary/10 border-primary" : "bg-white/[0.02] border-zinc-800 hover:border-zinc-700"
                                                )}
                                            >
                                                <cls.icon className={cn("w-5 h-5 mb-2", newAgent.agent_type === cls.id ? "text-primary" : "text-zinc-600")} />
                                                <p className={cn("text-xs font-bold uppercase tracking-widest", newAgent.agent_type === cls.id ? "text-primary" : "text-zinc-400")}>{cls.label}</p>
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <label className="text-[10px] uppercase tracking-widest text-zinc-500 flex justify-between">
                                        Primary Directives
                                        <span className="text-[8px] text-zinc-600 font-normal underline cursor-help">Load SOP Template</span>
                                    </label>
                                    <textarea
                                        rows={8}
                                        value={newAgent.system_prompt}
                                        onChange={(e) => setNewAgent({ ...newAgent, system_prompt: e.target.value })}
                                        className="w-full bg-white/[0.03] border border-zinc-800 p-4 rounded-sm text-xs focus:border-primary transition-colors outline-none font-mono resize-none leading-relaxed"
                                        placeholder="Enter the system personality and operational constraints..."
                                    />
                                </div>

                                <button
                                    type="submit"
                                    className="w-full h-14 bg-primary text-black font-bold uppercase tracking-[0.2em] text-xs hover:bg-primary/90 transition-all rounded-sm flex items-center justify-center gap-3 mt-8 shadow-[0_10px_30px_-10px_rgba(34,197,94,0.3)]"
                                >
                                    Initiate Unit Deployment
                                </button>
                            </form>
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
        </main>
    );
}

function AgentCard({ agent, onToggle, onDelete }: { agent: any, onToggle: () => void, onDelete: () => void }) {
    const isRunning = agent.status === "RUNNING";

    return (
        <motion.div
            whileHover={{ y: -4, scale: 1.02 }}
            className="glass relative overflow-hidden group border-t-2 border-t-zinc-800 transition-all hover:border-t-primary"
        >
            <div className="absolute top-0 right-0 p-4">
                <div className="flex gap-2">
                    <button className="text-zinc-600 hover:text-white transition-colors"><Settings2 className="w-3.5 h-3.5" /></button>
                    <button onClick={onDelete} className="text-zinc-700 hover:text-red-500 transition-colors">
                        <MoreVertical className="w-3.5 h-3.5" />
                    </button>
                </div>
            </div>

            <div className="p-6">
                <div className="flex items-center gap-4 mb-6">
                    <div className="relative">
                        <div className={cn(
                            "w-12 h-12 rounded-full flex items-center justify-center border bg-zinc-900/50 transition-all",
                            isRunning ? "border-primary glow-green" : "border-zinc-800"
                        )}>
                            <AgentIcon type={agent.agent_type} className={cn("w-5 h-5", isRunning ? "text-primary" : "text-zinc-600")} />
                        </div>
                        {isRunning && (
                            <motion.div
                                animate={{ scale: [1, 1.4, 1], opacity: [0.3, 0.1, 0.3] }}
                                transition={{ repeat: Infinity, duration: 2 }}
                                className="absolute inset-0 bg-primary/20 rounded-full blur-md"
                            />
                        )}
                    </div>
                    <div>
                        <h4 className="font-bold uppercase tracking-widest text-sm text-zinc-100">{agent.name}</h4>
                        <p className="text-[10px] text-zinc-500 uppercase tracking-widest">{agent.agent_type.replace('_', ' ')}</p>
                    </div>
                </div>

                <div className="space-y-4">
                    <div className="flex justify-between items-end">
                        <div>
                            <p className="text-[10px] text-zinc-500 uppercase mb-1">Efficiency Ratio</p>
                            <p className="text-lg font-bold">98.<span className="text-xs">4%</span></p>
                        </div>
                        <div className="text-right">
                            <p className="text-[10px] text-zinc-500 uppercase mb-1">Status</p>
                            <div className="flex items-center gap-1.5 justify-end">
                                <div className={cn("w-1 h-1 rounded-full", isRunning ? "bg-primary animate-pulse" : "bg-zinc-600")} />
                                <span className={cn("text-[9px] font-bold uppercase", isRunning ? "text-primary" : "text-zinc-600")}>{agent.status}</span>
                            </div>
                        </div>
                    </div>

                    <div className="h-12 bg-black/40 rounded-sm border border-zinc-900 p-2 font-mono text-[9px] overflow-hidden">
                        <p className="text-zinc-600 truncate animate-pulse uppercase tracking-wider">{isRunning ? `Neural Link established. PID ${agent.process_id || '...'}` : 'Module in standby mode.'}</p>
                        <p className="text-[8px] text-zinc-500/50 mt-1 uppercase italic">Secure Uplink: 129.159.224.220</p>
                    </div>

                    <button
                        onClick={onToggle}
                        className={cn(
                            "w-full h-10 rounded-sm font-bold uppercase text-[10px] tracking-[0.2em] flex items-center justify-center gap-2 transition-all",
                            isRunning ? "bg-zinc-800 text-red-500 hover:bg-zinc-700" : "bg-primary text-black hover:bg-primary/90"
                        )}
                    >
                        {isRunning ? <><Square className="w-3 h-3 fill-current" /> Terminate Unit</> : <><Play className="w-3 h-3 fill-current" /> Deploy Unit</>}
                    </button>
                </div>
            </div>
        </motion.div>
    );
}

function AgentIcon({ type, ...props }: { type: string, [key: string]: any }) {
    switch (type) {
        case "RESEARCHER": return <BrainCircuit {...props} />;
        case "LEAD_FINDER": return <SearchIcon {...props} />;
        case "CLOSER": return <Zap {...props} />;
        default: return <MessageCircle {...props} />;
    }
}
