import React from 'react';
import { Users, Car, Crosshair, Fingerprint, Activity, Gauge, Cpu, CreditCard, Shield, ShieldAlert } from 'lucide-react';

export const StatsPanel = ({ telemetry }) => {
  const currentPersons = telemetry?.current_persons ?? 0;
  const currentVehicles = telemetry?.current_vehicles ?? 0;
  const activeTracks = telemetry?.active_tracks ?? (currentPersons + currentVehicles);
  const totalUniquePersons = telemetry?.total_unique_persons ?? 0;
  const totalUniqueVehicles = telemetry?.total_unique_vehicles ?? 0;
  const totalAnprReads = telemetry?.total_anpr_reads ?? 0;
  const virtualFencesCount = telemetry?.virtual_fences_count ?? 0;
  const activeIntrusionsCount = telemetry?.active_intrusions_count ?? 0;
  const totalIntrusionsCount = telemetry?.total_intrusions_count ?? 0;
  const fps = telemetry?.fps ?? 0;
  const device = telemetry?.device ?? 'CPU';

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
      
      {/* Persons Detected */}
      <div className="bg-command-card border border-command-border rounded-xl p-3 flex flex-col justify-between hover:border-emerald-500/40 transition-colors">
        <div className="flex items-center justify-between text-slate-400">
          <span className="text-[10px] font-bold font-mono tracking-wider uppercase">Persons</span>
          <Users className="w-3.5 h-3.5 text-emerald-400" />
        </div>
        <div className="mt-1.5 flex items-baseline justify-between">
          <span className="text-xl font-black font-mono text-white">{currentPersons}</span>
          <span className="text-[9px] text-emerald-400/80 font-mono">ACTIVE (P)</span>
        </div>
      </div>

      {/* Vehicles Detected */}
      <div className="bg-command-card border border-command-border rounded-xl p-3 flex flex-col justify-between hover:border-cyan-500/40 transition-colors">
        <div className="flex items-center justify-between text-slate-400">
          <span className="text-[10px] font-bold font-mono tracking-wider uppercase">Vehicles</span>
          <Car className="w-3.5 h-3.5 text-cyan-400" />
        </div>
        <div className="mt-1.5 flex items-baseline justify-between">
          <span className="text-xl font-black font-mono text-cyan-400">{currentVehicles}</span>
          <span className="text-[9px] text-cyan-400/80 font-mono">ACTIVE (V)</span>
        </div>
      </div>

      {/* Active Combined Tracks */}
      <div className="bg-command-card border border-command-border rounded-xl p-3 flex flex-col justify-between hover:border-blue-500/40 transition-colors">
        <div className="flex items-center justify-between text-slate-400">
          <span className="text-[10px] font-bold font-mono tracking-wider uppercase">Active Tracks</span>
          <Crosshair className="w-3.5 h-3.5 text-blue-400" />
        </div>
        <div className="mt-1.5 flex items-baseline justify-between">
          <span className="text-xl font-black font-mono text-blue-400">{activeTracks}</span>
          <span className="text-[9px] text-slate-500 font-mono">DUAL</span>
        </div>
      </div>

      {/* ANPR Confirmed Reads */}
      <div className="bg-command-card border border-command-border rounded-xl p-3 flex flex-col justify-between hover:border-amber-500/40 transition-colors">
        <div className="flex items-center justify-between text-slate-400">
          <span className="text-[10px] font-bold font-mono tracking-wider uppercase">ANPR Reads</span>
          <CreditCard className="w-3.5 h-3.5 text-amber-400" />
        </div>
        <div className="mt-1.5 flex items-baseline justify-between">
          <span className="text-xl font-black font-mono text-amber-400">{totalAnprReads}</span>
          <span className="text-[9px] text-amber-400/80 font-mono">PLATES</span>
        </div>
      </div>

      {/* Virtual Fences Configured */}
      <div className="bg-command-card border border-command-border rounded-xl p-3 flex flex-col justify-between hover:border-cyan-500/40 transition-colors">
        <div className="flex items-center justify-between text-slate-400">
          <span className="text-[10px] font-bold font-mono tracking-wider uppercase">Virtual Fences</span>
          <Shield className="w-3.5 h-3.5 text-cyan-400" />
        </div>
        <div className="mt-1.5 flex items-baseline justify-between">
          <span className="text-xl font-black font-mono text-cyan-300">{virtualFencesCount}</span>
          <span className="text-[9px] text-cyan-400/80 font-mono">ZONES</span>
        </div>
      </div>

      {/* Active Intrusions */}
      <div className={`bg-command-card border rounded-xl p-3 flex flex-col justify-between transition-colors ${
        activeIntrusionsCount > 0
          ? 'border-red-500 bg-red-950/20 shadow glow-red'
          : 'border-command-border hover:border-red-500/40'
      }`}>
        <div className="flex items-center justify-between text-slate-400">
          <span className="text-[10px] font-bold font-mono tracking-wider uppercase">Active Breach</span>
          <ShieldAlert className={`w-3.5 h-3.5 ${activeIntrusionsCount > 0 ? 'text-red-400 animate-pulse' : 'text-slate-500'}`} />
        </div>
        <div className="mt-1.5 flex items-baseline justify-between">
          <span className={`text-xl font-black font-mono ${activeIntrusionsCount > 0 ? 'text-red-400' : 'text-slate-300'}`}>
            {activeIntrusionsCount}
          </span>
          <span className="text-[9px] text-slate-500 font-mono">
            {totalIntrusionsCount} TOTAL
          </span>
        </div>
      </div>

      {/* Processing FPS */}
      <div className="bg-command-card border border-command-border rounded-xl p-3 flex flex-col justify-between hover:border-yellow-500/40 transition-colors">
        <div className="flex items-center justify-between text-slate-400">
          <span className="text-[10px] font-bold font-mono tracking-wider uppercase">Process FPS</span>
          <Gauge className="w-3.5 h-3.5 text-yellow-400" />
        </div>
        <div className="mt-1.5 flex items-baseline justify-between">
          <span className="text-xl font-black font-mono text-yellow-400">{fps.toFixed(1)}</span>
          <span className="text-[9px] text-slate-500 font-mono">FPS</span>
        </div>
      </div>

      {/* Device Hardware & Total Unique */}
      <div className="bg-command-card border border-command-border rounded-xl p-3 flex flex-col justify-between hover:border-purple-500/40 transition-colors">
        <div className="flex items-center justify-between text-slate-400">
          <span className="text-[10px] font-bold font-mono tracking-wider uppercase">Hardware</span>
          <Cpu className="w-3.5 h-3.5 text-purple-400" />
        </div>
        <div className="mt-1.5 flex items-baseline justify-between">
          <span className="text-base font-black font-mono text-purple-400">{device}</span>
          <span className="text-[9px] text-slate-400 font-mono">
            {totalUniquePersons}P/{totalUniqueVehicles}V
          </span>
        </div>
      </div>

    </div>
  );
};
