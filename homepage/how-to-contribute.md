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

{{% include "content/cad/it/contributing/how-to-contribute.md" %}}

</div>

<script>
(() => {
  const buttons = document.querySelectorAll('[data-guide-button]');
  const panels = document.querySelectorAll('[data-guide-panel]');
  const apply = (value) => {
    const language = value === 'it' ? 'it' : 'en';
    document.documentElement.lang = language;
    buttons.forEach(function (button) {
      var active = button.dataset.guideButton === language;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
    panels.forEach((panel) => { panel.hidden = panel.dataset.guidePanel !== language; });
    const url = new URL(location.href);
    url.searchParams.set('lang', language);
    history.replaceState(null, '', url);
  };
  buttons.forEach((button) => button.addEventListener('click', () => apply(button.dataset.guideButton)));
  apply(new URLSearchParams(location.search).get('lang') || 'en');
})();
</script>
