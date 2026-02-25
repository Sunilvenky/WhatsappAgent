"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Shield, Lock, Terminal as TerminalIcon, AlertCircle, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

// Admin credentials - in production, use a proper auth backend
const ADMIN_USERS = [
    { email: "sunil.rocknrollriders@gmail.com", password: "Welcome@2026" },
    { email: "admin@vortex.com", password: "admin123" },
];

export default function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            // Simple credential check - bypasses Supabase Auth
            const user = ADMIN_USERS.find(
                (u) => u.email.toLowerCase() === email.toLowerCase() && u.password === password
            );

            if (!user) {
                throw new Error("Invalid credentials. Access Denied.");
            }

            // Generate a simple session token
            const token = btoa(`${user.email}:${Date.now()}`);
            localStorage.setItem("v_token", token);
            localStorage.setItem("v_user", user.email);

            console.log("Login successful!");
            router.push("/");
        } catch (err: any) {
            console.error("Login attempt failed:", err);
            setError(err.message || "Authentication Failed. Access Denied.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="min-h-screen bg-black text-slate-100 flex items-center justify-center p-6 font-mono">
            <div className="fixed inset-0 bg-[linear-gradient(to_right,#161618_1px,transparent_1px),linear-gradient(to_bottom,#161618_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none" />

            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full max-w-md relative z-10"
            >
                <div className="glass p-8 rounded-sm">
                    <div className="flex flex-col items-center mb-8">
                        <div className="relative mb-4">
                            <Shield className="w-12 h-12 text-primary glow-green" />
                            <motion.div
                                animate={{ opacity: [0.3, 0.6, 0.3] }}
                                transition={{ repeat: Infinity, duration: 2 }}
                                className="absolute inset-0 bg-primary/20 blur-xl"
                            />
                        </div>
                        <h1 className="text-2xl font-bold tracking-tighter uppercase italic">VORTEX AUTH</h1>
                        <p className="text-[10px] text-zinc-500 uppercase tracking-[0.2em] mt-1 text-center">Enter Sector Credentials</p>
                    </div>

                    <form onSubmit={handleLogin} className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-[10px] uppercase tracking-widest text-zinc-500 flex items-center gap-2">
                                <TerminalIcon className="w-3 h-3" /> Identity (Email)
                            </label>
                            <input
                                type="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full bg-white/[0.03] border border-zinc-800 p-4 rounded-sm text-sm focus:border-primary transition-colors outline-none font-mono"
                                placeholder="name@domain.com"
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-[10px] uppercase tracking-widest text-zinc-500 flex items-center gap-2">
                                <Lock className="w-3 h-3" /> Access Cipher
                            </label>
                            <input
                                type="password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full bg-white/[0.03] border border-zinc-800 p-4 rounded-sm text-sm focus:border-primary transition-colors outline-none font-mono"
                                placeholder="********"
                            />
                        </div>

                        {error && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="bg-red-950/30 border border-red-500/50 p-4 rounded-sm flex items-center gap-3 text-red-400 text-xs"
                            >
                                <AlertCircle className="w-4 h-4" />
                                {error}
                            </motion.div>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full h-12 bg-primary text-black font-bold uppercase tracking-widest text-xs hover:bg-primary/90 transition-all rounded-sm flex items-center justify-center gap-3"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" /> Verifying...
                                </>
                            ) : (
                                "Execute Login"
                            )}
                        </button>
                    </form>
                </div>

                <div className="mt-8 flex justify-center gap-6">
                    <div className="flex items-center gap-1.5 grayscale opacity-30 hover:grayscale-0 hover:opacity-100 transition-all cursor-crosshair">
                        <Shield className="w-3 h-3" />
                        <span className="text-[8px] uppercase tracking-[0.2em]">Secure Entry</span>
                    </div>
                    <div className="flex items-center gap-1.5 grayscale opacity-30 hover:grayscale-0 hover:opacity-100 transition-all cursor-crosshair">
                        <Lock className="w-3 h-3" />
                        <span className="text-[8px] uppercase tracking-[0.2em]">Encrypted Layer</span>
                    </div>
                </div>
            </motion.div>
        </main>
    );
}
