"use client";

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, Brain, Activity, Database, Server, Settings, TerminalSquare, AlertTriangle, PlayCircle, StopCircle, RefreshCw } from 'lucide-react';

export default function CommandCenter() {
  const [isSystemActive, setIsSystemActive] = useState(true);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 }
  };

  return (
    <div className="min-h-screen bg-[#0a0f1a] text-white p-8 font-sans selection:bg-emerald-500/30">
      <div className="max-w-7xl mx-auto">
        {/* Header Section */}
        <motion.header 
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="flex justify-between items-center mb-12 bg-white/5 border border-white/10 p-6 rounded-2xl backdrop-blur-md shadow-2xl"
        >
          <div className="flex items-center gap-4">
            <div className="p-3 bg-emerald-500/20 rounded-xl border border-emerald-500/50 shadow-[0_0_15px_rgba(16,185,129,0.3)]">
              <Brain className="w-8 h-8 text-emerald-400" />
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">قيام (QIYAM)</h1>
              <p className="text-gray-400 text-sm tracking-widest uppercase mt-1">Sovereign AI Operating System</p>
            </div>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3 bg-black/40 px-5 py-2.5 rounded-full border border-white/5">
              <div className="relative flex h-3 w-3">
                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${isSystemActive ? 'bg-emerald-400' : 'bg-red-500'}`}></span>
                <span className={`relative inline-flex rounded-full h-3 w-3 ${isSystemActive ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
              </div>
              <span className="text-sm font-medium tracking-wide">
                {isSystemActive ? 'النظام يعمل' : 'النظام متوقف'}
              </span>
            </div>
            <button 
              onClick={() => setIsSystemActive(!isSystemActive)}
              className={`p-2.5 rounded-full border transition-all duration-300 ${isSystemActive ? 'bg-red-500/10 border-red-500/30 text-red-400 hover:bg-red-500/20' : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20'}`}
            >
              {isSystemActive ? <StopCircle className="w-6 h-6" /> : <PlayCircle className="w-6 h-6" />}
            </button>
          </div>
        </motion.header>

        {/* Dashboard Grid */}
        <motion.div 
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {/* Node Status Card */}
          <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm hover:border-emerald-500/30 transition-colors group">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-200">حالة العُقد (Nodes)</h2>
              <Server className="text-emerald-400 opacity-50 group-hover:opacity-100 transition-opacity" />
            </div>
            <div className="space-y-4">
              <StatusRow label="المحرك الأساسي (Orchestrator)" status="online" />
              <StatusRow label="وكيل الرؤية (Vision)" status="online" />
              <StatusRow label="وكيل الإنترنت (WebSurfer)" status="online" />
              <StatusRow label="وكيل الحاسوب (Computer)" status="warning" />
            </div>
          </motion.div>

          {/* Memory & DB Card */}
          <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm hover:border-cyan-500/30 transition-colors group">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-200">الذاكرة والبيانات</h2>
              <Database className="text-cyan-400 opacity-50 group-hover:opacity-100 transition-opacity" />
            </div>
            <div className="space-y-4">
              <MetricRow label="قاعدة البيانات المحلية (SQLite)" value="45 MB" />
              <MetricRow label="الرسم البياني (Neo4j)" value="128 Nodes" />
              <MetricRow label="المتجهات (ChromaDB)" value="1,024 Vectors" />
              <div className="pt-4 mt-2 border-t border-white/10 flex justify-between items-center text-sm">
                <span className="text-gray-400">آخر مزامنة: منذ 5 دقائق</span>
                <button className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1">
                  <RefreshCw className="w-4 h-4" /> تحديث
                </button>
              </div>
            </div>
          </motion.div>

          {/* Security Sandbox Card */}
          <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm hover:border-purple-500/30 transition-colors group">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-200">بيئة الحماية (Sandbox)</h2>
              <Shield className="text-purple-400 opacity-50 group-hover:opacity-100 transition-opacity" />
            </div>
            <div className="space-y-4">
              <div className="flex items-center gap-3 bg-purple-500/10 border border-purple-500/20 p-3 rounded-xl">
                <AlertTriangle className="text-purple-400 w-5 h-5" />
                <span className="text-sm text-purple-200">لا توجد محاولات اختراق حديثة</span>
              </div>
              <MetricRow label="الأوامر الممنوعة المحبطة" value="0" />
              <MetricRow label="طلبات الصلاحية المعلقة" value="2" highlight />
            </div>
          </motion.div>

          {/* Live Terminal */}
          <motion.div variants={itemVariants} className="col-span-1 lg:col-span-3 bg-black/60 border border-white/10 rounded-2xl p-6 font-mono relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-emerald-500 via-cyan-500 to-purple-500 opacity-50"></div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2 text-gray-400">
                <TerminalSquare className="w-5 h-5" />
                <span>qiyam-core-logs</span>
              </div>
              <div className="flex gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500/50"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500/50"></div>
                <div className="w-3 h-3 rounded-full bg-green-500/50"></div>
              </div>
            </div>
            <div className="text-sm space-y-2 text-gray-300 h-48 overflow-y-auto custom-scrollbar pe-2">
              <p><span className="text-emerald-400">[INFO]</span> 2026-06-05 00:32:10 - System initialized.</p>
              <p><span className="text-emerald-400">[INFO]</span> 2026-06-05 00:32:15 - Connected to Ollama (LLaVA loaded).</p>
              <p><span className="text-emerald-400">[INFO]</span> 2026-06-05 00:33:02 - Incoming WhatsApp message from +966555555555.</p>
              <p><span className="text-cyan-400">[ROUTER]</span> 2026-06-05 00:33:03 - Intent classified as 'WEB_SEARCH'. Routing to WebAgent.</p>
              <p><span className="text-purple-400">[SANDBOX]</span> 2026-06-05 00:34:20 - Blocked attempt: 'rm -rf /' by Agent: ComputerOperator.</p>
              <p className="animate-pulse">_</p>
            </div>
          </motion.div>

        </motion.div>
      </div>
    </div>
  );
}

function StatusRow({ label, status }: { label: string, status: 'online' | 'offline' | 'warning' }) {
  const colors = {
    online: 'bg-emerald-500',
    offline: 'bg-red-500',
    warning: 'bg-yellow-500'
  };
  
  return (
    <div className="flex justify-between items-center">
      <span className="text-gray-300 text-sm">{label}</span>
      <div className="flex items-center gap-2">
        <span className="text-xs text-gray-500 uppercase tracking-wider">{status}</span>
        <div className={`w-2 h-2 rounded-full ${colors[status]}`}></div>
      </div>
    </div>
  );
}

function MetricRow({ label, value, highlight = false }: { label: string, value: string, highlight?: boolean }) {
  return (
    <div className="flex justify-between items-center border-b border-white/5 pb-2">
      <span className="text-gray-300 text-sm">{label}</span>
      <span className={`text-sm font-semibold ${highlight ? 'text-purple-400' : 'text-gray-100'}`}>{value}</span>
    </div>
  );
}
