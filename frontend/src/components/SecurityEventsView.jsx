import React, { useState, useEffect } from 'react';
import { ShieldAlert, RefreshCw, Filter, Eye, Camera, Clock, User, AlertTriangle, ChevronLeft } from 'lucide-react';
import { getIntrusionHistory, getFenceStats } from '../services/api.js';

export const SecurityEventsView = () => {
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedCamera, setSelectedCamera] = useState('ALL');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedSnapshot, setSelectedSnapshot] = useState(null);

  const fetchHistory = async () => {
    setIsLoading(true);
    try {
      const [evts, st] = await Promise.all([
        getIntrusionHistory({ camera_id: selectedCamera, limit: 100 }),
        getFenceStats()
      ]);
      setEvents(evts);
      setStats(st);
    } catch (err) {
      console.error('Failed to fetch intrusion history:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [selectedCamera]);

  return (
    <div className="space-y-6">
      
      {/* Overview Stat Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        
        <div className="bg-command-card border border-command-border rounded-xl p-4">
          <span className="text-[11px] font-mono text-slate-400 uppercase">Total Intrusions</span>
          <div className="mt-1 text-2xl font-black font-mono text-red-400">
            {stats?.total_intrusions ?? events.length}
          </div>
        </div>

        <div className="bg-command-card border border-command-border rounded-xl p-4">
          <span className="text-[11px] font-mono text-slate-400 uppercase">Active Intrusions</span>
          <div className="mt-1 text-2xl font-black font-mono text-amber-400">
            {stats?.active_intrusions ?? 0}
          </div>
        </div>

        <div className="bg-command-card border border-command-border rounded-xl p-4">
          <span className="text-[11px] font-mono text-slate-400 uppercase">Configured Fences</span>
          <div className="mt-1 text-2xl font-black font-mono text-cyan-400">
            {stats?.total_fences ?? 0}
          </div>
        </div>

        <div className="bg-command-card border border-command-border rounded-xl p-4">
          <span className="text-[11px] font-mono text-slate-400 uppercase">Active Fences</span>
          <div className="mt-1 text-2xl font-black font-mono text-emerald-400">
            {stats?.active_fences ?? 0}
          </div>
        </div>

      </div>

      {/* Main Table Card */}
      <div className="bg-command-card border border-command-border rounded-xl shadow-2xl overflow-hidden">
        
        {/* Filter Controls Bar */}
        <div className="p-4 border-b border-command-border flex flex-wrap items-center justify-between gap-4 bg-slate-900/80">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-red-400" />
            <h2 className="text-sm font-bold font-mono text-slate-100 uppercase tracking-wider">
              Virtual Fence Security Breach Log
            </h2>
          </div>

          <div className="flex items-center gap-3">
            {/* Camera Filter */}
            <div className="flex items-center gap-1.5 bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800">
              <Filter className="w-3.5 h-3.5 text-slate-400" />
              <select
                value={selectedCamera}
                onChange={(e) => setSelectedCamera(e.target.value)}
                className="bg-transparent text-xs text-slate-300 font-mono focus:outline-none cursor-pointer"
              >
                <option value="ALL">All Cameras</option>
                <option value="CAM-01">CAM-01 (Longewala)</option>
                <option value="CAM-02">CAM-02 (Wagah)</option>
                <option value="CAM-03">CAM-03 (Galwan LAC)</option>
                <option value="UPLOAD">Uploaded Videos</option>
              </select>
            </div>

            {/* Refresh */}
            <button
              onClick={fetchHistory}
              disabled={isLoading}
              className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-mono transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Intrusion Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse font-mono text-xs">
            <thead>
              <tr className="bg-slate-950/80 text-slate-400 border-b border-command-border text-[11px]">
                <th className="py-3 px-4">TIME</th>
                <th className="py-3 px-4">EVENT ID</th>
                <th className="py-3 px-4">PERSON</th>
                <th className="py-3 px-4">BIOMETRIC IDENTITY</th>
                <th className="py-3 px-4">RESTRICTED ZONE</th>
                <th className="py-3 px-4">CAMERA</th>
                <th className="py-3 px-4">SEVERITY</th>
                <th className="py-3 px-4 text-right">EVIDENCE</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {events.length === 0 ? (
                <tr>
                  <td colSpan="8" className="py-12 text-center text-slate-500">
                    No security breach events recorded in history.
                  </td>
                </tr>
              ) : (
                events.map((evt) => (
                  <tr key={evt.event_id} className="hover:bg-slate-900/60 transition-colors">
                    <td className="py-3 px-4 text-slate-300">{evt.timestamp}</td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded bg-red-950 text-red-300 border border-red-800 font-bold">
                        {evt.event_id}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-bold text-slate-200">{evt.person_track_id}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        evt.identity !== 'UNKNOWN'
                          ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                          : 'bg-amber-950 text-amber-300 border border-amber-800'
                      }`}>
                        {evt.identity}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-cyan-300 font-semibold">{evt.fence_name}</td>
                    <td className="py-3 px-4 text-slate-400">{evt.camera_id}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        evt.severity === 'CRITICAL'
                          ? 'bg-red-900 text-red-100'
                          : evt.severity === 'HIGH'
                          ? 'bg-amber-900 text-amber-100'
                          : 'bg-cyan-900 text-cyan-100'
                      }`}>
                        {evt.severity}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      {evt.snapshot_url ? (
                        <button
                          onClick={() => setSelectedSnapshot(evt.snapshot_url)}
                          className="px-2.5 py-1 bg-cyan-950 hover:bg-cyan-900 text-cyan-300 border border-cyan-800 rounded text-[11px] font-semibold transition-colors inline-flex items-center gap-1"
                        >
                          <Eye className="w-3 h-3" /> Snapshot
                        </button>
                      ) : (
                        <span className="text-slate-600 text-[10px]">No Snapshot</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

      </div>

      {/* Snapshot Modal View */}
      {selectedSnapshot && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-3xl w-full p-4 space-y-3 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h4 className="text-sm font-bold font-mono text-red-400 flex items-center gap-2">
                <ShieldAlert className="w-4 h-4" /> EVIDENCE SNAPSHOT RECORD
              </h4>
              <button
                onClick={() => setSelectedSnapshot(null)}
                className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono"
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
