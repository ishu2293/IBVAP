import axios from 'axios';

// Dynamic host resolution so frontend works seamlessly on both FastAPI (port 8000) and Vite (port 5173 / 3000)
const isViteDev = typeof window !== 'undefined' && (window.location.port === '5173' || window.location.port === '3000');
const API_BASE = isViteDev ? 'http://localhost:8000' : (typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8000');
const WS_HOST = isViteDev ? 'localhost:8000' : (typeof window !== 'undefined' ? window.location.host : 'localhost:8000');
const WS_PROTOCOL = typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const WS_BASE = `${WS_PROTOCOL}//${WS_HOST}/ws/video`;

export const getSystemStatus = async () => {
  const response = await axios.get(`${API_BASE}/api/system/status`);
  return response.data;
};

export const getCameras = async () => {
  const response = await axios.get(`${API_BASE}/api/video/cameras`);
  return response.data.cameras;
};

export const uploadVideo = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await axios.post(`${API_BASE}/api/video/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const getANPRHistory = async ({ plate = '', vehicle_type = '', camera_id = '', limit = 100 } = {}) => {
  const params = {};
  if (plate) params.plate = plate;
  if (vehicle_type && vehicle_type !== 'ALL') params.vehicle_type = vehicle_type;
  if (camera_id && camera_id !== 'ALL') params.camera_id = camera_id;
  if (limit) params.limit = limit;

  const response = await axios.get(`${API_BASE}/api/anpr/history`, { params });
  return response.data;
};

export const getRecentANPR = async (limit = 10) => {
  const response = await axios.get(`${API_BASE}/api/anpr/recent`, { params: { limit } });
  return response.data.recent;
};

export const getVehicleHistory = async () => {
  const response = await axios.get(`${API_BASE}/api/vehicles/history`);
  return response.data.vehicles;
};

export const getVehicleDetail = async (vehicleId) => {
  const response = await axios.get(`${API_BASE}/api/vehicles/${vehicleId}`);
  return response.data;
};

// Facial Recognition & Watchlist APIs
export const getRegisteredFaces = async () => {
  const response = await axios.get(`${API_BASE}/api/faces/registry`);
  return response.data;
};

export const getNextPersonId = async () => {
  const response = await axios.get(`${API_BASE}/api/faces/next-id`);
  return response.data.next_id;
};

export const registerFace = async (formData) => {
  const response = await axios.post(`${API_BASE}/api/faces/register`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const deleteRegisteredFace = async (personId) => {
  const response = await axios.delete(`${API_BASE}/api/faces/${personId}`);
  return response.data;
};

export const getFaceEvents = async ({ event_type = '', camera_id = '', limit = 50 } = {}) => {
  const params = {};
  if (event_type && event_type !== 'ALL') params.event_type = event_type;
  if (camera_id && camera_id !== 'ALL') params.camera_id = camera_id;
  if (limit) params.limit = limit;

  const response = await axios.get(`${API_BASE}/api/faces/events`, { params });
  return response.data;
};

export const getRecentFaces = async (limit = 10) => {
  const response = await axios.get(`${API_BASE}/api/faces/recent`, { params: { limit } });
  return response.data.recent;
};

export const getFaceStats = async () => {
  const response = await axios.get(`${API_BASE}/api/faces/stats`);
  return response.data;
};

export const getPrivacyNotice = async () => {
  const response = await axios.get(`${API_BASE}/api/faces/notice`);
  return response.data.notice;
};

// Virtual Fence & Intrusion Detection APIs
export const getFences = async (cameraId = null) => {
  const params = {};
  if (cameraId && cameraId !== 'ALL') params.camera_id = cameraId;
  const response = await axios.get(`${API_BASE}/api/fences`, { params });
  return response.data;
};

export const getFence = async (fenceId) => {
  const response = await axios.get(`${API_BASE}/api/fences/${fenceId}`);
  return response.data;
};

export const createFence = async (fenceData) => {
  const response = await axios.post(`${API_BASE}/api/fences`, fenceData);
  return response.data;
};

export const updateFence = async (fenceId, fenceData) => {
  const response = await axios.put(`${API_BASE}/api/fences/${fenceId}`, fenceData);
  return response.data;
};

export const deleteFence = async (fenceId) => {
  const response = await axios.delete(`${API_BASE}/api/fences/${fenceId}`);
  return response.data;
};

export const toggleFence = async (fenceId) => {
  const response = await axios.post(`${API_BASE}/api/fences/${fenceId}/toggle`);
  return response.data;
};

export const getIntrusionHistory = async ({ camera_id = '', limit = 50 } = {}) => {
  const params = {};
  if (camera_id && camera_id !== 'ALL') params.camera_id = camera_id;
  if (limit) params.limit = limit;
  const response = await axios.get(`${API_BASE}/api/fences/intrusions`, { params });
  return response.data;
};

export const getFenceStats = async () => {
  const response = await axios.get(`${API_BASE}/api/fences/stats`);
  return response.data;
};

export class VideoWebSocketClient {
  constructor() {
    this.ws = null;
    this.onMessageCallback = null;
    this.onStatusChangeCallback = null;
  }

  connect(onMessage, onStatusChange) {
    this.onMessageCallback = onMessage;
    this.onStatusChangeCallback = onStatusChange;

    this.ws = new WebSocket(WS_BASE);

    this.ws.onopen = () => {
      console.log('[WS] Connected to IBVAP Backend at', WS_BASE);
      if (this.onStatusChangeCallback) this.onStatusChangeCallback('CONNECTED');
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (this.onMessageCallback) this.onMessageCallback(data);
      } catch (err) {
        console.error('[WS] Failed to parse message:', err);
      }
    };

    this.ws.onclose = () => {
      console.log('[WS] Connection closed');
      if (this.onStatusChangeCallback) this.onStatusChangeCallback('DISCONNECTED');
    };

    this.ws.onerror = (err) => {
      console.error('[WS] Connection error:', err);
      if (this.onStatusChangeCallback) this.onStatusChangeCallback('ERROR');
    };
  }

  startDemoStream(cameraId, frameSkip = 1) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        action: 'start',
        mode: 'demo',
        camera_id: cameraId,
        process_every_n_frames: frameSkip
      }));
    }
  }

  startUploadStream(filename, frameSkip = 1) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        action: 'start',
        mode: 'upload',
        filename: filename,
        process_every_n_frames: frameSkip
      }));
    }
  }

  pause() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action: 'pause' }));
    }
  }

  resume() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action: 'resume' }));
    }
  }

  stop() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action: 'stop' }));
    }
  }

  selectTrack(trackId) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action: 'select_track', track_id: trackId }));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
