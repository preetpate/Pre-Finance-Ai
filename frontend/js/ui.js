/**
 * Pre-Finance AI – UI utilities (toast, modal, theme, loader)
 */

// ─── Toast notifications ───────────────────────────────────────────────────
const Toast = (() => {
  function _ensure() {
    let c = document.getElementById('toast-container');
    if (!c) {
      c = document.createElement('div');
      c.id = 'toast-container';
      document.body.appendChild(c);
    }
    return c;
  }

  function show(message, type = 'info', duration = 4000) {
    const container = _ensure();
    const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <span class="toast-icon">${icons[type] || 'ℹ'}</span>
      <span class="toast-msg">${message}</span>
      <button class="toast-close" onclick="this.parentElement.remove()">✕</button>
    `;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(20px)';
      toast.style.transition = 'opacity 0.3s, transform 0.3s';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }

  return {
    success: (m, d) => show(m, 'success', d),
    error:   (m, d) => show(m, 'error',   d),
    warning: (m, d) => show(m, 'warning', d),
    info:    (m, d) => show(m, 'info',    d),
  };
})();

// ─── Confirmation modal ────────────────────────────────────────────────────
function confirm(title, message) {
  return new Promise((resolve) => {
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.innerHTML = `
      <div class="modal">
        <div class="modal-title">${title}</div>
        <p class="text-sm">${message}</p>
        <div class="modal-actions">
          <button class="btn btn-secondary btn-sm" id="modal-cancel">Cancel</button>
          <button class="btn btn-danger btn-sm"    id="modal-confirm">Confirm</button>
        </div>
      </div>
    `;
    document.body.appendChild(overlay);
    requestAnimationFrame(() => overlay.classList.add('active'));

    overlay.querySelector('#modal-cancel').onclick  = () => { overlay.remove(); resolve(false); };
    overlay.querySelector('#modal-confirm').onclick = () => { overlay.remove(); resolve(true); };
  });
}

// ─── Page loader ───────────────────────────────────────────────────────────
const Loader = {
  show() {
    let el = document.getElementById('page-loader');
    if (!el) {
      el = document.createElement('div');
      el.id = 'page-loader';
      el.innerHTML = `
        <div style="display:flex;flex-direction:column;align-items:center;gap:16px">
          <div class="spinner spinner-lg"></div>
          <span style="font-size:0.875rem;color:var(--text-muted)">Loading…</span>
        </div>`;
      document.body.appendChild(el);
    }
    el.classList.remove('hidden');
  },
  hide() {
    const el = document.getElementById('page-loader');
    if (el) el.classList.add('hidden');
  },
};

// ─── Dark / light theme ────────────────────────────────────────────────────
const Theme = {
  get: () => localStorage.getItem('pf_theme') || 'dark',
  apply(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('pf_theme', theme);
  },
  toggle() {
    const next = this.get() === 'dark' ? 'light' : 'dark';
    this.apply(next);
    return next;
  },
  init() { this.apply(this.get()); },
};

// ─── Sidebar mobile toggle ─────────────────────────────────────────────────
function initSidebarToggle() {
  const toggle = document.getElementById('menu-toggle');
  const sidebar = document.querySelector('.sidebar');
  if (!toggle || !sidebar) return;
  toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
  document.addEventListener('click', (e) => {
    if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && !toggle.contains(e.target)) {
      sidebar.classList.remove('open');
    }
  });
}

// ─── Auto-resize textarea ──────────────────────────────────────────────────
function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 160) + 'px';
}

// ─── Format helpers ────────────────────────────────────────────────────────
function formatDate(iso) {
  return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}
function formatDateTime(iso) {
  return new Date(iso).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}
function formatBytes(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / 1048576).toFixed(1) + ' MB';
}
function initials(name) {
  return name ? name.split(' ').slice(0,2).map(w => w[0].toUpperCase()).join('') : '?';
}

// ─── Set active nav item ───────────────────────────────────────────────────
function setActiveNav(page) {
  document.querySelectorAll('.nav-item').forEach(el => {
    el.classList.toggle('active', el.dataset.page === page);
  });
}

// ─── Render sidebar user info ──────────────────────────────────────────────
function renderSidebarUser() {
  const user = Auth.getUser();
  if (!user) return;
  const nameEl = document.getElementById('sidebar-user-name');
  const roleEl = document.getElementById('sidebar-user-role');
  const avatarEl = document.getElementById('sidebar-avatar');
  if (nameEl) nameEl.textContent = user.name;
  if (roleEl) roleEl.textContent = user.role;
  if (avatarEl) avatarEl.textContent = initials(user.name);
}

// ─── Logout handler ────────────────────────────────────────────────────────
async function handleLogout() {
  try { await AuthAPI.logout(); } catch {}
  Auth.clear();
  window.location.href = '/login.html';
}

// ─── Init on every dashboard page ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  Theme.init();
  initSidebarToggle();
  renderSidebarUser();

  const themeBtn = document.getElementById('theme-toggle');
  if (themeBtn) {
    themeBtn.addEventListener('click', () => {
      const t = Theme.toggle();
      themeBtn.title = t === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
    });
  }

  const logoutBtns = document.querySelectorAll('.logout-btn');
  logoutBtns.forEach(b => b.addEventListener('click', handleLogout));
});
