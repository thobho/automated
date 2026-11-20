// Materials step (US-2.3A/B): check the chosen files before sending (count, size, type by
// extension/MIME, a video's duration). The server checks everything again; this only saves a
// useless upload. Video and audio go in resumable chunks (see below).
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

  // --- video and audio: resumable upload in chunks (US-2.3B) ----------------------------------
  // Protocol (apps/artists/resumable.py): POST the form URL (kind, size, name) -> session with
  // `url`, `complete_url`, `offset`, `chunk_size`; POST each chunk to `url` with the header
  // Upload-Offset; GET `url` answers the received offset; POST `complete_url` at the end.
  // The session URL is kept in localStorage per file, so choosing the same file again after a
  // lost connection or a page reload continues where it stopped.

  var RETRIES = 5;

  function storageKey(form, file) {
    return ["upload", form.dataset.kind, file.name, file.size, file.lastModified].join(":");
  }

  function remember(key, value) {
    try {
      if (value) {
        window.localStorage.setItem(key, JSON.stringify(value));
      } else {
        window.localStorage.removeItem(key);
      }
    } catch (e) {
      // storage disabled: the upload still works, it just cannot resume after a reload
    }
  }

  function recall(key) {
    try {
      return JSON.parse(window.localStorage.getItem(key) || "null");
    } catch (e) {
      return null;
    }
  }

  function pendingNames(kind) {
    var names = [];
    try {
      for (var i = 0; i < window.localStorage.length; i++) {
        var key = window.localStorage.key(i);
        var parts = key.split(":");
        if (parts[0] === "upload" && parts[1] === kind) {
          names.push(parts.slice(2, -2).join(":"));
        }
      }
    } catch (e) {
      // ignore
    }
    return names;
  }

  function csrf(form) {
    return form.querySelector('input[name="csrfmiddlewaretoken"]').value;
  }

  function wait(ms) {
    return new Promise(function (resolve) {
      window.setTimeout(resolve, ms);
    });
  }

  function answer(response) {
    return response
      .json()
      .catch(function () {
        return {};
      })
      .then(function (data) {
        data.httpStatus = response.status;
        data.ok = response.ok;
        return data;
      });
  }

  function videoDuration(file) {
    // Seconds read from the file's metadata in the browser, or null when it cannot be read.
    return new Promise(function (resolve) {
      var video = document.createElement("video");
      var url = URL.createObjectURL(file);
      var done = function (value) {
        URL.revokeObjectURL(url);
        resolve(value);
      };
      var timer = window.setTimeout(function () {
        done(null);
      }, 10000);
      video.preload = "metadata";
      video.addEventListener("loadedmetadata", function () {
        window.clearTimeout(timer);
        done(isFinite(video.duration) ? video.duration : null);
      });
      video.addEventListener("error", function () {
        window.clearTimeout(timer);
        done(null);
      });
      video.src = url;
    });
  }

  function checkMedia(form, file) {
    var accept = form.dataset.accept.split(",").map(function (s) {
      return s.trim().toLowerCase();
    });
    var problems = [];
    if (!file) {
      return Promise.resolve(["Wybierz plik."]);
    }
    if (parseInt(form.dataset.remaining, 10) < 1) {
      problems.push("Osiągnięto limit. Usuń któryś plik, aby dodać nowy.");
    } else if (file.size > parseInt(form.dataset.maxBytes, 10)) {
      problems.push(file.name + ": plik jest za duży (maksymalnie " + form.dataset.maxMb + " MB).");
    } else if (!file.size) {
      problems.push(file.name + ": plik jest pusty.");
    } else if (!allowed(file, accept)) {
      problems.push(file.name + ": ten typ pliku nie jest dozwolony.");
    }
    var maxSeconds = parseInt(form.dataset.maxSeconds, 10);
    if (problems.length || !maxSeconds) {
      return Promise.resolve(problems);
    }
    return videoDuration(file).then(function (seconds) {
      if (seconds !== null && seconds > maxSeconds) {
        problems.push(
          file.name + ": film trwa dłużej niż " + form.dataset.maxMinutes + " minut. Skróć go przed wysłaniem."
        );
      }
      return problems;
    });
  }

  function Uploader(form, file) {
    this.form = form;
    this.file = file;
    this.key = storageKey(form, file);
    this.box = form.querySelector("[data-upload-message]");
    this.bar = form.querySelector("[data-upload-progress]");
    this.status = form.querySelector("[data-upload-status]");
  }

  Uploader.prototype.progress = function (offset) {
    var percent = Math.floor((offset * 100) / this.file.size);
    this.bar.hidden = false;
    this.bar.value = percent;
    this.status.textContent = "Wysłano " + percent + "%";
  };

  Uploader.prototype.request = function (url, options) {
    options.credentials = "same-origin";
    options.headers = options.headers || {};
    options.headers["X-CSRFToken"] = csrf(this.form);
    return fetch(url, options).then(answer);
  };

  Uploader.prototype.open = function () {
    var self = this;
    var saved = recall(this.key);
    var fresh = function () {
      var data = new FormData();
      data.append("kind", self.form.dataset.kind);
      data.append("size", String(self.file.size));
      data.append("name", self.file.name);
      return self.request(self.form.action, { method: "POST", body: data }).then(function (session) {
        if (!session.ok) {
          throw new Error(session.error || "Nie udało się rozpocząć wysyłki.");
        }
        remember(self.key, { url: session.url, complete_url: session.complete_url });
        return session;
      });
    };
    if (!saved) {
      return fresh();
    }
    return this.request(saved.url, { method: "GET" }).then(function (session) {
      if (!session.ok) {
        remember(self.key, null); // expired or gone: start over
        return fresh();
      }
      self.status.textContent = "Wznawiam przerwaną wysyłkę…";
      return session;
    });
  };

  Uploader.prototype.send = function (session) {
    var self = this;
    var offset = session.offset;
    var failures = 0;
    var step = function () {
      self.progress(offset);
      if (offset >= self.file.size) {
        return Promise.resolve();
      }
      var chunk = self.file.slice(offset, Math.min(offset + session.chunk_size, self.file.size));
      return self
        .request(session.url, {
          method: "POST",
          headers: { "Upload-Offset": String(offset), "Content-Type": "application/octet-stream" },
          body: chunk,
        })
        .then(
          function (reply) {
            if (reply.ok || (reply.httpStatus === 409 && typeof reply.offset === "number")) {
              offset = reply.offset; // accepted, or the server already has more: continue there
              failures = 0;
              return step();
            }
            if (reply.httpStatus === 404) {
              remember(self.key, null);
            }
            if (reply.httpStatus >= 500 && failures < RETRIES) {
              failures += 1;
              return wait(1000 * failures).then(step);
            }
            if (reply.httpStatus !== 413 && reply.httpStatus !== 404 && reply.httpStatus !== 409) {
              remember(self.key, null); // refused by content: this session is gone
            }
            throw new Error(reply.error || "Wysyłka została przerwana.");
          },
          function () {
            // network error: wait, ask the server how much it has, continue from there
            if (failures >= RETRIES) {
              throw new Error("Brak połączenia. Wybierz ten sam plik ponownie, aby dokończyć wysyłkę.");
            }
            failures += 1;
            return wait(1000 * failures)
              .then(function () {
                return self.request(session.url, { method: "GET" });
              })
              .then(
                function (state) {
                  if (state.ok) {
                    offset = state.offset;
                  }
                  return step();
                },
                function () {
                  return step();
                }
              );
          }
        );
    };
    return step();
  };

  Uploader.prototype.finish = function (session) {
    var self = this;
    return this.request(session.complete_url, { method: "POST" }).then(function (reply) {
      if (reply.httpStatus !== 409) {
        remember(self.key, null);
      }
      if (!reply.ok) {
        throw new Error(reply.error || "Nie udało się zapisać pliku.");
      }
      self.status.textContent = "Wysłano. Sprawdzamy i przetwarzamy plik.";
      window.location.assign(reply.redirect);
    });
  };

  Uploader.prototype.run = function () {
    var self = this;
    var button = this.form.querySelector('button[type="submit"]');
    button.disabled = true;
    show(this.box, []);
    return this.open()
      .then(function (session) {
        return self.send(session).then(function () {
          return self.finish(session);
        });
      })
      .catch(function (error) {
        show(self.box, [self.file.name + ": " + error.message]);
        self.status.textContent = "";
      })
      .then(function () {
        button.disabled = false;
      });
  };

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

    document.querySelectorAll("form[data-resumable]").forEach(function (form) {
      var box = form.querySelector("[data-upload-message]");
      var input = form.querySelector('input[type="file"]');
      var interrupted = pendingNames(form.dataset.kind);
      if (interrupted.length) {
        show(box, [
          "Przerwana wysyłka: " + interrupted.join(", ") + ". Wybierz ten sam plik ponownie, aby ją dokończyć.",
        ]);
      }
      form.addEventListener("submit", function (event) {
        event.preventDefault(); // the upload goes in chunks, never as one form post
        var file = (input.files || [])[0];
        checkMedia(form, file).then(function (problems) {
          if (problems.length) {
            show(box, problems);
            input.setAttribute("aria-invalid", "true");
            return;
          }
          input.removeAttribute("aria-invalid");
          new Uploader(form, file).run();
        });
      });
    });
  });
})();
