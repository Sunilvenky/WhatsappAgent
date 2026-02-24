"use client";

import { useState } from "react";
import {
    Shield,
    Settings as SettingsIcon,
    Brain,
    Database,
    Save,
    ArrowLeft,
    CheckCircle2,
    AlertCircle
} from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

export default function Settings() {
    const [apiKey, setApiKey] = useState("your_zeroclaw_key_here");
    const [baseUrl, setBaseUrl] = useState("http://129.159.224.220:8000/v1");
    const [model, setModel] = useState("gpt-3.5-turbo");
    const [saving, setSaving] = useState(false);
    const [saved, setSaved] = useState(false);

    const handleSave = () => {
        setSaving(true);
        // In a real app, this would call your API to update the VM's docker-compose or .env
        setTimeout(() => {
            setSaving(false);
            setSaved(true);
            setTimeout(() => setSaved(false), 3000);
        }, 1500);
    };

    return (
        <main className="min-h-screen bg-black text-slate-100 font-mono">
            <div className="fixed inset-0 bg-[linear-gradient(to_right,#161618_1px,transparent_1px),linear-gradient(to_bottom,#161618_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none" />

            <header className="relative z-10 border-b border-border bg-black/50 backdrop-blur-md px-6 py-4 flex items-center justify-between">
                <Link href="/" className="flex items-center gap-3 group">
                    <ArrowLeft className="w-5 h-5 text-zinc-500 group-hover:text-primary transition-colors" />
                    <div>
                        <h1 className="text-xl font-bold tracking-tighter uppercase italic">VORTEX</h1>
                        <p className="text-[10px] text-zinc-500 uppercase tracking-[0.2em]">System Configuration</p>
                    </div>
                </Link>
            </header>

            <div className="relative z-10 max-w-3xl mx-auto p-8 pt-16">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="glass p-8 rounded-sm"
                >
                    <div className="flex items-center gap-4 mb-12">
                        <div className="p-3 bg-secondary/20 rounded-sm">
                            <Brain className="w-8 h-8 text-secondary glow-indigo" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold uppercase italic tracking-tighter">AI Neural Configuration</h2>
                            <p className="text-xs text-zinc-500">Define the intelligence parameters for automated responses.</p>
                        </div>
                    </div>

                    <div className="space-y-8">
                        <div className="space-y-2">
                            <label className="text-[10px] uppercase tracking-widest text-zinc-500 flex items-center gap-2">
                                <Shield className="w-3 h-3" /> ZeroClaw API Key
                            </label>
                            <input
                                type="password"
                                value={apiKey}
                                onChange={(e) => setApiKey(e.target.value)}
                                className="w-full bg-white/[0.03] border border-zinc-800 p-4 rounded-sm text-sm focus:border-secondary transition-colors outline-none font-mono"
                                placeholder="vort_..."
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-[10px] uppercase tracking-widest text-zinc-500 flex items-center gap-2">
                                <Database className="w-3 h-3" /> Endpoint URL
                            </label>
                            <input
                                type="text"
                                value={baseUrl}
                                onChange={(e) => setBaseUrl(e.target.value)}
                                className="w-full bg-white/[0.03] border border-zinc-800 p-4 rounded-sm text-sm focus:border-secondary transition-colors outline-none font-mono"
                                placeholder="http://..."
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-[10px] uppercase tracking-widest text-zinc-500 flex items-center gap-2">
                                <SettingsIcon className="w-3 h-3" /> Intelligence Model
                            </label>
                            <select
                                value={model}
                                onChange={(e) => setModel(e.target.value)}
                                className="w-full bg-white/[0.03] border border-zinc-800 p-4 rounded-sm text-sm focus:border-secondary transition-colors outline-none font-mono appearance-none"
                            >
                                <option value="gpt-3.5-turbo">GPT-3.5 Turbo (High Speed)</option>
                                <option value="gpt-4">GPT-4 Omni (High Intelligence)</option>
                                <option value="custom">Custom ZeroClaw Model</option>
                            </select>
                        </div>

                        <div className="pt-8 flex items-center justify-between">
                            <div className="text-[10px] text-zinc-600 flex items-center gap-2 italic">
                                {saved ? (
                                    <span className="text-primary flex items-center gap-2">
                                        <CheckCircle2 className="w-3 h-3" /> Sync Complete
                                    </span>
                                ) : (
                                    <>
                                        <AlertCircle className="w-3 h-3" /> Changes require container restart
                                    </>
                                )}
                            </div>
                            <button
                                onClick={handleSave}
                                disabled={saving}
                                className="flex items-center gap-3 bg-secondary px-8 h-12 text-black font-bold uppercase text-xs tracking-widest hover:bg-secondary/90 transition-all rounded-sm disabled:opacity-50"
                            >
                                {saving ? "Syncing..." : "Commit Changes"}
                                <Save className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                </motion.div>

                <div className="mt-8 p-4 border border-zinc-900 bg-zinc-950/50 rounded-sm">
                    <p className="text-[9px] text-zinc-600 leading-relaxed italic">
                        TECHNICAL NOTE: These settings update the environment variables in your remote infrastructure.
                        Once committed, the VORTEX back-end will automatically reload the intelligence module.
                    </p>
                </div>
            </div>
        </main>
    );
}
