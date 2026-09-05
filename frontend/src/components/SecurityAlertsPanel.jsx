import React, { useState, useEffect, useRef } from 'react';
import { ShieldAlert, Volume2, VolumeX, AlertTriangle, Eye, Clock, User, Camera, ShieldCheck, ChevronRight } from 'lucide-react';

// Web Audio API Synthesizer for high-visibility military alert sound
const playIntrusionAlarm = () => {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();

    // Dual-tone urgent security chime (880Hz -> 587Hz)
    const now = ctx.currentTime;
    
    // Tone 1
    const osc1 = ctx.createOscillator();
    const gain1 = ctx.createGain();
    osc1.type = 'sawtooth';
    osc1.frequency.setValueAtTime(880, now);
    osc1.frequency.exponentialRampToValueAtTime(440, now + 0.18);
    gain1.gain.setValueAtTime(0.15, now);
    gain1.gain.exponentialRampToValueAtTime(0.01, now + 0.18);
    osc1.connect(gain1);
    gain1.connect(ctx.destination);
    osc1.start(now);
    osc1.stop(now + 0.18);

    // Tone 2 (pulse)
    const osc2 = ctx.createOscillator();
    const gain2 = ctx.createGain();
    osc2.type = 'sine';
    osc2.frequency.setValueAtTime(1174.66, now + 0.1);
    osc2.frequency.exponentialRampToValueAtTime(587.33, now + 0.28);
    gain2.gain.setValueAtTime(0.2, now + 0.1);
    gain2.gain.exponentialRampToValueAtTime(0.01, now + 0.28);
    osc2.connect(gain2);
    gain2.connect(ctx.destination);
    osc2.start(now + 0.1);
    osc2.stop(now + 0.28);

  } catch (err) {
    console.warn('[Audio Alert] Web Audio not allowed or failed:', err);
  }
};

export const SecurityAlertsPanel = ({
  recentAlerts = [],
  onViewAllHistory,
  soundEnabled = true,
  onToggleSound
}) => {
  const [selectedSnapshot, setSelectedSnapshot] = useState(null);
  const lastAlertIdRef = useRef(null);

  // Play sound ONLY on newly arrived intrusion events
  useEffect(() => {
    if (recentAlerts.length > 0) {
      const latest = recentAlerts[0];
      if (latest && latest.event_id !== lastAlertIdRef.current) {
        lastAlertIdRef.current = latest.event_id;
        if (soundEnabled) {
          playIntrusionAlarm();
        }
      }
    }
  }, [recentAlerts, soundEnabled]);

  return (
    <div className="bg-command-card border border-command-border rounded-xl flex flex-col shadow-xl overflow-hidden">
      
      {/* Header */}
      <div className="p-3.5 border-b border-command-border flex items-center justify-between bg-slate-900/80">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-red-400 animate-pulse" />
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
            Security Intrusion Alerts
          </h3>
        </div>

        <div className="flex items-center gap-2">
          {/* Audio Alarm Toggle */}
          <button
            onClick={onToggleSound}
            title={soundEnabled ? 'Alert Sound: ON' : 'Alert Sound: OFF'}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-mono transition-all border ${
              soundEnabled
                ? 'bg-red-950/80 border-red-800/80 text-red-300 shadow glow-red'
                : 'bg-slate-800/80 border-slate-700 text-slate-400'
            }`}
          >
            {soundEnabled ? <Volume2 className="w-3.5 h-3.5 text-red-400" /> : <VolumeX className="w-3.5 h-3.5 text-slate-500" />}
            <span>{soundEnabled ? 'SOUND ON' : 'MUTED'}</span>
          </button>

          {onViewAllHistory && (
            <button
              onClick={onViewAllHistory}
              className="text-[11px] font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-0.5"
            >
              Logs <ChevronRight className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>

      {/* Alert Feed */}
      <div className="p-3 space-y-2.5 max-h-[360px] overflow-y-auto">
        {recentAlerts.length === 0 ? (
          <div className="text-center py-8 px-4 text-slate-500 font-mono text-xs">
            <ShieldCheck className="w-8 h-8 text-emerald-500/40 mx-auto mb-2" />
            No intrusion breaches detected. Perimeter secure.
          </div>
        ) : (
          recentAlerts.map((alert, idx) => (
            <div
              key={alert.event_id || idx}
              className={`p-3 rounded-lg border transition-all ${
                alert.severity === 'CRITICAL'
                  ? 'bg-red-950/50 border-red-600/80 shadow glow-red'
                  : alert.severity === 'HIGH'
                  ? 'bg-amber-950/40 border-amber-500/70 shadow'
                  : 'bg-slate-900/80 border-slate-800'
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="p-1 rounded bg-red-600 text-white font-mono text-[10px] font-extrabold">
                    {alert.event_id || 'ALERT'}
                  </span>
                  <span className="text-xs font-bold font-mono text-red-400 flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    VIRTUAL FENCE INTRUSION
                  </span>
                </div>

                <span className="text-[10px] font-mono text-slate-400">
                  {alert.timestamp}
                </span>
              </div>

              {/* Grid details */}
              <div className="mt-2.5 grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs font-mono">
                <div className="bg-slate-950/80 p-1.5 rounded border border-slate-800/80">
                  <span className="text-[10px] text-slate-500 block">Person:</span>
                  <span className="font-bold text-slate-200">{alert.person_track_id}</span>
                </div>

                <div className="bg-slate-950/80 p-1.5 rounded border border-slate-800/80">
                  <span className="text-[10px] text-slate-500 block">Identity:</span>
                  <span className={`font-bold truncate block ${
                    alert.identity !== 'UNKNOWN' ? 'text-emerald-400' : 'text-amber-400'
                  }`}>
                    {alert.identity}
                  </span>
                </div>

                <div className="bg-slate-950/80 p-1.5 rounded border border-slate-800/80 col-span-2 sm:col-span-1">
                  <span className="text-[10px] text-slate-500 block">Zone:</span>
                  <span className="text-cyan-300 font-bold truncate block">{alert.fence_name}</span>
                </div>
              </div>

              {/* Snapshot Thumbnail Link if available */}
              {alert.snapshot_url && (
                <div className="mt-2 flex items-center justify-between pt-1 border-t border-slate-800/80">
                  <div className="flex items-center gap-1.5 text-[10px] font-mono text-slate-400">
                    <Camera className="w-3 h-3 text-cyan-400" />
                    <span>Camera: {alert.camera_id}</span>
                  </div>

                  <button
                    onClick={() => setSelectedSnapshot(alert.snapshot_url)}
                    className="text-[10px] font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1 underline"
                  >
                    <Eye className="w-3 h-3" /> View Evidence Snapshot
                  </button>
                </div>
              )}

            </div>
          ))
        )}
      </div>

      {/* Snapshot Modal View */}
      {selectedSnapshot && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-2xl w-full p-4 space-y-3 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h4 className="text-sm font-bold font-mono text-red-400 flex items-center gap-2">
                <ShieldAlert className="w-4 h-4" /> EVIDENCE SNAPSHOT
              </h4>
              <button
                onClick={() => setSelectedSnapshot(null)}
                className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono"
              >
                CLOSE
              </button>
            </div>
            <div className="aspect-video bg-black rounded-lg overflow-hidden flex items-center justify-center">
              <img
                src={selectedSnapshot.startsWith('http') ? selectedSnapshot : `http://localhost:8000${selectedSnapshot}`}
                alt="Intrusion Snapshot"
                className="w-full h-full object-contain"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = '';
                }}
              />
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
