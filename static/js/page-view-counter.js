(function () {
  "use strict";

  var script = document.getElementById("goatcounter-script");
  var counter = document.getElementById("page-view-counter");
  var count = document.getElementById("page-view-count");

  if (!script || !counter || !count) return;

  function loadPageViewCount() {
    if (!window.goatcounter || typeof window.goatcounter.get_data !== "function") {
      return;
    }

    var path = window.goatcounter.get_data().p;
    var endpoint =
      "https://ssnet.goatcounter.com/counter/" +
      encodeURIComponent(path) +
      ".json?start=2026-08-19";

    window.fetch(endpoint, {
      mode: "cors",
      credentials: "omit"
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("HTTP " + response.status + " for path " + path);
        }
        return response.json();
      })
      .then(function (data) {
        if (data.count === undefined || data.count === null) {
          throw new Error("Missing count in GoatCounter response");
        }

        count.textContent = data.count;
        counter.hidden = false;
      })
      .catch(function (error) {
        console.error("[GoatCounter] Unable to load page view count", {
          path: path,
          endpoint: endpoint,
          error: error
        });
      });
  }

  if (window.goatcounter && typeof window.goatcounter.get_data === "function") {
    loadPageViewCount();
  } else {
    script.addEventListener("load", loadPageViewCount, { once: true });
  }
})();
