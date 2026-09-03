import React, { useState, useEffect, useRef } from 'react';
import { Header } from './components/Header.jsx';
import { CameraSelector } from './components/CameraSelector.jsx';
import { VideoPlayer } from './components/VideoPlayer.jsx';
import { StatsPanel } from './components/StatsPanel.jsx';
import { TrackListPanel } from './components/TrackListPanel.jsx';
import { TrackDetailPanel } from './components/TrackDetailPanel.jsx';
import { VehicleListPanel } from './components/VehicleListPanel.jsx';
import { VehicleDetailModal } from './components/VehicleDetailModal.jsx';
import { ANPRFeedPanel } from './components/ANPRFeedPanel.jsx';
import { ANPRHistoryView } from './components/ANPRHistoryView.jsx';

import { getSystemStatus, getCameras, uploadVideo, getRecentANPR, VideoWebSocketClient } from './services/api.js';

export const App = () => {
  const [activeTab, setActiveTab] = useState('live'); // 'live', 'anpr'
  const [sidePanelTab, setSidePanelTab] = useState('vehicles'); // 'vehicles', 'persons'
  
  const [systemStatus, setSystemStatus] = useState(null);
  const [cameras, setCameras] = useState([]);
  const [mode, setMode] = useState('demo');
  const [selectedCameraId, setSelectedCameraId] = useState('CAM-01');
  const [uploadedFilename, setUploadedFilename] = useState(null);

  const [telemetry, setTelemetry] = useState(null);
  const [frameImage, setFrameImage] = useState(null);
  const [streamStatus, setStreamStatus] = useState('STOPPED'); // STOPPED, RUNNING, PAUSED, ENDED
  const [selectedTrackId, setSelectedTrackId] = useState(null);
  const [frameSkip, setFrameSkip] = useState(1);
  const [recentANPREvents, setRecentANPREvents] = useState([]);

  const wsClientRef = useRef(null);

  // Fetch initial system status & cameras
  useEffect(() => {
    getSystemStatus()
      .then(setSystemStatus)
      .catch((err) => console.error('Failed to fetch system status:', err));

    getCameras()
      .then(setCameras)
      .catch((err) => console.error('Failed to fetch camera list:', err));

    getRecentANPR(10)
      .then(setRecentANPREvents)
      .catch((err) => console.error('Failed to fetch recent ANPR:', err));

    // Instantiate WebSocket Client
    const client = new VideoWebSocketClient();
    client.connect(
      (data) => {
        if (data.type === 'frame') {
          setFrameImage(data.image);
          setTelemetry(data.telemetry);
          setStreamStatus('RUNNING');

          // Check if there is a new ANPR event in this frame
          if (data.telemetry?.recent_anpr_event) {
            setRecentANPREvents((prev) => {
              const evt = data.telemetry.recent_anpr_event;
              const exists = prev.some((e) => e.id === evt.id || (e.vehicle_track_id === evt.vehicle_track_id && e.plate_number === evt.plate_number));
              if (exists) return prev;
              return [evt, ...prev.slice(0, 19)];
            });
          }
        } else if (data.type === 'video_ended') {
          setStreamStatus('ENDED');
        } else if (data.type === 'status') {
          setStreamStatus(data.status);
        } else if (data.type === 'error') {
          console.error('[WS Error]', data.message);
          setStreamStatus('STOPPED');
        }
      },
      (wsStatus) => {
        console.log('[WS Connection Status]', wsStatus);
      }
    );
    wsClientRef.current = client;

    return () => {
      client.disconnect();
    };
  }, []);

  // Control handlers
  const handleStartStream = () => {
    if (!wsClientRef.current) return;
    setStreamStatus('RUNNING');
    if (mode === 'demo') {
      wsClientRef.current.startDemoStream(selectedCameraId, frameSkip);
    } else if (uploadedFilename) {
      wsClientRef.current.startUploadStream(uploadedFilename, frameSkip);
    }
  };

  const handlePauseStream = () => {
    wsClientRef.current?.pause();
    setStreamStatus('PAUSED');
  };

  const handleResumeStream = () => {
    wsClientRef.current?.resume();
    setStreamStatus('RUNNING');
  };

  const handleStopStream = () => {
    wsClientRef.current?.stop();
    setStreamStatus('STOPPED');
    setFrameImage(null);
    setTelemetry(null);
    setSelectedTrackId(null);
  };

  const handleFileUpload = async (file) => {
    try {
      handleStopStream();
      setUploadedFilename(null);
      setFrameImage(null);
      setTelemetry(null);

      const res = await uploadVideo(file);
      setUploadedFilename(res.filename);
    } catch (err) {
      console.error('File upload failed:', err);
    }
  };

  const handleSelectTrack = (trackId) => {
    setSelectedTrackId(trackId);
    wsClientRef.current?.selectTrack(trackId);
  };

  const personTracks = telemetry?.person_tracks || telemetry?.tracks || [];
  const vehicleTracks = telemetry?.vehicle_tracks || [];

  const selectedVehicleDetail =
    vehicleTracks.find((v) => v.track_id === selectedTrackId) || null;

  const selectedPersonDetail =
    personTracks.find((p) => p.track_id === selectedTrackId) || null;

  return (
    <div className="min-h-screen bg-command-bg flex flex-col font-sans">
      
      {/* Header Bar */}
      <Header
        systemStatus={systemStatus}
        mode={mode}
        onModeChange={(newMode) => {
          handleStopStream();
          setMode(newMode);
        }}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 space-y-6">
        
        {/* Live Statistics Cards */}
        <StatsPanel telemetry={telemetry} />

        {/* View Switch: Live Command vs ANPR History */}
        {activeTab === 'anpr' ? (
          <ANPRHistoryView />
        ) : (
          <>
            {/* Camera Selector (in Demo CCTV Mode) */}
            {mode === 'demo' && (
              <CameraSelector
                cameras={cameras}
                selectedCameraId={selectedCameraId}
                onSelectCamera={(id) => {
                  if (id !== selectedCameraId) {
                    handleStopStream();
                    setSelectedCameraId(id);
                  }
                }}
                disabled={streamStatus === 'RUNNING'}
              />
            )}

            {/* Main Grid: Video Player & ANPR Ticker + Side Tracking Panels */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
              
              {/* Left 2 Columns: Video Player & Recent ANPR Feed */}
              <div className="lg:col-span-2 space-y-6">
                <VideoPlayer
                  mode={mode}
                  frameImage={frameImage}
                  telemetry={telemetry}
                  streamStatus={streamStatus}
                  onStart={handleStartStream}
                  onPause={handlePauseStream}
                  onResume={handleResumeStream}
                  onStop={handleStopStream}
                  onUpload={handleFileUpload}
                  uploadedFilename={uploadedFilename}
                  frameSkip={frameSkip}
                  onFrameSkipChange={setFrameSkip}
                />

                {/* Recent ANPR Live Feed */}
                <ANPRFeedPanel
                  recentEvents={recentANPREvents}
                  onViewHistory={() => setActiveTab('anpr')}
                />
              </div>

              {/* Right 1 Column: Tracking & Telemetry Panels */}
              <div className="lg:col-span-1 space-y-4">
                
                {/* Switcher between Vehicles and Persons view */}
                <div className="flex bg-slate-900/90 p-1 rounded-xl border border-slate-800">
                  <button
                    onClick={() => setSidePanelTab('vehicles')}
                    className={`flex-1 py-1.5 rounded-lg text-xs font-mono font-bold transition-all ${
                      sidePanelTab === 'vehicles'
                        ? 'bg-cyan-600 text-white shadow glow-cyan'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    VEHICLES ({vehicleTracks.length})
                  </button>
                  <button
                    onClick={() => setSidePanelTab('persons')}
                    className={`flex-1 py-1.5 rounded-lg text-xs font-mono font-bold transition-all ${
                      sidePanelTab === 'persons'
                        ? 'bg-emerald-600 text-white shadow glow-emerald'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    PERSONS ({personTracks.length})
                  </button>
                </div>

                {/* Active Vehicles List Panel */}
                {sidePanelTab === 'vehicles' ? (
                  <VehicleListPanel
                    vehicles={vehicleTracks}
                    selectedTrackId={selectedTrackId}
                    onSelectTrack={handleSelectTrack}
                  />
                ) : (
                  <TrackListPanel
                    tracks={personTracks}
                    selectedTrackId={selectedTrackId}
                    onSelectTrack={handleSelectTrack}
                  />
                )}

                {/* Inspection Drawers */}
                {selectedVehicleDetail && (
                  <VehicleDetailModal
                    vehicle={selectedVehicleDetail}
                    onClose={() => handleSelectTrack(null)}
                  />
                )}

                {selectedPersonDetail && !selectedVehicleDetail && (
                  <TrackDetailPanel
                    track={selectedPersonDetail}
                    onClose={() => handleSelectTrack(null)}
                  />
                )}

              </div>

            </div>
          </>
        )}

      </main>

    </div>
  );
};

export default App;
