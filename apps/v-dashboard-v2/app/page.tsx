"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Shield,
  Zap,
  MessageSquare,
  Cpu,
  Wifi,
  WifiOff,
  QrCode,
  ArrowRight,
  Loader2,
  Terminal as TerminalIcon,
  LogOut
} from "lucide-react";
import axios from "axios";
import { useRouter } from "next/navigation";
import { GATEWAY_URL, API_KEY } from "@/lib/constants";
import { cn } from "@/lib/utils";

export default function Home() {
  const [status, setStatus] = useState<any>(null);
  const [qrCode, setQrCode] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Multi-Tenancy: Get user session from local storage
  const [user, setUser] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem("v_token");
    const storedUser = localStorage.getItem("v_user");

    if (!storedToken) {
      router.push("/auth");
    } else {
      setToken(storedToken);
      setUser(storedUser);
    }
  }, [router]);

  const fetchStatus = async () => {
    const sessionId = localStorage.getItem("v_user") || "default";
    try {
      const response = await axios.get(`${GATEWAY_URL}/auth/status?api_key=${API_KEY}`, {
        headers: { "x-session-id": sessionId }
      });
      setStatus(response.data.data);
      if (response.data.data.status === 'qr_ready') {
        fetchQR();
      } else {
        setQrCode(null);
      }
      setError(null);
    } catch (err) {
      console.error("Status fetch failed", err);
      setError("Gateway Unreachable");
    } finally {
      setLoading(false);
    }
  };

  const fetchQR = async () => {
    const sessionId = localStorage.getItem("v_user") || "default";
    try {
      const response = await axios.get(`${GATEWAY_URL}/auth/qr?api_key=${API_KEY}`, {
        headers: { "x-session-id": sessionId }
      });
      if (response.data.data.qrCode) {
        setQrCode(response.data.data.qrCode);
      }
    } catch (err) {
      console.error("QR fetch failed", err);
    }
  };

  const handleLogout = async () => {
    if (!confirm("Are you sure you want to terminate this session?")) return;
    const sessionId = localStorage.getItem("v_user") || "default";
    try {
      await axios.post(`${GATEWAY_URL}/auth/logout?api_key=${API_KEY}`, {}, {
        headers: { "x-session-id": sessionId }
      });
      fetchStatus();
    } catch (err) {
      alert("Logout failed");
    }
  };

  const clearAuth = () => {
    localStorage.removeItem("v_token");
    localStorage.removeItem("v_user");
    router.push("/auth");
  };

  useEffect(() => {
    if (localStorage.getItem("v_token")) {
      fetchStatus();
      const interval = setInterval(fetchStatus, 10000);
      return () => clearInterval(interval);
    }
  }, []);

  return (
    <main className="min-h-screen bg-black text-slate-100 flex flex-col font-mono selection:bg-primary selection:text-black">
      {/* Cinematic Grid Background */}
      <div className="fixed inset-0 bg-[linear-gradient(to_right,#161618_1px,transparent_1px),linear-gradient(to_bottom,#161618_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none" />

      {/* Header */}
      <header className="relative z-10 border-b border-border bg-black/50 backdrop-blur-md px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Shield className="w-8 h-8 text-primary glow-green" />
            <motion.div
              animate={{ opacity: [0.3, 0.6, 0.3] }}
              transition={{ repeat: Infinity, duration: 2 }}
              className="absolute inset-0 bg-primary/20 blur-xl"
            />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tighter uppercase italic">VORTEX</h1>
            <p className="text-[10px] text-zinc-500 uppercase tracking-[0.2em]">Command Console v1.0.4</p>
          </div>
        </div>

        <div className="flex items-center gap-6 text-[10px] uppercase tracking-widest text-zinc-400">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
            System Secure
          </div>
          {status?.isConnected ? (
            <button onClick={handleLogout} className="flex items-center gap-2 h-8 px-4 border border-zinc-800 hover:border-red-500/50 hover:text-red-400 transition-all rounded-sm group">
              <LogOut className="w-3 h-3 group-hover:rotate-12 transition-transform" />
              Term. Session
            </button>
          ) : (
            <div className="flex items-center gap-2">
              <TerminalIcon className="w-3 h-3" />
              Root Access Active
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 relative z-10 p-8 grid grid-cols-1 lg:grid-cols-12 gap-8 max-w-7xl mx-auto w-full">

        {/* Left: Status & Logic */}
        <div className="lg:col-span-7 space-y-8">
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass p-8 rounded-sm relative overflow-hidden group"
          >
            <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
              <Cpu className="w-32 h-32" />
            </div>

            <div className="flex items-start justify-between mb-8">
              <div>
                <h2 className="text-sm uppercase tracking-[0.3em] text-zinc-500 mb-1">Deployment Status</h2>
                <div className="flex items-center gap-3">
                  <span className={cn(
                    "text-3xl font-bold tracking-tighter uppercase italic",
                    status?.isConnected ? "text-primary" : "text-zinc-400"
                  )}>
                    {status?.isConnected ? "Operational" : status?.status === 'qr_ready' ? "Pulse Required" : "Shadow Mode"}
                  </span>
                  {status?.isConnected ? <Wifi className="w-6 h-6 text-primary" /> : <WifiOff className="w-6 h-6 text-zinc-600" />}
                </div>
              </div>
              <div className="text-right">
                <p className="text-[10px] text-zinc-500 uppercase">Latency</p>
                <p className="text-xs text-primary font-bold">14ms</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white/[0.03] border border-white/[0.05] p-4 rounded-sm">
                <p className="text-[10px] text-zinc-500 uppercase mb-1">Messages Sent</p>
                <p className="text-2xl font-bold">{status?.messagesSentToday || 0}</p>
                <p className="text-[10px] text-zinc-600">Period: 24h cycle</p>
              </div>
              <div className="bg-white/[0.03] border border-white/[0.05] p-4 rounded-sm">
                <p className="text-[10px] text-zinc-500 uppercase mb-1">Daily Cap</p>
                <p className="text-2xl font-bold text-zinc-400">{status?.dailyLimit || 1000}</p>
                <p className="text-[10px] text-zinc-600">Usage: {Math.round(((status?.messagesSentToday || 0) / (status?.dailyLimit || 1000)) * 100)}%</p>
              </div>
            </div>
          </motion.section>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <motion.div
              whileHover={{ scale: 1.02 }}
              onClick={() => router.push("/agents")}
              className="glass p-6 rounded-sm border-l-2 border-l-secondary/50 group cursor-pointer"
            >
              <MessageSquare className="w-6 h-6 text-secondary mb-4 glow-indigo" />
              <h3 className="font-bold uppercase tracking-widest text-sm mb-2">Agent War Room</h3>
              <p className="text-xs text-zinc-500 leading-relaxed mb-4">
                Deploy and manage your autonomous subagent swarm. Neural links active across all sectors.
              </p>
              <div className="flex items-center gap-2 text-[10px] text-secondary font-bold uppercase group-hover:gap-4 transition-all">
                Enter Command Console <ArrowRight className="w-3 h-3" />
              </div>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.02 }}
              className="glass p-6 rounded-sm border-l-2 border-l-primary/50 group cursor-pointer"
            >
              <Zap className="w-6 h-6 text-primary mb-4 glow-green" />
              <h3 className="font-bold uppercase tracking-widest text-sm mb-2">Strike Campaigns</h3>
              <p className="text-xs text-zinc-500 leading-relaxed mb-4">
                Mass transmission module primed. Reach {status?.dailyLimit || 1000} targets with randomized delivery windows.
              </p>
              <div className="flex items-center gap-2 text-[10px] text-primary font-bold uppercase group-hover:gap-4 transition-all">
                Deploy Assets <ArrowRight className="w-3 h-3" />
              </div>
            </motion.div>
          </div>
        </div>

        {/* Right: Connection Hub (The QR Scanner) */}
        <div className="lg:col-span-5">
          <AnimatePresence mode="wait">
            {!status?.isConnected ? (
              <motion.div
                key="qr-section"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 1.05 }}
                className="glass rounded-sm h-full flex flex-col items-center justify-center p-12 text-center"
              >
                <div className="mb-8 p-4 bg-primary/10 rounded-full">
                  <QrCode className="w-12 h-12 text-primary" />
                </div>
                <h3 className="text-xl font-bold uppercase italic tracking-tighter mb-2">Bridge Authentication</h3>
                <p className="text-xs text-zinc-500 mb-10 max-w-[280px]">
                  Scan the secure uplink code with your WhatsApp device to authorize command transmission.
                </p>

                <div className="relative p-2 border border-zinc-800 bg-white/5 rounded-sm overflow-hidden group">
                  {qrCode ? (
                    <motion.img
                      initial={{ filter: 'blur(10px)', opacity: 0 }}
                      animate={{ filter: 'blur(0px)', opacity: 1 }}
                      src={qrCode}
                      alt="Uplink Code"
                      className="w-64 h-64 grayscale contrast-125"
                    />
                  ) : (
                    <div className="w-64 h-64 flex flex-col items-center justify-center gap-4 bg-black/40">
                      <Loader2 className="w-8 h-8 text-zinc-700 animate-spin" />
                      <p className="text-[10px] text-zinc-600 uppercase">Fetching Uplink...</p>
                    </div>
                  )}

                  {/* Digital Scanline Effect */}
                  <motion.div
                    animate={{ top: ['0%', '100%', '0%'] }}
                    transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}
                    className="absolute inset-x-0 h-[2px] bg-primary/20 blur-sm pointer-events-none"
                  />
                </div>

                <div className="mt-10 flex items-center gap-3 px-4 py-2 bg-white/[0.02] border border-white/[0.05] rounded-full">
                  <span className="w-1.5 h-1.5 rounded-full bg-yellow-500 animate-pulse" />
                  <span className="text-[9px] uppercase tracking-widest text-zinc-400">Waiting for Handshake...</span>
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="connected-section"
                initial={{ opacity: 0, scale: 1.05 }}
                animate={{ opacity: 1, scale: 1 }}
                className="glass rounded-sm h-full flex flex-col items-center justify-center p-12 text-center relative overflow-hidden"
              >
                <div className="absolute inset-0 bg-primary/5 [mask-image:radial-gradient(circle_at_center,white,transparent)]" />

                <div className="relative mb-8">
                  <div className="p-6 bg-primary/20 rounded-full">
                    <Wifi className="w-16 h-16 text-primary glow-green" />
                  </div>
                  <motion.div
                    animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
                    transition={{ repeat: Infinity, duration: 3 }}
                    className="absolute inset-0 border-2 border-primary rounded-full"
                  />
                </div>

                <h3 className="text-2xl font-bold uppercase italic tracking-tighter mb-4">Uplink Stable</h3>
                <p className="text-xs text-primary/80 font-bold uppercase tracking-[0.2em] mb-8">
                  Encrypted Tunnel Established
                </p>

                <div className="w-full space-y-4 max-w-[300px]">
                  <button className="w-full h-12 bg-primary text-black font-bold uppercase tracking-widest text-xs hover:bg-primary/90 transition-colors rounded-sm">
                    Enter Tactical View
                  </button>
                  <p className="text-[9px] text-zinc-600 uppercase">Session ID: {status?.sessionId || 'MASTER'}</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Footer / Terminal Feed */}
      <footer className="relative z-10 border-t border-border bg-black p-4 flex items-center justify-between px-8">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-primary" />
            <span className="text-[10px] text-zinc-500 uppercase">API: {GATEWAY_URL}</span>
          </div>
        </div>
        <p className="text-[9px] text-zinc-600 uppercase tracking-tighter">
          © {new Date().getFullYear()} VORTEX SEC OVERSIGHT. ALL TRANSMISSIONS LOGGED.
        </p>
      </footer>
    </main>
  );
}
