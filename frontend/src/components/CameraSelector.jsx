import React from 'react';
import { Camera, CheckCircle2 } from 'lucide-react';

export const CameraSelector = ({
  cameras,
  selectedCameraId,
  onSelectCamera,
  disabled
}) => {
  return (
    <div className="bg-command-card border border-command-border rounded-xl p-4 shadow-lg">
      <div className="flex items-center gap-2 mb-3">
        <Camera className="w-4 h-4 text-emerald-400" />
        <h3 className="text-xs font-bold text-slate-200 tracking-wider uppercase font-mono">
          CCTV Camera Selector
        </h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {cameras.map((cam) => {
          const isSelected = cam.id === selectedCameraId;

          return (
            <button
              key={cam.id}
              onClick={() => onSelectCamera(cam.id)}
              disabled={disabled}
              className={`flex items-start justify-between p-3 rounded-lg border text-left transition-all ${
                isSelected
                  ? 'bg-emerald-950/40 border-emerald-500/60 ring-1 ring-emerald-500/50 shadow-md'
                  : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900'
              } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold text-white">{cam.id}</span>
                  <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono bg-emerald-900/60 text-emerald-400 border border-emerald-700/50">
                    🟢 {cam.status}
                  </span>
                </div>
                <div className="text-sm font-semibold text-slate-200 mt-1">{cam.name}</div>
                <div className="text-xs text-slate-400 mt-0.5 font-mono">{cam.location}</div>
              </div>

              {isSelected && (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};
