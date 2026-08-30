---
title: "How to contribute · Come contribuire"
bookHidden: true
bookToC: true
---

<div class="language-switch" role="group" aria-label="Language · Lingua">
  <button type="button" data-guide-button="en" aria-pressed="true">English</button>
  <button type="button" data-guide-button="it" aria-pressed="false">Italiano</button>
</div>


<div data-guide-panel="en">

{{% include "content/cad/en/contributing/how-to-contribute.md" %}}

</div>
<div data-guide-panel="it" hidden>

{{% include-homepage-contribute-it %}}

</div>

<script>
(() => {
  const buttons = document.querySelectorAll('[data-guide-button]');
  const panels = document.querySelectorAll('[data-guide-panel]');
  const browserLanguage = () => /^it(?:-|$)/i.test((navigator.languages && navigator.languages[0]) || navigator.language || 'en') ? 'it' : 'en';
  const apply = (value, remember = false) => {
    const language = value === 'it' ? 'it' : 'en';
    document.documentElement.lang = language;
    buttons.forEach(function (button) {
      var active = button.dataset.guideButton === language;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
    panels.forEach((panel) => { panel.hidden = panel.dataset.guidePanel !== language; });
    if (remember) {
      try { localStorage.setItem('preferred-language', language); } catch (_) {}
    }
  };
  buttons.forEach((button) => button.addEventListener('click', () => apply(button.dataset.guideButton, true)));
  let savedLanguage = null;
  try { savedLanguage = localStorage.getItem('preferred-language'); } catch (_) {}
  const url = new URL(location.href);
  if (url.searchParams.delete('lang')) {
    history.replaceState(null, '', url.pathname + url.search + url.hash);
  }
  apply(savedLanguage === 'it' || savedLanguage === 'en' ? savedLanguage : browserLanguage());
})();
</script>
