document.querySelectorAll('.nav-toggle').forEach(button => {
  const topbar = button.closest('.topbar');
  button.addEventListener('click', () => {
    const open = topbar.classList.toggle('nav-open');
    button.setAttribute('aria-expanded', String(open));
  });
  topbar.querySelectorAll('.site-nav a').forEach(link => link.addEventListener('click', () => {
    topbar.classList.remove('nav-open');
    button.setAttribute('aria-expanded', 'false');
  }));
});
