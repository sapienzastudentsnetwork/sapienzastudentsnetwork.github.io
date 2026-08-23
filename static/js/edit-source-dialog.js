(function () {
  "use strict";

  var dialog = document.getElementById("edit-source-dialog");
  var trigger = document.querySelector("[data-edit-source-trigger]");
  var closeButton = dialog && dialog.querySelector("[data-edit-source-close]");

  if (!dialog || !trigger || !closeButton) return;

  trigger.addEventListener("click", function (event) {
    if (typeof dialog.showModal !== "function") return;

    event.preventDefault();
    dialog.showModal();
  });

  closeButton.addEventListener("click", function () {
    dialog.close();
  });

  dialog.addEventListener("click", function (event) {
    if (event.target === dialog) dialog.close();
  });
})();
