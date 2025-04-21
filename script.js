// THEME TOGGLE
const themeToggle = document.getElementById('theme-toggle');
themeToggle.addEventListener('click', () => {
  const next =
    document.body.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
  document.body.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
});
// Initialize theme on load
document.body.setAttribute(
  'data-theme',
  localStorage.getItem('theme') || 'light'
);

// AOS INITIALIZATION
AOS.init({
  duration: 800,
  once: true,
});

// SET SKILL BAR LEVELS
document.querySelectorAll('.skill-bar').forEach((bar) => {
  const level = bar.getAttribute('data-level') || '0%';
  bar.style.setProperty('--level', level);
});
