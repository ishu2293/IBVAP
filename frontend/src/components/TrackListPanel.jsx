import React from 'react';
import { UserCheck, ArrowUpRight, ArrowUp, ArrowRight, ArrowDown, ArrowLeft, ArrowUpLeft, ArrowDownRight, ArrowDownLeft, PauseCircle, ChevronRight } from 'lucide-react';

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

export const TrackListPanel = ({
  tracks,
  selectedTrackId,
  onSelectTrack
}) => {
  return (
    <div className="bg-command-card border border-command-border rounded-xl flex flex-col h-full shadow-lg overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-command-border flex items-center justify-between bg-slate-900/80">
        <div className="flex items-center gap-2">
          <UserCheck className="w-4 h-4 text-emerald-400" />
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
            Active Person Tracks
          </h3>
        </div>
        <span className="px-2 py-0.5 rounded-full text-xs font-mono bg-emerald-950 text-emerald-400 border border-emerald-800">
          {tracks.length} ACTIVE
        </span>
      </div>

      {/* Track List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2 max-h-[480px]">
        {tracks.length === 0 ? (
          <div className="text-center py-10 px-4 text-slate-500 font-mono text-xs">
            No person tracks currently active in camera view.
          </div>
        ) : (
          tracks.map((track) => {
            const isSelected = track.track_id === selectedTrackId;
            const confPercent = Math.round(track.confidence * 100);

            return (
              <div
                key={track.track_id}
                onClick={() => onSelectTrack(isSelected ? null : track.track_id)}
                className={`p-3 rounded-lg border transition-all cursor-pointer flex items-center justify-between ${
                  isSelected
                    ? 'bg-emerald-950/50 border-emerald-500 shadow-md ring-1 ring-emerald-500/40'
                    : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg font-mono font-bold text-xs ${
                    isSelected ? 'bg-emerald-500 text-slate-950' : 'bg-slate-800 text-slate-200'
                  }`}>
                    {track.track_id}
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-slate-200">Person</span>
                      <span className="text-[11px] font-mono text-emerald-400">
                        {confPercent}%
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5 mt-0.5 text-xs text-slate-400">
                      {getDirectionIcon(track.direction)}
                      <span className="font-mono text-[11px] font-medium text-slate-300">
                        {track.direction}
                      </span>
                      <span className="text-slate-600">•</span>
                      <span className={`text-[11px] ${
                        track.status === 'Moving' ? 'text-emerald-400' : 'text-slate-400'
                      }`}>
                        {track.status}
                      </span>
                    </div>
                  </div>
                </div>

                <ChevronRight className={`w-4 h-4 transition-transform ${
                  isSelected ? 'text-emerald-400 translate-x-0.5' : 'text-slate-600'
                }`} />
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
