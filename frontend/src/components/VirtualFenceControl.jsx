import React, { useState, useEffect } from 'react';
import { Shield, ShieldAlert, Plus, Trash2, Power, Eye, Crosshair, Check, AlertTriangle, Layers } from 'lucide-react';
import { getFences, createFence, deleteFence, toggleFence } from '../services/api.js';

export const VirtualFenceControl = ({
  cameraId,
  isDrawing,
  onStartDrawing,
  onCancelDrawing,
  drawnPoints,
  onClearDrawnPoints,
  activeIntrusionsCount = 0
}) => {
  const [fences, setFences] = useState([]);
  const [fenceName, setFenceName] = useState('Restricted Border Zone');
  const [fenceType, setFenceType] = useState('polygon'); // 'polygon' | 'line'
  const [severity, setSeverity] = useState('HIGH'); // 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  const [isLoading, setIsLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);

  // Fetch fences for current camera
  const loadFences = async () => {
    try {
      const data = await getFences(cameraId);
      setFences(data);
    } catch (err) {
      console.error('Failed to load fences:', err);
    }
  };

  useEffect(() => {
    loadFences();
  }, [cameraId]);

  const handleSaveFence = async () => {
    if (!drawnPoints || drawnPoints.length < (fenceType === 'polygon' ? 3 : 2)) {
      setStatusMessage({ type: 'error', text: 'Draw points on video before saving' });
      return;
    }

    setIsLoading(true);
    try {
      await createFence({
        name: fenceName.trim() || 'Restricted Zone',
        type: fenceType,
        points: drawnPoints,
        camera_id: cameraId || 'CAM-01',
        enabled: true,
        severity: severity
      });
      onClearDrawnPoints();
      onCancelDrawing();
      setStatusMessage({ type: 'success', text: 'Virtual Fence created successfully!' });
      loadFences();
    } catch (err) {
      console.error('Failed to save fence:', err);
      setStatusMessage({ type: 'error', text: 'Error saving virtual fence' });
    } finally {
      setIsLoading(false);
      setTimeout(() => setStatusMessage(null), 4000);
    }
  };

  const handleToggle = async (fenceId) => {
    try {
      await toggleFence(fenceId);
      loadFences();
    } catch (err) {
      console.error('Failed to toggle fence:', err);
    }
  };

  const handleDelete = async (fenceId) => {
    try {
      await deleteFence(fenceId);
      loadFences();
    } catch (err) {
      console.error('Failed to delete fence:', err);
    }
  };

  const activeFencesCount = fences.filter((f) => f.enabled).length;

  return (
    <div className="bg-command-card border border-command-border rounded-xl flex flex-col shadow-lg overflow-hidden">
      
      {/* Header */}
      <div className="p-3.5 border-b border-command-border flex items-center justify-between bg-slate-900/80">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
            Virtual Fence Configurator
          </h3>
        </div>
        <div className="flex items-center gap-2">
          {activeIntrusionsCount > 0 && (
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-red-950 text-red-400 border border-red-700 font-bold animate-pulse">
              🚨 {activeIntrusionsCount} INTRUSION
            </span>
          )}
          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-cyan-950 text-cyan-400 border border-cyan-800">
            {activeFencesCount} ACTIVE
          </span>
        </div>
      </div>

      <div className="p-4 space-y-4">
        
        {/* Status Message Notification */}
        {statusMessage && (
          <div className={`p-2 rounded-lg text-xs font-mono flex items-center gap-2 ${
            statusMessage.type === 'error'
              ? 'bg-red-950/80 text-red-300 border border-red-800'
              : 'bg-emerald-950/80 text-emerald-300 border border-emerald-800'
          }`}>
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>{statusMessage.text}</span>
          </div>
        )}

        {/* Fence Creation Form */}
        <div className="space-y-3 bg-slate-900/60 p-3 rounded-lg border border-slate-800/80">
          
          {/* Fence Name */}
          <div>
            <label className="text-[11px] font-mono text-slate-400 block mb-1">
              Fence / Zone Name
            </label>
            <input
              type="text"
              value={fenceName}
              onChange={(e) => setFenceName(e.target.value)}
              placeholder="e.g. Restricted Border Zone"
              className="w-full px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>

          {/* Type Selector: Polygon vs Line */}
          <div>
            <label className="text-[11px] font-mono text-slate-400 block mb-1">
              Fence Geometry Type
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => {
                  setFenceType('polygon');
                  onClearDrawnPoints();
                }}
                className={`py-1.5 rounded-lg text-xs font-mono font-bold transition-all border ${
                  fenceType === 'polygon'
                    ? 'bg-cyan-600/30 text-cyan-300 border-cyan-500 shadow-sm'
                    : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
                }`}
              >
                Polygon Zone
              </button>
              <button
                type="button"
                onClick={() => {
                  setFenceType('line');
                  onClearDrawnPoints();
                }}
                className={`py-1.5 rounded-lg text-xs font-mono font-bold transition-all border ${
                  fenceType === 'line'
                    ? 'bg-cyan-600/30 text-cyan-300 border-cyan-500 shadow-sm'
                    : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
                }`}
              >
                Line Crossing
              </button>
            </div>
          </div>

          {/* Severity Selector */}
          <div>
            <label className="text-[11px] font-mono text-slate-400 block mb-1">
              Intrusion Severity Level
            </label>
            <div className="grid grid-cols-4 gap-1.5">
              {['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].map((lvl) => (
                <button
                  key={lvl}
                  type="button"
                  onClick={() => setSeverity(lvl)}
                  className={`py-1 rounded text-[10px] font-mono font-bold transition-all border ${
                    severity === lvl
                      ? lvl === 'CRITICAL'
                        ? 'bg-red-600 text-white border-red-500 shadow'
                        : lvl === 'HIGH'
                        ? 'bg-amber-600 text-white border-amber-500 shadow'
                        : 'bg-cyan-600 text-white border-cyan-500 shadow'
                      : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-300'
                  }`}
                >
                  {lvl}
                </button>
              ))}
            </div>
          </div>

          {/* Drawing Controls */}
          <div className="pt-1 flex items-center gap-2">
            {!isDrawing ? (
              <button
                type="button"
                onClick={() => onStartDrawing(fenceType)}
                className="flex-1 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-mono font-bold flex items-center justify-center gap-1.5 shadow glow-cyan transition-all"
              >
                <Crosshair className="w-3.5 h-3.5" /> Draw on Video
              </button>
            ) : (
              <>
                <button
                  type="button"
                  onClick={handleSaveFence}
                  disabled={isLoading || !drawnPoints || drawnPoints.length < (fenceType === 'polygon' ? 3 : 2)}
                  className="flex-1 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg text-xs font-mono font-bold flex items-center justify-center gap-1.5 shadow glow-emerald transition-all"
                >
                  <Check className="w-3.5 h-3.5" /> Save Fence
                </button>
                <button
                  type="button"
                  onClick={() => {
                    onClearDrawnPoints();
                    onCancelDrawing();
                  }}
                  className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-mono transition-colors"
                >
                  Clear
                </button>
              </>
            )}
          </div>

        </div>

        {/* Existing Fences List */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400">
            <span>Configured Fences ({fences.length})</span>
            <span className="text-[10px] text-slate-500">Camera: {cameraId}</span>
          </div>

          <div className="space-y-2 max-h-[220px] overflow-y-auto">
            {fences.length === 0 ? (
              <div className="text-center py-6 text-slate-600 font-mono text-xs border border-dashed border-slate-800 rounded-lg">
                No virtual fences configured for this camera. Click "Draw on Video" to add one.
              </div>
            ) : (
              fences.map((fence) => (
                <div
                  key={fence.id}
                  className={`p-2.5 rounded-lg border transition-all flex items-center justify-between ${
                    fence.enabled
                      ? 'bg-slate-900/80 border-slate-800'
                      : 'bg-slate-950/60 border-slate-900 opacity-60'
                  }`}
                >
                  <div className="min-w-0 flex-1 pr-2">
                    <div className="flex items-center gap-1.5">
                      <span className="font-mono text-xs font-bold text-slate-200 truncate">
                        {fence.name}
                      </span>
                      <span className={`text-[9px] font-mono px-1.5 py-0.2 rounded font-bold uppercase ${
                        fence.severity === 'CRITICAL'
                          ? 'bg-red-950 text-red-300 border border-red-800'
                          : fence.severity === 'HIGH'
                          ? 'bg-amber-950 text-amber-300 border border-amber-800'
                          : 'bg-cyan-950 text-cyan-300 border border-cyan-800'
                      }`}>
                        {fence.severity}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 mt-0.5 text-[10px] font-mono text-slate-500">
                      <span>{fence.id}</span>
                      <span>•</span>
                      <span className="capitalize">{fence.type}</span>
                      <span>•</span>
                      <span>{fence.points?.length || 0} pts</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-1 shrink-0">
                    <button
                      onClick={() => handleToggle(fence.id)}
                      title={fence.enabled ? 'Disable Fence' : 'Enable Fence'}
                      className={`p-1.5 rounded-md transition-colors ${
                        fence.enabled
                          ? 'bg-emerald-950/80 text-emerald-400 hover:bg-emerald-900'
                          : 'bg-slate-800 text-slate-500 hover:bg-slate-700'
                      }`}
                    >
                      <Power className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => handleDelete(fence.id)}
                      title="Delete Fence"
                      className="p-1.5 rounded-md bg-slate-800/80 hover:bg-red-950 hover:text-red-400 text-slate-400 transition-colors"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>
    </div>
  );
};
