import React from 'react';
import { ShieldAlert, Cpu, Radio, UploadCloud, LayoutDashboard, CreditCard, Car, UserCheck } from 'lucide-react';

export const Header = ({
  systemStatus,
  mode,
  onModeChange,
  activeTab = 'live',
  onTabChange
}) => {
  const isOnline = systemStatus?.status === 'ONLINE';
  const device = systemStatus?.device || 'CPU';

  return (
    <header className="bg-command-header border-b border-command-border px-6 py-3 shadow-xl">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Logo & Branding */}
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-400 glow-emerald">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-extrabold tracking-tight text-white">IBVAP</h1>
              <span className="text-[11px] px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 font-mono border border-cyan-800">
                AI ANALYTICS V2.1
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium tracking-wide">
              INTELLIGENT BORDER VIDEO ANALYTICS • TRACKING • ANPR • FACIAL RECOGNITION
            </p>
          </div>
        </div>

        {/* Center: Navigation Tabs */}
        <div className="flex items-center bg-slate-900/90 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => onTabChange('live')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'live'
                ? 'bg-emerald-600 text-white shadow-lg glow-emerald'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <LayoutDashboard className="w-3.5 h-3.5" />
            Live Command
          </button>
          
          <button
            onClick={() => onTabChange('anpr')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'anpr'
                ? 'bg-amber-600 text-white shadow-lg'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <CreditCard className="w-3.5 h-3.5" />
            ANPR Logs
          </button>

          <button
            onClick={() => onTabChange('faces')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'faces'
                ? 'bg-cyan-600 text-white shadow-lg glow-cyan'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <UserCheck className="w-3.5 h-3.5" />
            Face Watchlist
          </button>

          <button
            onClick={() => onTabChange('security')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'security'
                ? 'bg-red-600 text-white shadow-lg glow-red'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            Security Breaches
          </button>
        </div>

        {/* Right Controls: Input Mode & Status */}
        <div className="flex items-center gap-3">
          
          {/* Mode Selector */}
          {activeTab === 'live' && (
            <div className="flex items-center bg-slate-900 p-1 rounded-lg border border-slate-800">
              <button
                onClick={() => onModeChange('demo')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded text-xs font-mono transition-all ${
                  mode === 'demo'
                    ? 'bg-cyan-600 text-white shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Radio className="w-3 h-3" />
                Demo CCTV
              </button>
              <button
                onClick={() => onModeChange('upload')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded text-xs font-mono transition-all ${
                  mode === 'upload'
                    ? 'bg-cyan-600 text-white shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <UploadCloud className="w-3 h-3" />
                Upload
              </button>
            </div>
          )}

          {/* Device Badge */}
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300">
            <Cpu className="w-3.5 h-3.5 text-blue-400" />
            <span><strong className="text-blue-400">{device}</strong></span>
          </div>

          {/* Online Status */}
          <div className="flex items-center gap-2 px-3 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono">
            <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-400 animate-pulse' : 'bg-red-500'}`} />
            <span className={isOnline ? 'text-emerald-400' : 'text-red-400'}>
              {isOnline ? 'ONLINE' : 'OFFLINE'}
            </span>
          </div>

        </div>

      </div>
    </header>
  );
};
