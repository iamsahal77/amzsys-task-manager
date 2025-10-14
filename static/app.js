(function () {
  // ================================
  // Theme toggle with persistence
  // ================================
  const toggleBtn = document.getElementById('themeToggle');
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const stored = localStorage.getItem('theme') || (prefersDark ? 'dark' : 'light');
  applyTheme(stored);

  if (toggleBtn) {
    toggleBtn.addEventListener('click', function () {
      const current = document.documentElement.dataset.theme || 'light';
      const next = current === 'light' ? 'dark' : 'light';
      applyTheme(next);
      localStorage.setItem('theme', next);
    });
  }

  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    document.body.classList.toggle('bg-light', theme === 'light');
    document.body.classList.toggle('bg-dark', theme === 'dark');
    document.body.classList.toggle('text-light', theme === 'dark');
  }

  // ================================
  // Subtle list fade-in effect
  // ================================
  document.querySelectorAll('.list-group-item').forEach((el, idx) => {
    el.style.opacity = 0;
    setTimeout(() => {
      el.style.transition = 'opacity 240ms ease';
      el.style.opacity = 1;
    }, 40 * idx);
  });

  // ================================
  // Flash toasts (Bootstrap with fallback)
  // ================================
  const toastEls = document.querySelectorAll('.toast');
  if (toastEls.length) {
    if (window.bootstrap && bootstrap.Toast) {
      toastEls.forEach((el) => new bootstrap.Toast(el).show());
    } else {
      toastEls.forEach((el) => {
        el.classList.add('show');
        el.style.opacity = 1;
      });
    }
  }

  // ================================
  // Confirmation modal for destructive actions
  // ================================
  const confirmModalEl = document.getElementById('confirmModal');
  const confirmBodyEl = document.getElementById('confirmModalBody');
  const confirmOkBtn = document.getElementById('confirmModalOk');
  let pendingForm = null;

  if (confirmModalEl && window.bootstrap && bootstrap.Modal) {
    const confirmModal = new bootstrap.Modal(confirmModalEl);

    document.querySelectorAll('form.js-confirm').forEach((form) => {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        pendingForm = form;
        const message = form.dataset.confirmMessage || 'Are you sure?';
        const okClass = form.dataset.confirmOkayClass || 'btn-primary';
        const okText = form.dataset.confirmOkayText || 'OK';
        confirmBodyEl.textContent = message;
        confirmOkBtn.className = 'btn ' + okClass;
        confirmOkBtn.textContent = okText;
        confirmModal.show();
      });
    });

    confirmOkBtn && confirmOkBtn.addEventListener('click', () => {
      if (pendingForm) {
        confirmModal.hide();
        setTimeout(() => pendingForm.submit(), 50);
        pendingForm = null;
      }
    });
  }

  // ================================
  // Tooltips for helpful hints
  // ================================
  if (window.bootstrap && bootstrap.Tooltip) {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((el) => new bootstrap.Tooltip(el));
  }

  // ================================
  // Button ripple micro-interaction
  // ================================
  document.querySelectorAll('.btn').forEach((btn) => {
    btn.addEventListener('click', function (e) {
      const circle = document.createElement('span');
      const diameter = Math.max(btn.clientWidth, btn.clientHeight);
      const radius = diameter / 2;
      circle.style.width = circle.style.height = `${diameter}px`;
      circle.style.position = 'absolute';
      circle.style.borderRadius = '50%';
      circle.style.transform = 'translate(-50%, -50%)';
      circle.style.left = `${e.clientX - btn.getBoundingClientRect().left}px`;
      circle.style.top = `${e.clientY - btn.getBoundingClientRect().top}px`;
      circle.style.background = 'rgba(255,255,255,0.4)';
      circle.style.pointerEvents = 'none';
      circle.style.animation = 'ripple 600ms ease-out';
      btn.style.position = 'relative';
      btn.style.overflow = 'hidden';
      btn.appendChild(circle);
      setTimeout(() => circle.remove(), 650);
    });
  });

  // Inject ripple keyframes once
  if (!document.getElementById('ripple-style')) {
    const style = document.createElement('style');
    style.id = 'ripple-style';
    style.textContent = `@keyframes ripple { from { opacity: 0.6; transform: translate(-50%, -50%) scale(0); } to { opacity: 0; transform: translate(-50%, -50%) scale(2); } }`;
    document.head.appendChild(style);
  }
})();
