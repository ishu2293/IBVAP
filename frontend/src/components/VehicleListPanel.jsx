import React from 'react';
import { Car, Truck, Bike, Bus, ShieldCheck, ArrowUp, ArrowDown, ArrowLeft, ArrowRight, ArrowUpRight, ArrowUpLeft, ArrowDownRight, ArrowDownLeft, PauseCircle, ChevronRight, CreditCard } from 'lucide-react';

const getVehicleIcon = (type) => {
  switch (type?.toUpperCase()) {
    case 'TRUCK': return <Truck className="w-4 h-4 text-amber-400" />;
    case 'MOTORCYCLE': return <Bike className="w-4 h-4 text-red-400" />;
    case 'BUS': return <Bus className="w-4 h-4 text-purple-400" />;
    default: return <Car className="w-4 h-4 text-cyan-400" />;
  }
};

const getDirectionIcon = (direction) => {
  switch (direction) {
    case 'NORTH': return <ArrowUp className="w-3.5 h-3.5 text-emerald-400" />;
    case 'SOUTH': return <ArrowDown className="w-3.5 h-3.5 text-blue-400" />;
    case 'EAST': return <ArrowRight className="w-3.5 h-3.5 text-amber-400" />;
    case 'WEST': return <ArrowLeft className="w-3.5 h-3.5 text-purple-400" />;
    case 'NORTH-EAST': return <ArrowUpRight className="w-3.5 h-3.5 text-emerald-400" />;
    case 'NORTH-WEST': return <ArrowUpLeft className="w-3.5 h-3.5 text-emerald-400" />;
    case 'SOUTH-EAST': return <ArrowDownRight className="w-3.5 h-3.5 text-blue-400" />;
    case 'SOUTH-WEST': return <ArrowDownLeft className="w-3.5 h-3.5 text-blue-400" />;
    default: return <PauseCircle className="w-3.5 h-3.5 text-slate-500" />;
  }
};

export const VehicleListPanel = ({
  vehicles = [],
  selectedTrackId,
  onSelectTrack
}) => {
  return (
    <div className="bg-command-card border border-command-border rounded-xl flex flex-col h-full shadow-lg overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-command-border flex items-center justify-between bg-slate-900/80">
        <div className="flex items-center gap-2">
          <Car className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
            Active Vehicles
          </h3>
        </div>
        <span className="px-2 py-0.5 rounded-full text-xs font-mono bg-cyan-950 text-cyan-400 border border-cyan-800">
          {vehicles.length} ACTIVE
        </span>
      </div>

      {/* Vehicle List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2 max-h-[380px]">
        {vehicles.length === 0 ? (
          <div className="text-center py-8 px-4 text-slate-500 font-mono text-xs">
            No vehicle tracks currently active in camera view.
          </div>
        ) : (
          vehicles.map((v) => {
            const isSelected = v.track_id === selectedTrackId;
            const confPercent = Math.round(v.confidence * 100);
            const plate = v.plate?.plate_number;
            const plateConf = Math.round((v.plate?.ocr_confidence || 0) * 100);
            const plateStatus = v.plate?.status || 'Not Detected';

            return (
              <div
                key={v.track_id}
                onClick={() => onSelectTrack(isSelected ? null : v.track_id)}
                className={`p-3 rounded-lg border transition-all cursor-pointer flex flex-col gap-2 ${
                  isSelected
                    ? 'bg-cyan-950/50 border-cyan-500 shadow-md ring-1 ring-cyan-500/40'
                    : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900'
                }`}
              >
                {/* Row 1: ID, Type, Conf, Chevron */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <div className={`p-1.5 rounded-lg font-mono font-bold text-xs flex items-center gap-1.5 ${
                      isSelected ? 'bg-cyan-500 text-slate-950' : 'bg-slate-800 text-cyan-400 border border-slate-700'
                    }`}>
                      {getVehicleIcon(v.vehicle_type)}
                      <span>{v.track_id}</span>
                    </div>

                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-slate-200 uppercase font-mono">
                          {v.vehicle_type}
                        </span>
                        <span className="text-[11px] font-mono text-cyan-400">
                          {confPercent}%
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1 text-[11px] font-mono text-slate-400">
                      {getDirectionIcon(v.direction)}
                      <span>{v.direction}</span>
                    </div>
                    <ChevronRight className={`w-4 h-4 transition-transform ${
                      isSelected ? 'text-cyan-400 translate-x-0.5' : 'text-slate-600'
                    }`} />
                  </div>
                </div>

                {/* Row 2: ANPR Plate Badge */}
                <div className="flex items-center justify-between bg-slate-950/70 px-2.5 py-1.5 rounded border border-slate-800/80 text-xs font-mono">
                  <div className="flex items-center gap-1.5">
                    <CreditCard className="w-3.5 h-3.5 text-amber-400" />
                    <span className="text-slate-400 text-[11px]">Plate:</span>
                    {plate ? (
                      <span className="font-bold text-amber-300 tracking-wider">
                        {plate}
                      </span>
                    ) : plateStatus === 'Recognizing' ? (
                      <span className="text-cyan-400 text-[11px] animate-pulse">Recognizing...</span>
                    ) : plateStatus === 'Uncertain' ? (
                      <span className="text-amber-500/80 text-[11px]">Uncertain</span>
                    ) : (
                      <span className="text-slate-500 text-[11px]">Not Detected</span>
                    )}
                  </div>

                  {plate && (
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-amber-950/80 text-amber-400 border border-amber-800/60">
                      {plateConf}% OCR
                    </span>
                  )}
                </div>

              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
