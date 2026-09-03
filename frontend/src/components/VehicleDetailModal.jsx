import React from 'react';
import { X, Car, ShieldCheck, CreditCard, Compass, Clock, MapPin, Layers, Gauge } from 'lucide-react';

export const VehicleDetailModal = ({ vehicle, onClose }) => {
  if (!vehicle) return null;

  const confPercent = Math.round((vehicle.confidence || 0) * 100);
  const plate = vehicle.plate?.plate_number;
  const plateConf = Math.round((vehicle.plate?.ocr_confidence || 0) * 100);
  const plateStatus = vehicle.plate?.status || 'Not Detected';
  const cx = vehicle.center ? Math.round(vehicle.center[0]) : 0;
  const cy = vehicle.center ? Math.round(vehicle.center[1]) : 0;

  return (
    <div className="bg-command-card border border-cyan-500/40 rounded-xl p-5 shadow-2xl space-y-4">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-command-border pb-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-cyan-500/20 border border-cyan-500/40 rounded-lg font-mono font-black text-cyan-400 text-sm">
            {vehicle.track_id}
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-mono">
              Vehicle Inspection
            </h3>
            <p className="text-xs text-slate-400 font-mono">
              Classification: <strong className="text-cyan-300">{vehicle.vehicle_type}</strong>
            </p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* ANPR Plate Highlight Banner */}
      <div className="bg-slate-950/90 border border-amber-500/40 p-3 rounded-lg flex items-center justify-between">
        <div className="flex items-center gap-2">
          <CreditCard className="w-4 h-4 text-amber-400" />
          <div>
            <span className="text-[10px] text-slate-400 font-mono uppercase block">License Plate</span>
            <span className="text-base font-black font-mono text-amber-300 tracking-wider">
              {plate || plateStatus}
            </span>
          </div>
        </div>
        {plate && (
          <div className="text-right">
            <span className="text-[10px] text-slate-400 font-mono block">OCR Match</span>
            <span className="text-sm font-bold font-mono text-emerald-400">{plateConf}%</span>
          </div>
        )}
      </div>

      {/* Detail Metrics Grid */}
      <div className="grid grid-cols-2 gap-3 text-xs">
        
        {/* Detection Confidence */}
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <div className="flex items-center gap-1.5 text-slate-400 font-mono mb-1">
            <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
            <span>Detection Conf</span>
          </div>
          <span className="text-base font-bold font-mono text-cyan-400">{confPercent}%</span>
        </div>

        {/* Direction */}
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <div className="flex items-center gap-1.5 text-slate-400 font-mono mb-1">
            <Compass className="w-3.5 h-3.5 text-blue-400" />
            <span>Direction</span>
          </div>
          <span className="text-base font-bold font-mono text-blue-400">{vehicle.direction}</span>
        </div>

        {/* Status / Speed */}
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <div className="flex items-center gap-1.5 text-slate-400 font-mono mb-1">
            <Gauge className="w-3.5 h-3.5 text-amber-400" />
            <span>Relative Motion</span>
          </div>
          <span className="text-base font-bold font-mono text-amber-400 uppercase">
            {vehicle.status} ({vehicle.relative_speed || 'Normal'})
          </span>
        </div>

        {/* Frames Tracked */}
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <div className="flex items-center gap-1.5 text-slate-400 font-mono mb-1">
            <Layers className="w-3.5 h-3.5 text-purple-400" />
            <span>Frames Tracked</span>
          </div>
          <span className="text-base font-bold font-mono text-purple-400">
            {vehicle.total_frames_tracked || 1}
          </span>
        </div>

      </div>

      {/* Position Coordinates */}
      <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800 flex items-center justify-between text-xs font-mono">
        <div className="flex items-center gap-1.5 text-slate-300">
          <MapPin className="w-3.5 h-3.5 text-red-400" />
          <span>Center Coordinates:</span>
        </div>
        <span className="text-slate-200">X: {cx}, Y: {cy}</span>
      </div>

      {/* Crop Previews (if available) */}
      {(vehicle.plate?.plate_crop_url || vehicle.plate?.vehicle_crop_url) && (
        <div className="grid grid-cols-2 gap-2 pt-1">
          {vehicle.plate.plate_crop_url && (
            <div className="bg-black/60 p-2 rounded border border-slate-800 text-center">
              <span className="text-[10px] font-mono text-slate-400 block mb-1">Plate Crop</span>
              <img
                src={vehicle.plate.plate_crop_url}
                alt="Plate"
                className="h-12 mx-auto object-contain"
              />
            </div>
          )}
          {vehicle.plate.vehicle_crop_url && (
            <div className="bg-black/60 p-2 rounded border border-slate-800 text-center">
              <span className="text-[10px] font-mono text-slate-400 block mb-1">Vehicle Crop</span>
              <img
                src={vehicle.plate.vehicle_crop_url}
                alt="Vehicle"
                className="h-12 mx-auto object-contain"
              />
            </div>
          )}
        </div>
      )}

      {/* Lifecycle stats */}
      <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 bg-slate-900/50 p-2 rounded-lg border border-slate-800">
        <div className="flex items-center gap-1">
          <Clock className="w-3 h-3 text-slate-500" />
          <span>First Seen: Frame #{vehicle.first_seen_frame || 1}</span>
        </div>
        <div>
          <span>Last Seen: Frame #{vehicle.last_seen_frame || 1}</span>
        </div>
      </div>

    </div>
  );
};
