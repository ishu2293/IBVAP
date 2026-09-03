import React, { useState, useEffect } from 'react';
import { Search, Filter, Camera, Car, CreditCard, Clock, Image as ImageIcon, X, RefreshCw, ShieldCheck } from 'lucide-react';
import { getANPRHistory } from '../services/api.js';

export const ANPRHistoryView = () => {
  const [records, setRecords] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [searchPlate, setSearchPlate] = useState('');
  const [selectedType, setSelectedType] = useState('ALL');
  const [selectedCamera, setSelectedCamera] = useState('ALL');
  const [isLoading, setIsLoading] = useState(false);
  const [previewImage, setPreviewImage] = useState(null);

  const fetchHistory = async () => {
    setIsLoading(true);
    try {
      const data = await getANPRHistory({
        plate: searchPlate,
        vehicle_type: selectedType,
        camera_id: selectedCamera,
        limit: 100
      });
      setRecords(data.records || []);
      setTotalCount(data.total_anpr_reads || data.total || 0);
    } catch (err) {
      console.error('Failed to load ANPR history:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [selectedType, selectedCamera]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchHistory();
  };

  return (
    <div className="space-y-6">
      
      {/* Top Filter & Search Bar */}
      <div className="bg-command-card border border-command-border rounded-xl p-4 shadow-xl flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} className="flex-1 w-full flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchPlate}
              onChange={(e) => setSearchPlate(e.target.value)}
              placeholder="Search by license plate (e.g. MH12, DL01, RJ14)..."
              className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold font-mono text-xs rounded-lg transition-colors flex items-center gap-1.5"
          >
            Search
          </button>
        </form>

        {/* Filters */}
        <div className="flex items-center gap-3 w-full md:w-auto flex-wrap">
          
          {/* Vehicle Type Filter */}
          <div className="flex items-center gap-1.5 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800 text-xs font-mono">
            <Car className="w-3.5 h-3.5 text-cyan-400" />
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="bg-transparent text-slate-300 focus:outline-none cursor-pointer"
            >
              <option value="ALL">All Vehicle Types</option>
              <option value="CAR">Car</option>
              <option value="TRUCK">Truck</option>
              <option value="MOTORCYCLE">Motorcycle</option>
              <option value="BUS">Bus</option>
            </select>
          </div>

          {/* Camera Filter */}
          <div className="flex items-center gap-1.5 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800 text-xs font-mono">
            <Camera className="w-3.5 h-3.5 text-emerald-400" />
            <select
              value={selectedCamera}
              onChange={(e) => setSelectedCamera(e.target.value)}
              className="bg-transparent text-slate-300 focus:outline-none cursor-pointer"
            >
              <option value="ALL">All Cameras</option>
              <option value="CAM-01">CAM-01 (Longewala)</option>
              <option value="CAM-02">CAM-02 (Wagah-Attari)</option>
              <option value="CAM-03">CAM-03 (Galwan LAC)</option>
            </select>
          </div>

          {/* Refresh Button */}
          <button
            onClick={fetchHistory}
            className="p-2 bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800 rounded-lg transition-colors"
            title="Refresh Log"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-amber-400' : ''}`} />
          </button>

        </div>

      </div>

      {/* ANPR Log Table */}
      <div className="bg-command-card border border-command-border rounded-xl shadow-2xl overflow-hidden">
        
        <div className="p-4 border-b border-command-border flex items-center justify-between bg-slate-900/90">
          <div className="flex items-center gap-2">
            <CreditCard className="w-4 h-4 text-amber-400" />
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
              ANPR Historical Verification Log
            </h3>
          </div>
          <span className="text-xs font-mono text-slate-400">
            Showing <strong className="text-amber-400">{records.length}</strong> of {totalCount} total verified reads
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 uppercase tracking-wider text-[11px]">
              <tr>
                <th className="py-3 px-4">Time</th>
                <th className="py-3 px-4">Camera</th>
                <th className="py-3 px-4">Vehicle ID</th>
                <th className="py-3 px-4">Vehicle Type</th>
                <th className="py-3 px-4">License Plate</th>
                <th className="py-3 px-4">OCR Confidence</th>
                <th className="py-3 px-4">Direction</th>
                <th className="py-3 px-4 text-right">Crops / Evidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {records.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500 font-mono">
                    {isLoading ? 'Loading ANPR records...' : 'No ANPR records matched your query.'}
                  </td>
                </tr>
              ) : (
                records.map((r) => {
                  const conf = Math.round(r.ocr_confidence * 100);
                  return (
                    <tr key={r.id || `${r.vehicle_track_id}_${r.plate_number}`} className="hover:bg-slate-900/60 transition-colors">
                      <td className="py-3 px-4 flex items-center gap-1.5 text-slate-400">
                        <Clock className="w-3.5 h-3.5 text-slate-500" />
                        {r.timestamp}
                      </td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800">
                          {r.camera_id}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-bold text-cyan-400">
                        {r.vehicle_track_id}
                      </td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-200">
                          {r.vehicle_type}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-black text-amber-300 tracking-wider text-sm">
                        {r.plate_number}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-1 text-emerald-400 font-bold">
                          <ShieldCheck className="w-3.5 h-3.5" />
                          <span>{conf}%</span>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-slate-400">
                        {r.direction || 'IN'}
                      </td>
                      <td className="py-3 px-4 text-right space-x-2">
                        {r.plate_crop_url && (
                          <button
                            onClick={() => setPreviewImage({ url: r.plate_crop_url, title: `Plate Crop: ${r.plate_number}` })}
                            className="px-2 py-1 rounded bg-amber-950/80 hover:bg-amber-900 border border-amber-800/60 text-amber-300 text-[10px] transition-colors"
                          >
                            Plate Crop
                          </button>
                        )}
                        {r.vehicle_crop_url && (
                          <button
                            onClick={() => setPreviewImage({ url: r.vehicle_crop_url, title: `Vehicle Crop: ${r.vehicle_track_id}` })}
                            className="px-2 py-1 rounded bg-cyan-950/80 hover:bg-cyan-900 border border-cyan-800/60 text-cyan-300 text-[10px] transition-colors"
                          >
                            Vehicle Crop
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

      </div>

      {/* Image Preview Modal */}
      {previewImage && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-command-card border border-command-border rounded-xl max-w-lg w-full p-4 space-y-3 shadow-2xl">
            <div className="flex items-center justify-between border-b border-command-border pb-2">
              <h4 className="text-xs font-bold font-mono text-slate-200">{previewImage.title}</h4>
              <button
                onClick={() => setPreviewImage(null)}
                className="text-slate-400 hover:text-white p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="aspect-video bg-black rounded-lg overflow-hidden flex items-center justify-center">
              <img src={previewImage.url} alt="Evidence Crop" className="max-w-full max-h-full object-contain" />
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
