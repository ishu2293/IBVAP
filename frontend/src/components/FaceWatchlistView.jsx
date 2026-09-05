import React, { useState, useEffect, useRef } from 'react';
import {
  UserCheck,
  Shield,
  UserPlus,
  AlertTriangle,
  Trash2,
  Upload,
  RefreshCw,
  Camera,
  CheckCircle,
  XCircle,
  FileText,
  Clock,
  ShieldAlert,
  Info,
  Video,
  VideoOff,
  RotateCcw,
  Sparkles,
  Lock
} from 'lucide-react';
import {
  getRegisteredFaces,
  registerFace,
  deleteRegisteredFace,
  getFaceEvents,
  getFaceStats,
  getNextPersonId
} from '../services/api.js';

export const FaceWatchlistView = () => {
  const [activeSubTab, setActiveSubTab] = useState('personnel'); // 'personnel', 'register', 'audit_log'
  const [personnel, setPersonnel] = useState([]);
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Form State (Only asks for Name, Role, Dept, and Photo)
  const [autoAssignedId, setAutoAssignedId] = useState('P_004');
  const [formName, setFormName] = useState('');
  const [formRole, setFormRole] = useState('Patrol Commander');
  const [formDept, setFormDept] = useState('Border Security Force (BSF)');
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  // Photo Option: 'upload' or 'camera'
  const [photoSourceMode, setPhotoMode] = useState('upload'); // 'upload' | 'camera'
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [cameraError, setCameraError] = useState('');
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const mediaStreamRef = useRef(null);

  // Filters
  const [filterType, setFilterType] = useState('ALL');
  const [filterCamera, setFilterCamera] = useState('ALL');

  const loadData = async () => {
    setLoading(true);
    try {
      const [regRes, evtRes, statsRes, nextIdRes] = await Promise.all([
        getRegisteredFaces(),
        getFaceEvents({ event_type: filterType, camera_id: filterCamera, limit: 50 }),
        getFaceStats(),
        getNextPersonId().catch(() => 'P_004')
      ]);
      setPersonnel(regRes.personnel || []);
      setEvents(evtRes.events || []);
      setStats(statsRes);
      if (nextIdRes) setAutoAssignedId(nextIdRes);
    } catch (err) {
      console.error('Failed to load face data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [filterType, filterCamera]);

  // Handle webcam stream start/stop
  const startCamera = async () => {
    setCameraError('');
    setIsCameraActive(false);

    if (!navigator?.mediaDevices?.getUserMedia) {
      setCameraError('Webcam access not supported by browser environment.');
      return;
    }

    try {
      // Release any lingering stream
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((t) => t.stop());
        mediaStreamRef.current = null;
      }

      let stream = null;
      // Progressive constraint fallback to maximize hardware compatibility
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 640 },
            height: { ideal: 480 },
            facingMode: 'user'
          },
          audio: false
        });
      } catch (e1) {
        try {
          stream = await navigator.mediaDevices.getUserMedia({
            video: { width: { ideal: 640 }, height: { ideal: 480 } },
            audio: false
          });
        } catch (e2) {
          stream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false
          });
        }
      }

      mediaStreamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          if (videoRef.current) {
            videoRef.current.play()
              .then(() => setIsCameraActive(true))
              .catch(() => setIsCameraActive(true));
          }
        };
        // Also trigger directly in case metadata was already cached
        videoRef.current.play()
          .then(() => setIsCameraActive(true))
          .catch(() => {});
      } else {
        setIsCameraActive(true);
      }
    } catch (err) {
      console.error('Camera initialization error:', err);
      let msg = 'Could not access camera. Please check device permissions.';
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        msg = 'Camera access denied. Please allow camera permissions in your browser.';
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        msg = 'No camera device detected on this system.';
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        msg = 'Camera is already in use by another application or process.';
      }
      setCameraError(msg);
      setIsCameraActive(false);
    }
  };

  const stopCamera = () => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
  };

  // Switch photo modes
  const handleSelectPhotoMode = (mode) => {
    setPhotoMode(mode);
    setCameraError('');
    if (mode === 'camera') {
      setSelectedFile(null);
      setPreviewUrl(null);
    } else {
      stopCamera();
    }
  };

  // Dedicated lifecycle manager for camera
  useEffect(() => {
    if (activeSubTab === 'register' && photoSourceMode === 'camera' && !previewUrl) {
      startCamera();
    } else {
      stopCamera();
    }

    return () => {
      stopCamera();
    };
  }, [activeSubTab, photoSourceMode, previewUrl]);

  // Capture live snapshot from webcam
  const handleCaptureSnapshot = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const vw = video.videoWidth || 640;
    const vh = video.videoHeight || 480;
    canvas.width = vw;
    canvas.height = vh;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, vw, vh);

    canvas.toBlob((blob) => {
      if (blob) {
        const capturedFile = new File([blob], `capture_${autoAssignedId || 'person'}.jpg`, { type: 'image/jpeg' });
        setSelectedFile(capturedFile);
        setPreviewUrl(URL.createObjectURL(blob));
        setErrorMsg('');
      }
    }, 'image/jpeg', 0.95);
  };

  // Retake photo (re-engages webcam automatically via useEffect when previewUrl becomes null)
  const handleRetake = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setCameraError('');
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setErrorMsg('');
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');

    if (!formName.trim()) {
      setErrorMsg('Full Name is required.');
      return;
    }
    if (!selectedFile) {
      setErrorMsg('Please upload a photo or capture a live webcam photo.');
      return;
    }

    setSubmitting(true);
    try {
      const fd = new FormData();
      fd.append('person_id', autoAssignedId);
      fd.append('name', formName.trim());
      fd.append('role', formRole.trim());
      fd.append('department', formDept.trim());
      fd.append('file', selectedFile);

      const res = await registerFace(fd);
      setSuccessMsg(`Successfully registered ${res.personnel.name} (${res.personnel.person_id})`);
      setFormName('');
      setSelectedFile(null);
      setPreviewUrl(null);
      stopCamera();
      loadData();
      setTimeout(() => setActiveSubTab('personnel'), 1300);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Registration failed.';
      setErrorMsg(detail);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (personId, name) => {
    if (!window.confirm(`Are you sure you want to remove '${name}' (${personId}) from the watchlist?`)) {
      return;
    }
    try {
      await deleteRegisteredFace(personId);
      loadData();
    } catch (err) {
      console.error('Delete failed:', err);
      alert('Failed to delete personnel record.');
    }
  };

  return (
    <div className="space-y-6">

      {/* Biometric Privacy & Safeguard Notice Banner */}
      <div className="bg-slate-900/95 border-l-4 border-cyan-500 rounded-xl p-4 shadow-lg border border-slate-800 flex items-start gap-3.5">
        <div className="p-2 bg-cyan-500/10 border border-cyan-500/30 rounded-lg text-cyan-400 shrink-0">
          <Shield className="w-5 h-5" />
        </div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-400 font-mono">
              Biometric Data & Privacy Safeguard Notice
            </h4>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-mono">
              Authorized Monitoring Only
            </span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed font-sans">
            Facial recognition is intended for authorized security monitoring. Facial images and biometric information are processed only for the intended surveillance purpose and should be handled according to applicable organizational policies, privacy requirements, and data-retention rules. Stored biometric embeddings are restricted to local secure storage.
          </p>
        </div>
      </div>

      {/* Top Metrics Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        
        <div className="bg-command-card border border-command-border rounded-xl p-4 shadow-lg">
          <div className="flex items-center gap-2 text-slate-400 font-mono text-xs mb-1">
            <UserCheck className="w-4 h-4 text-emerald-400" />
            <span>Watchlist Personnel</span>
          </div>
          <div className="text-2xl font-black font-mono text-emerald-400">
            {stats?.total_registered_personnel ?? personnel.length}
          </div>
          <span className="text-[11px] text-slate-500 font-mono">Authorized & Enrolled</span>
        </div>

        <div className="bg-command-card border border-command-border rounded-xl p-4 shadow-lg">
          <div className="flex items-center gap-2 text-slate-400 font-mono text-xs mb-1">
            <CheckCircle className="w-4 h-4 text-cyan-400" />
            <span>Verified Detections</span>
          </div>
          <div className="text-2xl font-black font-mono text-cyan-400">
            {stats?.recognized_events ?? 0}
          </div>
          <span className="text-[11px] text-slate-500 font-mono">Recognized Staff Hits</span>
        </div>

        <div className="bg-command-card border border-command-border rounded-xl p-4 shadow-lg">
          <div className="flex items-center gap-2 text-slate-400 font-mono text-xs mb-1">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>Unknown Alerts</span>
          </div>
          <div className="text-2xl font-black font-mono text-amber-400">
            {stats?.unknown_alerts ?? 0}
          </div>
          <span className="text-[11px] text-slate-500 font-mono">Unregistered Individuals</span>
        </div>

        <div className="bg-command-card border border-command-border rounded-xl p-4 shadow-lg">
          <div className="flex items-center gap-2 text-slate-400 font-mono text-xs mb-1">
            <Clock className="w-4 h-4 text-purple-400" />
            <span>Total Events</span>
          </div>
          <div className="text-2xl font-black font-mono text-purple-400">
            {stats?.total_face_events ?? events.length}
          </div>
          <span className="text-[11px] text-slate-500 font-mono">Audit Entries Logged</span>
        </div>

      </div>

      {/* Sub-Navigation Switcher */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 border-b border-command-border pb-3">
        
        <div className="flex bg-slate-900/90 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveSubTab('personnel')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeSubTab === 'personnel'
                ? 'bg-cyan-600 text-white shadow glow-cyan'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <UserCheck className="w-3.5 h-3.5" />
            Authorized Personnel ({personnel.length})
          </button>
          
          <button
            onClick={() => {
              setActiveSubTab('register');
              getNextPersonId().then((id) => id && setAutoAssignedId(id)).catch(() => {});
            }}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeSubTab === 'register'
                ? 'bg-emerald-600 text-white shadow glow-emerald'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <UserPlus className="w-3.5 h-3.5" />
            Register Personnel
          </button>

          <button
            onClick={() => setActiveSubTab('audit_log')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeSubTab === 'audit_log'
                ? 'bg-amber-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            Recognition Events ({events.length})
          </button>
        </div>

        <button
          onClick={loadData}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300 hover:text-white hover:border-slate-700 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          Refresh
        </button>

      </div>

      {/* Tab 1: Authorized Personnel Registry */}
      {activeSubTab === 'personnel' && (
        <div className="space-y-4">
          {personnel.length === 0 ? (
            <div className="bg-command-card border border-command-border rounded-xl p-12 text-center space-y-3">
              <ShieldAlert className="w-12 h-12 text-slate-600 mx-auto" />
              <h3 className="text-sm font-bold text-slate-300 font-mono">No Personnel Registered Yet</h3>
              <p className="text-xs text-slate-500 max-w-md mx-auto">
                Register authorized border guards, officers, or staff members using the Register Personnel form.
              </p>
              <button
                onClick={() => setActiveSubTab('register')}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-600 text-white text-xs font-bold shadow hover:bg-cyan-500 transition-colors font-mono"
              >
                <UserPlus className="w-4 h-4" />
                Register First Person
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {personnel.map((person) => (
                <div
                  key={person.person_id}
                  className="bg-command-card border border-command-border hover:border-slate-700 rounded-xl p-4 shadow-lg transition-all flex flex-col justify-between space-y-4"
                >
                  <div className="flex items-start gap-3.5">
                    {/* Avatar */}
                    <div className="w-16 h-16 rounded-xl bg-slate-900 border border-slate-800 overflow-hidden shrink-0 flex items-center justify-center relative shadow-inner">
                      {person.avatar_url ? (
                        <img
                          src={`http://localhost:8000${person.avatar_url}`}
                          alt={person.name}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            e.target.onerror = null;
                            e.target.src = '';
                          }}
                        />
                      ) : (
                        <UserCheck className="w-8 h-8 text-slate-600" />
                      )}
                      <div className="absolute bottom-0 right-0 p-0.5 bg-emerald-500 rounded-tl">
                        <CheckCircle className="w-3 h-3 text-slate-950" />
                      </div>
                    </div>

                    {/* Metadata */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5">
                        <h4 className="text-sm font-bold text-slate-100 truncate">
                          {person.name}
                        </h4>
                      </div>
                      <span className="inline-block mt-0.5 px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-cyan-950 text-cyan-400 border border-cyan-800">
                        {person.person_id}
                      </span>
                      <p className="text-xs text-slate-400 mt-1 truncate">
                        {person.role || 'Security Personnel'}
                      </p>
                      <p className="text-[11px] text-slate-500 truncate font-mono">
                        {person.department || 'Border Command'}
                      </p>
                    </div>
                  </div>

                  {/* Footer Stats & Delete */}
                  <div className="pt-3 border-t border-command-border/60 flex items-center justify-between text-[11px] font-mono text-slate-500">
                    <span>Enrolled: {person.registered_at?.split(' ')[0] || 'Active'}</span>
                    <button
                      onClick={() => handleDelete(person.person_id, person.name)}
                      className="p-1.5 rounded-lg hover:bg-red-500/20 text-slate-500 hover:text-red-400 transition-colors"
                      title="Delete Record"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Register Personnel Form (Auto-ID, Name, Role, Dept, Upload + Live Camera) */}
      {activeSubTab === 'register' && (
        <div className="max-w-2xl mx-auto bg-command-card border border-command-border rounded-2xl p-6 shadow-xl space-y-6">
          <div className="border-b border-command-border pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h3 className="text-base font-bold text-slate-100 font-mono flex items-center gap-2">
                <UserPlus className="w-5 h-5 text-emerald-400" />
                Enroll Authorized Personnel
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Personnel ID is auto-assigned. Upload a photo or take a live camera snapshot.
              </p>
            </div>

            {/* Auto-Assigned ID Badge */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-cyan-950/70 border border-cyan-800 text-cyan-300 shrink-0 self-start sm:self-center">
              <Lock className="w-3.5 h-3.5 text-cyan-400" />
              <div className="text-xs font-mono">
                <span className="text-slate-400">Assigned ID: </span>
                <strong className="text-white font-bold">{autoAssignedId}</strong>
                <span className="text-[10px] text-cyan-400 ml-1">(Auto)</span>
              </div>
            </div>
          </div>

          {errorMsg && (
            <div className="p-3 bg-red-950/60 border border-red-800/80 rounded-xl text-xs text-red-300 flex items-center gap-2">
              <XCircle className="w-4 h-4 text-red-400 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {successMsg && (
            <div className="p-3 bg-emerald-950/60 border border-emerald-800/80 rounded-xl text-xs text-emerald-300 flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          <form onSubmit={handleRegisterSubmit} className="space-y-5">
            
            {/* Full Name */}
            <div>
              <label className="block text-xs font-mono text-slate-300 mb-1 font-semibold">
                Full Name *
              </label>
              <input
                type="text"
                required
                placeholder="e.g. Major Sandeep Unnikrishnan"
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50 transition-all"
              />
            </div>

            {/* Role & Department */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-mono text-slate-300 mb-1 font-semibold">
                  Role / Designation
                </label>
                <input
                  type="text"
                  placeholder="e.g. Patrol Commander"
                  value={formRole}
                  onChange={(e) => setFormRole(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50 transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-mono text-slate-300 mb-1 font-semibold">
                  Department / Battalion
                </label>
                <input
                  type="text"
                  placeholder="e.g. Border Security Force (BSF)"
                  value={formDept}
                  onChange={(e) => setFormDept(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50 transition-all"
                />
              </div>
            </div>

            {/* Photo Capture / Upload Section */}
            <div className="space-y-3 pt-2">
              
              <div className="flex items-center justify-between">
                <label className="text-xs font-mono text-slate-300 font-semibold flex items-center gap-1.5">
                  <Camera className="w-4 h-4 text-cyan-400" />
                  Facial Photo (Choose Option) *
                </label>

                {/* Photo Option Switcher */}
                <div className="flex bg-slate-900 p-1 rounded-xl border border-slate-800">
                  <button
                    type="button"
                    onClick={() => handleSelectPhotoMode('upload')}
                    className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-mono transition-all ${
                      photoSourceMode === 'upload'
                        ? 'bg-cyan-600 text-white shadow'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <Upload className="w-3.5 h-3.5" />
                    Upload Photo
                  </button>
                  <button
                    type="button"
                    onClick={() => handleSelectPhotoMode('camera')}
                    className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-mono transition-all ${
                      photoSourceMode === 'camera'
                        ? 'bg-emerald-600 text-white shadow'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <Video className="w-3.5 h-3.5" />
                    Live Camera
                  </button>
                </div>
              </div>

              {/* OPTION 1: File Upload */}
              {photoSourceMode === 'upload' && (
                <div className="border-2 border-dashed border-slate-800 hover:border-slate-700 rounded-xl p-5 text-center cursor-pointer transition-colors bg-slate-900/50">
                  <input
                    type="file"
                    id="face-photo-input"
                    accept="image/jpeg,image/png,image/webp"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                  <label htmlFor="face-photo-input" className="cursor-pointer flex flex-col items-center gap-2.5">
                    {previewUrl ? (
                      <div className="relative w-32 h-32 rounded-xl overflow-hidden border-2 border-cyan-500 shadow-xl group">
                        <img src={previewUrl} alt="Preview" className="w-full h-full object-cover" />
                        <div className="absolute inset-0 bg-slate-950/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-xs text-white font-mono gap-1">
                          <RotateCcw className="w-3.5 h-3.5" />
                          Change Photo
                        </div>
                      </div>
                    ) : (
                      <>
                        <div className="p-3.5 bg-slate-800/80 rounded-full text-cyan-400">
                          <Upload className="w-6 h-6" />
                        </div>
                        <span className="text-xs text-slate-200 font-semibold">Click to browse or drop photo</span>
                        <span className="text-[11px] text-slate-500 font-mono">Accepts JPG, PNG, or WebP</span>
                      </>
                    )}
                  </label>
                </div>
              )}

              {/* OPTION 2: Live Webcam Capture */}
              {photoSourceMode === 'camera' && (
                <div className="border border-slate-800 rounded-xl p-4 bg-slate-900/80 space-y-3">
                  
                  {cameraError && (
                    <div className="p-3 bg-red-950/50 border border-red-800 rounded-lg text-xs text-red-300 flex items-center gap-2">
                      <VideoOff className="w-4 h-4 text-red-400 shrink-0" />
                      <span>{cameraError}</span>
                      <button
                        type="button"
                        onClick={startCamera}
                        className="ml-auto underline font-bold"
                      >
                        Retry
                      </button>
                    </div>
                  )}

                  {/* Viewfinder or Captured Snapshot */}
                  <div className="relative w-full max-w-sm mx-auto aspect-4/3 rounded-xl overflow-hidden bg-slate-950 border-2 border-slate-800 flex items-center justify-center shadow-inner">
                    
                    {previewUrl ? (
                      // Captured Preview
                      <div className="relative w-full h-full">
                        <img src={previewUrl} alt="Captured Snapshot" className="w-full h-full object-cover" />
                        <div className="absolute top-2 right-2 px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-mono text-[10px] font-bold flex items-center gap-1">
                          <CheckCircle className="w-3 h-3 text-emerald-400" />
                          Captured
                        </div>
                      </div>
                    ) : (
                      // Live Video Stream
                      <>
                        <video
                          ref={videoRef}
                          autoPlay
                          playsInline
                          muted
                          className="w-full h-full object-cover"
                        />

                        {/* Tactical HUD Reticle Guide */}
                        <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
                          <div className="w-44 h-56 border border-cyan-400/50 rounded-3xl relative">
                            {/* Corner ticks */}
                            <div className="absolute -top-1 -left-1 w-3 h-3 border-t-2 border-l-2 border-cyan-400" />
                            <div className="absolute -top-1 -right-1 w-3 h-3 border-t-2 border-r-2 border-cyan-400" />
                            <div className="absolute -bottom-1 -left-1 w-3 h-3 border-b-2 border-l-2 border-cyan-400" />
                            <div className="absolute -bottom-1 -right-1 w-3 h-3 border-b-2 border-r-2 border-cyan-400" />
                            <div className="text-[10px] font-mono text-cyan-300 absolute -top-5 left-1/2 -translate-x-1/2 whitespace-nowrap bg-slate-950/80 px-2 rounded">
                              ALIGN FACE HERE
                            </div>
                          </div>
                        </div>

                        {!isCameraActive && !cameraError && (
                          <div className="absolute inset-0 bg-slate-950/80 flex flex-col items-center justify-center text-xs text-slate-400 gap-2">
                            <RefreshCw className="w-6 h-6 animate-spin text-cyan-400" />
                            <span>Starting camera...</span>
                          </div>
                        )}
                      </>
                    )}

                    {/* Hidden Canvas for snapshot extraction */}
                    <canvas ref={canvasRef} className="hidden" />
                  </div>

                  {/* Camera Controls */}
                  <div className="flex items-center justify-center gap-3 pt-1">
                    {previewUrl ? (
                      <button
                        type="button"
                        onClick={handleRetake}
                        className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono font-bold flex items-center gap-1.5 transition-colors"
                      >
                        <RotateCcw className="w-3.5 h-3.5 text-cyan-400" />
                        Retake Photo
                      </button>
                    ) : (
                      <button
                        type="button"
                        onClick={handleCaptureSnapshot}
                        disabled={!isCameraActive}
                        className="px-5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-xs font-mono font-bold flex items-center gap-2 shadow-lg glow-cyan transition-all"
                      >
                        <Camera className="w-4 h-4" />
                        Capture Snapshot
                      </button>
                    )}
                  </div>

                </div>
              )}

            </div>

            {/* Authorization disclaimer */}
            <div className="p-3 bg-slate-900/80 rounded-xl border border-slate-800 text-[11px] text-slate-400 flex items-start gap-2">
              <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
              <span>
                By enrolling this individual, you confirm they are authorized border patrol or security personnel. Biometric embeddings are retained only for real-time video surveillance verification.
              </span>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-bold shadow-lg glow-emerald transition-all flex items-center justify-center gap-2 font-mono uppercase tracking-wider"
            >
              {submitting ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Extracting Biometrics & Enrolling...
                </>
              ) : (
                <>
                  <UserPlus className="w-4 h-4" />
                  Confirm & Register into Watchlist
                </>
              )}
            </button>

          </form>
        </div>
      )}

      {/* Tab 3: Recognition Events Audit Log */}
      {activeSubTab === 'audit_log' && (
        <div className="bg-command-card border border-command-border rounded-xl shadow-lg overflow-hidden space-y-4 p-4">
          
          {/* Filters Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-command-border">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-amber-400" />
              <h3 className="text-xs font-bold font-mono text-slate-200 uppercase tracking-wider">
                Facial Recognition Audit Feed
              </h3>
            </div>

            <div className="flex items-center gap-2">
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-xs font-mono text-slate-300 focus:outline-none focus:border-cyan-500"
              >
                <option value="ALL">All Event Types</option>
                <option value="FACE_RECOGNIZED">Verified Staff</option>
                <option value="UNKNOWN_FACE">Unknown Intruder Alerts</option>
              </select>
            </div>
          </div>

          {events.length === 0 ? (
            <div className="py-12 text-center text-slate-500 font-mono text-xs">
              No face recognition events logged yet. Start a video stream to monitor personnel in real time.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-mono text-[11px] uppercase bg-slate-900/60">
                    <th className="py-2.5 px-3">Face</th>
                    <th className="py-2.5 px-3">Timestamp</th>
                    <th className="py-2.5 px-3">Event Type</th>
                    <th className="py-2.5 px-3">Identity / Person</th>
                    <th className="py-2.5 px-3">Track ID</th>
                    <th className="py-2.5 px-3">Camera</th>
                    <th className="py-2.5 px-3">Match Score</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
                  {events.map((evt) => {
                    const isRecognized = evt.event_type === 'FACE_RECOGNIZED';
                    return (
                      <tr key={evt.id} className="hover:bg-slate-900/40 transition-colors">
                        <td className="py-2 px-3">
                          <div className="w-9 h-9 rounded-lg bg-slate-900 border border-slate-800 overflow-hidden flex items-center justify-center">
                            {evt.face_crop_url ? (
                              <img
                                src={`http://localhost:8000${evt.face_crop_url}`}
                                alt="Face"
                                className="w-full h-full object-cover"
                                onError={(e) => {
                                  e.target.onerror = null;
                                  e.target.src = '';
                                }}
                              />
                            ) : (
                              <Camera className="w-4 h-4 text-slate-600" />
                            )}
                          </div>
                        </td>
                        <td className="py-2 px-3 text-slate-400 font-bold">{evt.timestamp}</td>
                        <td className="py-2 px-3">
                          <span
                            className={`px-2 py-0.5 rounded-full font-bold text-[10px] ${
                              isRecognized
                                ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                                : 'bg-amber-950 text-amber-400 border border-amber-800'
                            }`}
                          >
                            {isRecognized ? 'VERIFIED STAFF' : 'UNKNOWN FACE'}
                          </span>
                        </td>
                        <td className="py-2 px-3">
                          <span className="font-sans font-bold text-slate-200">
                            {evt.person}
                          </span>
                          {evt.person_id && (
                            <span className="text-[10px] text-cyan-400 block font-mono">
                              ID: {evt.person_id}
                            </span>
                          )}
                        </td>
                        <td className="py-2 px-3 text-slate-300">{evt.track_id}</td>
                        <td className="py-2 px-3 text-slate-400">{evt.camera_id}</td>
                        <td className="py-2 px-3">
                          <span
                            className={`font-bold ${
                              isRecognized ? 'text-emerald-400' : 'text-amber-400'
                            }`}
                          >
                            {Math.round((evt.confidence || 0) * 100)}%
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}

        </div>
      )}

    </div>
  );
};

export default FaceWatchlistView;
