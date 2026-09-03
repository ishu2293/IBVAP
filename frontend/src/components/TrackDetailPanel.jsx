import React from 'react';
import { X, User, MapPin, Compass, Clock, Layers, ShieldCheck } from 'lucide-react';

export const TrackDetailPanel = ({ track, onClose }) => {
  if (!track) return null;

  const confPercent = Math.round(track.confidence * 100);
  const cx = Math.round(track.center[0]);
  const cy = Math.round(track.center[1]);
  const fx = Math.round(track.foot_point[0]);
  const fy = Math.round(track.foot_point[1]);

  return (
    <div className="bg-command-card border border-emerald-500/40 rounded-xl p-5 shadow-2xl space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-command-border pb-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-emerald-500/20 border border-emerald-500/40 rounded-lg font-mono font-black text-emerald-400 text-sm">
            {track.track_id}
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-mono">
              Track Details
            </h3>
            <p className="text-xs text-slate-400">Class: Person</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Grid of details */}
      <div className="grid grid-cols-2 gap-3 text-xs">
        
        {/* Confidence */}
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <div className="flex items-center gap-1.5 text-slate-400 font-mono mb-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Confidence</span>
          </div>
          <span className="text-base font-bold font-mono text-emerald-400">{confPercent}%</span>
        </div>

        {/* Direction */}
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <div className="flex items-center gap-1.5 text-slate-400 font-mono mb-1">
            <Compass className="w-3.5 h-3.5 text-blue-400" />
            <span>Direction</span>
          </div>
          <span className="text-base font-bold font-mono text-blue-400">{track.direction}</span>
        </div>

        {/* Status */}
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <div className="flex items-center gap-1.5 text-slate-400 font-mono mb-1">
            <User className="w-3.5 h-3.5 text-amber-400" />
            <span>Status</span>
          </div>
          <span className="text-base font-bold font-mono text-amber-400 uppercase">{track.status}</span>
        </div>

        {/* Frames Tracked */}
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <div className="flex items-center gap-1.5 text-slate-400 font-mono mb-1">
            <Layers className="w-3.5 h-3.5 text-purple-400" />
            <span>Frames Tracked</span>
          </div>
          <span className="text-base font-bold font-mono text-purple-400">{track.total_frames_tracked}</span>
        </div>

      </div>

      {/* Position Coordinates */}
      <div className="bg-slate-900/80 p-3.5 rounded-lg border border-slate-800 space-y-2">
        <div className="flex items-center gap-1.5 text-xs font-mono font-bold text-slate-300">
          <MapPin className="w-3.5 h-3.5 text-red-400" />
          <span>Current Coordinates</span>
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs font-mono">
          <div className="bg-slate-950 p-2 rounded border border-slate-800/80">
            <span className="text-slate-500">Center:</span> <span className="text-slate-200">X:{cx}, Y:{cy}</span>
          </div>
          <div className="bg-slate-950 p-2 rounded border border-slate-800/80">
            <span className="text-slate-500">Foot:</span> <span className="text-slate-200">X:{fx}, Y:{fy}</span>
          </div>
        </div>
      </div>

      {/* Lifecycle stats */}
      <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 bg-slate-900/50 p-2.5 rounded-lg border border-slate-800">
        <div className="flex items-center gap-1">
          <Clock className="w-3 h-3 text-slate-500" />
          <span>First Seen: Frame #{track.first_seen_frame}</span>
        </div>
        <div>
          <span>Last Seen: Frame #{track.last_seen_frame}</span>
        </div>
      </div>

    </div>
  );
};
