import React from 'react';
import { CreditCard, Clock, Camera, Car, ShieldCheck } from 'lucide-react';

export const ANPRFeedPanel = ({ recentEvents = [], onViewHistory }) => {
  return (
    <div className="bg-command-card border border-command-border rounded-xl flex flex-col h-full shadow-lg overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-command-border flex items-center justify-between bg-slate-900/80">
        <div className="flex items-center gap-2">
          <CreditCard className="w-4 h-4 text-amber-400" />
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
            Recent ANPR Detections
          </h3>
        </div>
        {onViewHistory && (
          <button
            onClick={onViewHistory}
            className="text-[11px] font-mono text-amber-400 hover:text-amber-300 hover:underline"
          >
            View All Logs →
          </button>
        )}
      </div>

      {/* ANPR Feed List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2 max-h-[350px]">
        {recentEvents.length === 0 ? (
          <div className="text-center py-6 px-4 text-slate-500 font-mono text-xs">
            No license plates recognized in current stream yet.
          </div>
        ) : (
          recentEvents.map((evt) => {
            const confPercent = Math.round(evt.ocr_confidence * 100);

            return (
              <div
                key={evt.id || `${evt.vehicle_track_id}_${evt.plate_number}`}
                className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 hover:border-amber-500/40 transition-all flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  {/* Plate Badge */}
                  <div className="px-2.5 py-1.5 rounded-md bg-amber-950/60 border border-amber-500/50 font-mono font-black text-xs text-amber-300 tracking-wider shadow-inner">
                    {evt.plate_number}
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-bold text-cyan-400">
                        {evt.vehicle_track_id}
                      </span>
                      <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-300">
                        {evt.vehicle_type}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 mt-0.5 text-[10px] text-slate-400 font-mono">
                      <span className="flex items-center gap-1">
                        <Camera className="w-3 h-3 text-slate-500" />
                        {evt.camera_id}
                      </span>
                      <span>•</span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3 text-slate-500" />
                        {evt.timestamp}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="text-right">
                  <div className="flex items-center gap-1 text-xs font-mono font-bold text-emerald-400">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>{confPercent}%</span>
                  </div>
                  <span className="text-[9px] font-mono text-slate-500">CONFIDENCE</span>
                </div>

              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
