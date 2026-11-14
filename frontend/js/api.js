/**
 * Pre-Finance AI – API client
 * All backend calls go through this module.
 */

const API_BASE = 'http://localhost:8000';

// ─── Token storage ────────────────────────────────────────────────────────────
const Auth = {
  getToken: () => localStorage.getItem('pf_token'),
  setToken: (t) => localStorage.setItem('pf_token', t),
  removeToken: () => localStorage.removeItem('pf_token'),

  getUser: () => {
    try { return JSON.parse(localStorage.getItem('pf_user')); } catch { return null; }
  },
  setUser: (u) => localStorage.setItem('pf_user', JSON.stringify(u)),
  removeUser: () => localStorage.removeItem('pf_user'),

  isLoggedIn: () => !!localStorage.getItem('pf_token'),
  isAdmin: () => {
    const u = Auth.getUser();
    return u && u.role === 'admin';
  },

  save: (tokenResp) => {
    Auth.setToken(tokenResp.access_token);
    Auth.setUser(tokenResp.user);
  },

  clear: () => {
    Auth.removeToken();
    Auth.removeUser();
  },
};

// ─── Core fetch wrapper ───────────────────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const token = Auth.getToken();
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  // 401 → auto-logout
  if (res.status === 401) {
    Auth.clear();
    window.location.href = '/login.html';
    return;
  }

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const msg = data?.detail || data?.message || `Request failed (${res.status})`;
    throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
  }

  return data;
}

// Multipart upload (no Content-Type header – browser sets boundary)
async function apiUpload(path, formData) {
  const token = Auth.getToken();
  const headers = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { method: 'POST', headers, body: formData });

  if (res.status === 401) {
    Auth.clear();
    window.location.href = '/login.html';
    return;
  }

  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data?.detail || `Upload failed (${res.status})`);
  return data;
}

// ─── Auth endpoints ───────────────────────────────────────────────────────────
const AuthAPI = {
  register: (name, email, password) =>
    apiFetch('/auth/register', { method: 'POST', body: JSON.stringify({ name, email, password }) }),

  login: (email, password) =>
    apiFetch('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),

  logout: () =>
    apiFetch('/auth/logout', { method: 'POST' }),

  me: () => apiFetch('/auth/me'),

  changePassword: (current_password, new_password) =>
    apiFetch('/auth/change-password', { method: 'POST', body: JSON.stringify({ current_password, new_password }) }),
};

// ─── Document endpoints ───────────────────────────────────────────────────────
const DocsAPI = {
  list: () => apiFetch('/documents'),

  upload: (file) => {
    const fd = new FormData();
    fd.append('file', file);
    return apiUpload('/documents', fd);
  },

  delete: (id) => apiFetch(`/documents/${id}`, { method: 'DELETE' }),

  get: (id) => apiFetch(`/documents/${id}`),
};

// ─── Chat endpoints ───────────────────────────────────────────────────────────
const ChatAPI = {
  listConversations: () => apiFetch('/chat/conversations'),

  getConversation: (id) => apiFetch(`/chat/conversations/${id}`),

  rename: (id, title) =>
    apiFetch(`/chat/conversations/${id}/rename`, { method: 'PATCH', body: JSON.stringify({ title }) }),

  delete: (id) => apiFetch(`/chat/conversations/${id}`, { method: 'DELETE' }),

  ask: (question, conversation_id = null) =>
    apiFetch('/chat/ask', { method: 'POST', body: JSON.stringify({ question, conversation_id }) }),
};

// ─── Admin endpoints ──────────────────────────────────────────────────────────
const AdminAPI = {
  stats: () => apiFetch('/admin/stats'),
  users: () => apiFetch('/admin/users'),
  setUserStatus: (id, is_active) =>
    apiFetch(`/admin/users/${id}/status`, { method: 'PATCH', body: JSON.stringify({ is_active }) }),
  documents: () => apiFetch('/admin/documents'),
  logs: (limit = 100) => apiFetch(`/admin/logs?limit=${limit}`),
};

// ─── Route guard helpers ──────────────────────────────────────────────────────
function requireAuth() {
  if (!Auth.isLoggedIn()) {
    window.location.href = '/login.html';
  }
}

function requireAdmin() {
  if (!Auth.isLoggedIn()) { window.location.href = '/login.html'; return; }
  if (!Auth.isAdmin())    { window.location.href = '/pages/dashboard.html'; }
}

function redirectIfLoggedIn() {
  if (!Auth.isLoggedIn()) return;
  if (Auth.isAdmin()) {
    window.location.href = '/pages/admin/dashboard.html';
  } else {
    window.location.href = '/pages/dashboard.html';
  }
}
