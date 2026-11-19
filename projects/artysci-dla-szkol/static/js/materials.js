// Materials step (US-2.3A): check the chosen files before sending (count, size, type by
// extension/MIME). The server checks everything again; this only saves a useless upload.
// Static file, no inline script: the strict CSP stays as it is.
(function () {
  "use strict";

  function allowed(file, accept) {
    var name = file.name.toLowerCase();
    return accept.some(function (rule) {
      if (rule.charAt(0) === ".") {
        return name.slice(-rule.length) === rule;
      }
      return file.type === rule;
    });
  }

  function show(box, lines) {
    box.textContent = "";
    lines.forEach(function (line) {
      var p = document.createElement("p");
      p.textContent = line; // never innerHTML: file names are user input
      box.appendChild(p);
    });
  }

  function check(form) {
    var input = form.querySelector('input[type="file"]');
    var files = Array.prototype.slice.call(input.files || []);
    var remaining = parseInt(form.dataset.remaining, 10);
    var maxBytes = parseInt(form.dataset.maxBytes, 10);
    var accept = form.dataset.accept.split(",").map(function (s) {
      return s.trim().toLowerCase();
    });
    var problems = [];
    if (!files.length) {
      problems.push("Wybierz plik.");
    } else if (files.length > remaining) {
      problems.push("Za dużo plików: możesz dodać jeszcze " + remaining + ".");
    }
    files.forEach(function (file) {
      if (file.size > maxBytes) {
        problems.push(file.name + ": plik jest za duży (maksymalnie " + form.dataset.maxMb + " MB).");
      } else if (!allowed(file, accept)) {
        problems.push(file.name + ": ten typ pliku nie jest dozwolony.");
      }
    });
    return problems;
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("form[data-upload-check]").forEach(function (form) {
      var box = form.querySelector("[data-upload-message]");
      form.addEventListener("submit", function (event) {
        var problems = check(form);
        if (problems.length) {
          event.preventDefault();
          show(box, problems);
          form.querySelector('input[type="file"]').setAttribute("aria-invalid", "true");
        }
      });
    });
  });
})();
