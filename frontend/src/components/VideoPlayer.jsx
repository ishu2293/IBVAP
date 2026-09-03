import React, { useState } from 'react';
import { Play, Pause, Square, RotateCcw, Upload, Sliders, Film, Radio } from 'lucide-react';

export const VideoPlayer = ({
  mode,
  frameImage,
  telemetry,
  streamStatus,
  onStart,
  onPause,
  onResume,
  onStop,
  onUpload,
  uploadedFilename,
  frameSkip,
  onFrameSkipChange,
}) => {
  const [dragActive, setDragActive] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0]);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUpload(e.dataTransfer.files[0]);
    }
  };

  const isStreaming = streamStatus === 'RUNNING';
  const isPaused = streamStatus === 'PAUSED';
  const isEnded = streamStatus === 'ENDED';

  return (
    <div className="bg-command-card border border-command-border rounded-xl flex flex-col overflow-hidden shadow-2xl">
      
      {/* Video Stream Container */}
      <div className="relative aspect-video bg-black flex items-center justify-center overflow-hidden border-b border-command-border">
        {frameImage ? (
          <img
            src={frameImage}
            alt="Processed Stream"
            className="w-full h-full object-contain"
          />
        ) : (
          <div className="flex flex-col items-center justify-center text-slate-500 p-8 text-center">
            {mode === 'upload' && !uploadedFilename ? (
              <div
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
                className={`w-full max-w-md p-8 rounded-xl border-2 border-dashed transition-all ${
                  dragActive ? 'border-emerald-400 bg-emerald-950/20' : 'border-slate-800 bg-slate-900/50'
                }`}
              >
                <Upload className="w-10 h-10 text-emerald-400 mx-auto mb-3" />
                <p className="text-sm font-semibold text-slate-200">Upload Video File</p>
                <p className="text-xs text-slate-400 mt-1">MP4, AVI, MOV, or MKV supported</p>
                <label className="mt-4 inline-block px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold cursor-pointer transition-colors">
                  Select Video
                  <input type="file" accept="video/*" onChange={handleFileChange} className="hidden" />
                </label>
              </div>
            ) : (
              <div className="space-y-3">
                <Radio className="w-12 h-12 text-slate-700 animate-pulse mx-auto" />
                <p className="text-sm font-mono text-slate-400">
                  {mode === 'demo'
                    ? 'Press START DETECTION to stream Demo CCTV'
                    : `Ready to process '${uploadedFilename}'`}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Video Ended Banner */}
        {isEnded && (
          <div className="absolute inset-0 bg-black/80 backdrop-blur-sm flex flex-col items-center justify-center">
            <Film className="w-12 h-12 text-amber-400 mb-2" />
            <h3 className="text-lg font-bold font-mono text-amber-400 uppercase">VIDEO ENDED</h3>
            <p className="text-xs text-slate-300 font-mono mt-1">Video stream processing completed</p>
            <button
              onClick={onStart}
              className="mt-4 px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-lg text-xs font-mono transition-colors flex items-center gap-2"
            >
              <RotateCcw className="w-3.5 h-3.5" /> RESTART STREAM
            </button>
          </div>
        )}
      </div>

      {/* Stream Controls & Settings Bar */}
      <div className="p-4 bg-slate-900/90 flex flex-wrap items-center justify-between gap-4">
        
        {/* Playback & Upload Buttons */}
        <div className="flex items-center gap-2 flex-wrap">
          {!isStreaming && !isPaused ? (
            <button
              onClick={onStart}
              disabled={mode === 'upload' && !uploadedFilename}
              className="px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs tracking-wide uppercase transition-all shadow-md glow-emerald flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Play className="w-4 h-4 fill-white" />
              START DETECTION
            </button>
          ) : isPaused ? (
            <button
              onClick={onResume}
              className="px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs uppercase transition-all flex items-center gap-2"
            >
              <Play className="w-4 h-4 fill-white" />
              RESUME
            </button>
          ) : (
            <button
              onClick={onPause}
              className="px-5 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs uppercase transition-all flex items-center gap-2"
            >
              <Pause className="w-4 h-4 fill-white" />
              PAUSE
            </button>
          )}

          {(isStreaming || isPaused) && (
            <button
              onClick={onStop}
              className="px-4 py-2 rounded-lg bg-red-600/80 hover:bg-red-600 text-white font-bold text-xs uppercase transition-all flex items-center gap-1.5"
            >
              <Square className="w-3.5 h-3.5 fill-white" />
              STOP
            </button>
          )}

          {/* Option to Upload New Video File anytime in Upload Mode */}
          {mode === 'upload' && (
            <label className="px-4 py-2 rounded-lg bg-purple-950/80 hover:bg-purple-900 border border-purple-700/60 text-purple-200 font-bold text-xs uppercase transition-all flex items-center gap-1.5 cursor-pointer">
              <Upload className="w-3.5 h-3.5" />
              <span>{uploadedFilename ? 'CHANGE / UPLOAD NEW VIDEO' : 'SELECT VIDEO'}</span>
              <input type="file" accept="video/*" onChange={handleFileChange} className="hidden" />
            </label>
          )}
        </div>

        {/* Frame Skipping Configurator */}
        <div className="flex items-center gap-3 bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800">
          <div className="flex items-center gap-1.5 text-xs text-slate-400 font-mono">
            <Sliders className="w-3.5 h-3.5 text-emerald-400" />
            <span>Process Every:</span>
          </div>
          <div className="flex items-center gap-1">
            {[1, 2, 3].map((val) => (
              <button
                key={val}
                onClick={() => onFrameSkipChange(val)}
                className={`px-2 py-0.5 rounded text-xs font-mono font-bold transition-colors ${
                  frameSkip === val
                    ? 'bg-emerald-500 text-slate-950'
                    : 'bg-slate-900 text-slate-400 hover:text-slate-200'
                }`}
              >
                {val}x
              </button>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
};
