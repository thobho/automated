// "Kopiuj link" (US-3.7): copies the address in the read-only field next to the button.
// Without JavaScript the button stays hidden and the field itself is the fallback (select and copy).
// Static file, no inline script: the strict CSP stays as it is.
(function () {
  "use strict";

  function copied(status, text) {
    status.textContent = text;
  }

  function fallbackCopy(input) {
    input.focus();
    input.select();
    try {
      return document.execCommand("copy");
    } catch (e) {
      return false;
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-copy]").forEach(function (box) {
      var input = box.querySelector("[data-copy-source]");
      var button = box.querySelector("[data-copy-button]");
      var status = box.querySelector("[data-copy-status]");
      if (!input || !button || !status) {
        return;
      }
      button.hidden = false;
      button.addEventListener("click", function () {
        var done = function () {
          copied(status, "Skopiowano link.");
        };
        var failed = function () {
          if (fallbackCopy(input)) {
            done();
          } else {
            copied(status, "Nie udało się skopiować. Zaznacz adres w polu i skopiuj go ręcznie.");
          }
        };
        if (navigator.clipboard && window.isSecureContext) {
          navigator.clipboard.writeText(input.value).then(done, failed);
        } else {
          failed();
        }
      });
    });
  });
})();
