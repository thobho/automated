/* Public artist page behaviour (US-3.6). Plain script, no inline code (strict CSP).
   Everything here is an enhancement: without it the page still works (photos are links to the
   files, the extra offers are visible). */
(function () {
  "use strict";

  /* "Pokaż pozostałe": a real button with aria-expanded / aria-controls. */
  document.querySelectorAll(".offers-more").forEach(function (box) {
    var button = box.querySelector(".offers-more__toggle");
    var list = button && document.getElementById(button.getAttribute("aria-controls"));
    if (!button || !list) return;
    list.hidden = true;
    button.hidden = false;
    button.addEventListener("click", function () {
      var open = button.getAttribute("aria-expanded") !== "true";
      button.setAttribute("aria-expanded", String(open));
      list.hidden = !open;
    });
  });

  /* Gallery: a modal <dialog> (focus stays inside, Esc closes, focus returns to the opener). */
  var gallery = document.querySelector("[data-gallery]");
  var dialog = document.getElementById("lightbox");
  if (!gallery || !dialog || typeof dialog.showModal !== "function") return;

  var links = Array.prototype.slice.call(gallery.querySelectorAll(".gallery__open"));
  var image = document.createElement("img"); /* made here: no empty-src image in the HTML */
  image.className = "lightbox__image";
  image.alt = "";
  dialog.querySelector(".lightbox__frame").appendChild(image);
  var counter = dialog.querySelector(".lightbox__counter");
  var current = 0;
  var opener = null;

  function show(index) {
    current = (index + links.length) % links.length;
    var thumb = links[current].querySelector("img");
    image.src = links[current].getAttribute("href");
    image.alt = thumb ? thumb.alt : "";
    counter.textContent = current + 1 + " / " + links.length;
  }

  links.forEach(function (link, index) {
    link.addEventListener("click", function (event) {
      event.preventDefault();
      opener = link;
      show(index);
      dialog.showModal();
      dialog.querySelector("[data-lightbox=close]").focus();
    });
  });

  dialog.addEventListener("click", function (event) {
    var action = event.target.getAttribute && event.target.getAttribute("data-lightbox");
    if (action === "next") show(current + 1);
    else if (action === "prev") show(current - 1);
    else if (action === "close" || event.target === dialog) dialog.close();
  });

  dialog.addEventListener("keydown", function (event) {
    if (event.key === "ArrowRight") show(current + 1);
    else if (event.key === "ArrowLeft") show(current - 1);
    else if (event.key === "Tab") {
      /* A modal dialog lets Tab leave for the browser's own controls: keep it in a loop. */
      var controls = dialog.querySelectorAll("button");
      var first = controls[0];
      var last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }
  });

  dialog.addEventListener("close", function () {
    if (opener) opener.focus();
  });
})();
