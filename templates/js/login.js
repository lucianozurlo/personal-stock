(function () {
  const themeBtn = document.getElementById('themeToggle');
  const themeStorageKey = 'personal-stock-theme';
  let themeFadeTimeout = null;

  function setTheme(light, persist = true, animate = true) {
    clearTimeout(themeFadeTimeout);
    if (animate) document.body.classList.add('theme-ready', 'theme-fading');
    document.body.classList.toggle('light', light);
    themeBtn?.setAttribute('aria-checked', String(light));
    if (persist) localStorage.setItem(themeStorageKey, light ? 'light' : 'dark');
    themeFadeTimeout = setTimeout(() => document.body.classList.remove('theme-fading'), 900);
  }

  const savedTheme = localStorage.getItem(themeStorageKey);
  setTheme(savedTheme === 'light', false, false);
  requestAnimationFrame(() => document.body.classList.add('theme-ready'));

  themeBtn?.addEventListener('click', () => setTheme(!document.body.classList.contains('light')));
})();

(function () {
  const password = document.getElementById('password');
  const toggle = document.getElementById('passwordToggle');
  const form = document.getElementById('loginForm');
  const ssoBtn = document.getElementById('ssoBtn');
  const toast = document.getElementById('toast');

  function showToast() {
    toast?.classList.add('show');
    setTimeout(() => toast?.classList.remove('show'), 2400);
  }

  function goHome() {
    showToast();
    setTimeout(() => {
      window.location.href = 'index.html';
    }, 650);
  }

  toggle?.addEventListener('click', () => {
    const isPassword = password.type === 'password';
    password.type = isPassword ? 'text' : 'password';
    toggle.setAttribute('aria-label', isPassword ? 'Ocultar contraseña' : 'Mostrar contraseña');
    toggle.innerHTML = isPassword ? '<i class="fa-regular fa-eye-slash"></i>' : '<i class="fa-regular fa-eye"></i>';
    password.focus();
  });

  form?.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }
    goHome();
  });

  ssoBtn?.addEventListener('click', goHome);
})();
