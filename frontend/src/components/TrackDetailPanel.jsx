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

      {/* Facial Recognition & Identity Card */}
      {track.face && (
        <div className={`p-3.5 rounded-xl border space-y-3 ${
          track.face.status === 'recognized'
            ? 'bg-emerald-950/40 border-emerald-500/50'
            : track.face.status === 'unknown'
            ? 'bg-amber-950/40 border-amber-500/50'
            : 'bg-slate-900/80 border-slate-800'
        }`}>
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
            <div className="flex items-center gap-2">
              <ShieldCheck className={`w-4 h-4 ${
                track.face.status === 'recognized'
                  ? 'text-emerald-400'
                  : track.face.status === 'unknown'
                  ? 'text-amber-400'
                  : 'text-cyan-400'
              }`} />
              <h4 className="text-xs font-bold font-mono uppercase tracking-wider text-slate-200">
                Facial Biometric Identity
              </h4>
            </div>

            <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
              track.face.status === 'recognized'
                ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                : track.face.status === 'unknown'
                ? 'bg-amber-950 text-amber-300 border border-amber-800'
                : 'bg-slate-800 text-slate-400'
            }`}>
              {track.face.status === 'recognized' ? 'Verified Staff' : track.face.status === 'unknown' ? 'Unknown Person' : 'Searching Face'}
            </span>
          </div>

          <div className="flex items-center gap-3">
            {/* Face Crop Thumbnail */}
            <div className="w-14 h-14 rounded-lg bg-slate-950 border border-slate-800 overflow-hidden shrink-0 flex items-center justify-center">
              {track.face.face_crop_url ? (
                <img
                  src={`http://localhost:8000${track.face.face_crop_url}`}
                  alt="Face Crop"
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = '';
                  }}
                />
              ) : (
                <User className="w-7 h-7 text-slate-600" />
              )}
            </div>

            <div className="flex-1 min-w-0">
              <div className="text-sm font-bold text-slate-100 truncate">
                {track.face.name}
              </div>
              {track.face.person_id && (
                <span className="text-[11px] font-mono text-cyan-400">
                  ID: {track.face.person_id}
                </span>
              )}
              <div className="text-[11px] text-slate-400 truncate">
                {track.face.role || 'Personnel'}
              </div>
            </div>
          </div>

          {/* Biometric Match Score vs Face Detection Confidence */}
          <div className="grid grid-cols-2 gap-2 text-xs font-mono">
            <div className="bg-slate-950/80 p-2 rounded border border-slate-800/80">
              <span className="text-slate-500 block text-[10px]">Recognition Match:</span>
              <span className={`font-bold text-sm ${
                track.face.status === 'recognized' ? 'text-emerald-400' : 'text-amber-400'
              }`}>
                {Math.round((track.face.match_score || 0) * 100)}%
              </span>
            </div>
            <div className="bg-slate-950/80 p-2 rounded border border-slate-800/80">
              <span className="text-slate-500 block text-[10px]">Face Detection Conf:</span>
              <span className="font-bold text-sm text-cyan-400">
                {Math.round((track.face.face_confidence || 0) * 100)}%
              </span>
            </div>
          </div>

          {/* Privacy Notice Pill */}
          <p className="text-[10px] text-slate-500 font-sans italic leading-tight pt-1">
            Privacy Notice: Biometric facial identification is restricted to authorized surveillance monitoring.
          </p>
        </div>
      )}

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
