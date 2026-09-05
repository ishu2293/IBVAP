import React, { useState, useRef, useEffect } from 'react';
import { Check, Trash2, Undo, ShieldAlert, Crosshair } from 'lucide-react';

export const FenceDrawingCanvas = ({
  fenceType = 'polygon',
  onFinishDrawing,
  onCancel,
  existingFences = []
}) => {
  const [points, setPoints] = useState([]);
  const [mousePos, setMousePos] = useState(null);
  const containerRef = useRef(null);

  const handlePointerMove = (e) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const y = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));
    setMousePos([x, y]);
  };

  const handleClick = (e) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const y = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));

    if (fenceType === 'line') {
      if (points.length === 0) {
        setPoints([[x, y]]);
      } else if (points.length === 1) {
        const linePoints = [points[0], [x, y]];
        setPoints(linePoints);
        onFinishDrawing(linePoints);
      }
    } else {
      // Polygon mode
      setPoints((prev) => [...prev, [x, y]]);
    }
  };

  const handleUndo = (e) => {
    e.stopPropagation();
    setPoints((prev) => prev.slice(0, -1));
  };

  const handleClear = (e) => {
    e.stopPropagation();
    setPoints([]);
  };

  const handleCompletePolygon = (e) => {
    e.stopPropagation();
    if (points.length >= 3) {
      onFinishDrawing(points);
    }
  };

  return (
    <div
      ref={containerRef}
      onMouseMove={handlePointerMove}
      onClick={handleClick}
      className="absolute inset-0 z-30 cursor-crosshair select-none overflow-hidden bg-black/30 backdrop-blur-[1px]"
    >
      {/* HUD Guide Banner */}
      <div className="absolute top-3 left-1/2 -translate-x-1/2 bg-slate-950/90 border border-cyan-500/60 px-4 py-1.5 rounded-full shadow-2xl flex items-center gap-3 pointer-events-auto">
        <div className="flex items-center gap-1.5 text-cyan-400 font-mono text-xs font-bold">
          <Crosshair className="w-3.5 h-3.5 animate-spin" />
          <span>DRAWING MODE: {fenceType === 'polygon' ? 'POLYGON ZONE' : 'LINE CROSSING'}</span>
        </div>
        <span className="text-slate-600">|</span>
        <span className="text-[11px] text-slate-300 font-mono">
          {fenceType === 'line'
            ? points.length === 0 ? 'Click to set Line Start Point' : 'Click to set Line End Point'
            : points.length < 3
            ? `Click points on video (${points.length}/3 minimum)`
            : `${points.length} points placed. Click Finish or add more`}
        </span>
      </div>

      {/* SVG Canvas for interactive visual feedback */}
      <svg className="w-full h-full pointer-events-none">
        {/* Render Existing Fences dimly */}
        {existingFences.map((ef) => {
          if (!ef.points || ef.points.length < 2) return null;
          const ptsStr = ef.points.map((p) => `${p[0] * 100}%,${p[1] * 100}%`).join(' ');
          return ef.type === 'polygon' ? (
            <polygon
              key={ef.id}
              points={ptsStr}
              fill="rgba(0, 255, 200, 0.05)"
              stroke="rgba(0, 255, 200, 0.3)"
              strokeWidth="1.5"
              strokeDasharray="4 4"
            />
          ) : (
            <line
              key={ef.id}
              x1={`${ef.points[0][0] * 100}%`}
              y1={`${ef.points[0][1] * 100}%`}
              x2={`${ef.points[1][0] * 100}%`}
              y2={`${ef.points[1][1] * 100}%`}
              stroke="rgba(0, 255, 200, 0.3)"
              strokeWidth="2"
              strokeDasharray="4 4"
            />
          );
        })}

        {/* Currently Drawing Geometry */}
        {fenceType === 'polygon' && points.length >= 2 && (
          <polygon
            points={points.map((p) => `${p[0] * 100}%,${p[1] * 100}%`).join(' ')}
            fill="rgba(6, 182, 212, 0.25)"
            stroke="#06b6d4"
            strokeWidth="2.5"
          />
        )}

        {/* Live Elastic Line to Mouse Cursor */}
        {points.length > 0 && mousePos && (
          <line
            x1={`${points[points.length - 1][0] * 100}%`}
            y1={`${points[points.length - 1][1] * 100}%`}
            x2={`${mousePos[0] * 100}%`}
            y2={`${mousePos[1] * 100}%`}
            stroke="#22d3ee"
            strokeWidth="2"
            strokeDasharray="5 5"
          />
        )}

        {/* Vertex handles */}
        {points.map((p, idx) => (
          <g key={idx}>
            <circle
              cx={`${p[0] * 100}%`}
              cy={`${p[1] * 100}%`}
              r="6"
              fill="#06b6d4"
              stroke="#ffffff"
              strokeWidth="2"
            />
            <text
              x={`${p[0] * 100 + 1}%`}
              y={`${p[1] * 100 - 1}%`}
              fill="#ffffff"
              fontSize="10"
              fontFamily="monospace"
              fontWeight="bold"
            >
              P{idx + 1}
            </text>
          </g>
        ))}
      </svg>

      {/* Floating Action Controls */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2 bg-slate-950/95 border border-slate-700/80 p-1.5 rounded-xl shadow-2xl pointer-events-auto">
        {points.length > 0 && (
          <>
            <button
              onClick={handleUndo}
              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-mono flex items-center gap-1.5 transition-colors"
            >
              <Undo className="w-3.5 h-3.5" /> Undo
            </button>
            <button
              onClick={handleClear}
              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-mono flex items-center gap-1.5 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" /> Clear
            </button>
          </>
        )}

        {fenceType === 'polygon' && points.length >= 3 && (
          <button
            onClick={handleCompletePolygon}
            className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white font-bold rounded-lg text-xs font-mono flex items-center gap-1.5 shadow glow-cyan transition-all"
          >
            <Check className="w-3.5 h-3.5" /> Complete Polygon ({points.length} pts)
          </button>
        )}

        <button
          onClick={onCancel}
          className="px-3 py-1.5 bg-red-950/80 hover:bg-red-900 text-red-200 border border-red-800/80 rounded-lg text-xs font-mono transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  );
};
