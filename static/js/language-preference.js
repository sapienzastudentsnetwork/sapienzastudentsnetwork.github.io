document.addEventListener('click', function (event) {
  var control = event.target.closest('[data-language-link]');
  if (!control) return;

  try {
    localStorage.setItem('preferred-language', control.dataset.languageLink);
  } catch (_) {}

  if (control.dataset.languageHref) {
    window.location.href = control.dataset.languageHref;
  }
});
