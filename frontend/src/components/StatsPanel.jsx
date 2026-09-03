import React from 'react';
import { Users, Car, Crosshair, Fingerprint, Activity, Gauge, Cpu, CreditCard } from 'lucide-react';

export const StatsPanel = ({ telemetry }) => {
  const currentPersons = telemetry?.current_persons ?? 0;
  const currentVehicles = telemetry?.current_vehicles ?? 0;
  const activeTracks = telemetry?.active_tracks ?? (currentPersons + currentVehicles);
  const totalUniquePersons = telemetry?.total_unique_persons ?? 0;
  const totalUniqueVehicles = telemetry?.total_unique_vehicles ?? 0;
  const totalAnprReads = telemetry?.total_anpr_reads ?? 0;
  const fps = telemetry?.fps ?? 0;
  const device = telemetry?.device ?? 'CPU';

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      
      {/* Persons Detected */}
      <div className="bg-command-card border border-command-border rounded-xl p-3 flex flex-col justify-between hover:border-emerald-500/40 transition-colors">
        <div className="flex items-center justify-between text-slate-400">
          <span className="text-[11px] font-bold font-mono tracking-wider uppercase">Persons</span>
          <Users className="w-4 h-4 text-emerald-400" />
        </div>
        <div className="mt-2 flex items-baseline justify-between">
          <span className="text-2xl font-black font-mono text-white">{currentPersons}</span>
          <span className="text-[10px] text-emerald-400/80 font-mono">ACTIVE (P)</span>
        </div>
      </div>

      {/* Vehicles Detected */}
      <div className="bg-command-card border border-command-border rounded-xl p-3 flex flex-col justify-between hover:border-cyan-500/40 transition-colors">
        <div className="flex items-center justify-between text-slate-400">
          <span className="text-[11px] font-bold font-mono tracking-wider uppercase">Vehicles</span>
          <Car className="w-4 h-4 text-cyan-400" />
        </div>
        <div className="mt-2 flex items-baseline justify-between">
          <span className="text-2xl font-black font-mono text-cyan-400">{currentVehicles}</span>
          <span className="text-[10px] text-cyan-400/80 font-mono">ACTIVE (V)</span>
        </div>
      </div>

      {/* Active Combined Tracks */}
      <div className="bg-command-card border border-command-border rounded-xl p-3 flex flex-col justify-between hover:border-blue-500/40 transition-colors">
        <div className="flex items-center justify-between text-slate-400">
          <span className="text-[11px] font-bold font-mono tracking-wider uppercase">Active Tracks</span>
          <Crosshair className="w-4 h-4 text-blue-400" />
        </div>
        <div className="mt-2 flex items-baseline justify-between">
          <span className="text-2xl font-black font-mono text-blue-400">{activeTracks}</span>
          <span className="text-[10px] text-slate-500 font-mono">DUAL PIPELINE</span>
        </div>
      </div>

      {/* ANPR Confirmed Reads */}
      <div className="bg-command-card border border-command-border rounded-xl p-3 flex flex-col justify-between hover:border-amber-500/40 transition-colors">
        <div className="flex items-center justify-between text-slate-400">
          <span className="text-[11px] font-bold font-mono tracking-wider uppercase">ANPR Reads</span>
          <CreditCard className="w-4 h-4 text-amber-400" />
        </div>
        <div className="mt-2 flex items-baseline justify-between">
          <span className="text-2xl font-black font-mono text-amber-400">{totalAnprReads}</span>
          <span className="text-[10px] text-amber-400/80 font-mono">PLATES READ</span>
        </div>
      </div>

      {/* Processing FPS */}
      <div className="bg-command-card border border-command-border rounded-xl p-3 flex flex-col justify-between hover:border-yellow-500/40 transition-colors">
        <div className="flex items-center justify-between text-slate-400">
          <span className="text-[11px] font-bold font-mono tracking-wider uppercase">Processing FPS</span>
          <Gauge className="w-4 h-4 text-yellow-400" />
        </div>
        <div className="mt-2 flex items-baseline justify-between">
          <span className="text-2xl font-black font-mono text-yellow-400">{fps.toFixed(1)}</span>
          <span className="text-[10px] text-slate-500 font-mono">FRAMES/SEC</span>
        </div>
      </div>

      {/* Device Hardware & Total Unique */}
      <div className="bg-command-card border border-command-border rounded-xl p-3 flex flex-col justify-between hover:border-purple-500/40 transition-colors">
        <div className="flex items-center justify-between text-slate-400">
          <span className="text-[11px] font-bold font-mono tracking-wider uppercase">Hardware</span>
          <Cpu className="w-4 h-4 text-purple-400" />
        </div>
        <div className="mt-2 flex items-baseline justify-between">
          <span className="text-xl font-black font-mono text-purple-400">{device}</span>
          <span className="text-[10px] text-slate-400 font-mono">
            {totalUniquePersons}P / {totalUniqueVehicles}V
          </span>
        </div>
      </div>

    </div>
  );
};
