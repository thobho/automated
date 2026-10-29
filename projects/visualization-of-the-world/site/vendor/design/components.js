// visualization-of-the-world - component behaviour (no dependencies, no build step).
// Each initialiser finds its markup by data-* attributes, so pages only include this file.
(function () {
  "use strict";

  const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Mobile menu: button[aria-controls] toggles a [hidden] sheet and a scrim; Esc and scrim close it.
  function initMenus(root) {
    root.querySelectorAll("[data-menu-button]").forEach((btn) => {
      const menu = document.getElementById(btn.getAttribute("aria-controls"));
      const scrim = document.querySelector("[data-menu-scrim]");
      if (!menu) return;
      const setOpen = (open) => {
        btn.setAttribute("aria-expanded", String(open));
        btn.querySelector("[data-menu-label]").textContent = open ? "Zamknij" : "Menu";
        menu.hidden = !open;
        if (scrim) scrim.hidden = !open;
        if (open) menu.querySelector("a, button")?.focus();
      };
      btn.addEventListener("click", () => setOpen(btn.getAttribute("aria-expanded") !== "true"));
      scrim?.addEventListener("click", () => setOpen(false));
      document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && btn.getAttribute("aria-expanded") === "true") { setOpen(false); btn.focus(); }
      });
      menu.addEventListener("click", (e) => { if (e.target.closest("a")) setOpen(false); });
    });
  }

  // Tabs (WAI-ARIA tabs pattern, automatic activation): arrows, Home, End.
  function initTabs(root) {
    root.querySelectorAll("[data-tabs]").forEach((wrap) => {
      const tabs = Array.from(wrap.querySelectorAll('[role="tab"]'));
      const select = (tab, focus) => {
        tabs.forEach((t) => {
          const on = t === tab;
          t.setAttribute("aria-selected", String(on));
          t.tabIndex = on ? 0 : -1;
          document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
        });
        if (focus) tab.focus();
        wrap.dispatchEvent(new CustomEvent("tabchange", { detail: { id: tab.id } }));
      };
      tabs.forEach((tab, i) => {
        tab.addEventListener("click", () => select(tab, false));
        tab.addEventListener("keydown", (e) => {
          const next = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: tabs.length - 1 }[e.key];
          if (next === undefined) return;
          e.preventDefault();
          select(tabs[(next + tabs.length) % tabs.length], true);
        });
      });
    });
  }

  // Place-type toggle: aria-pressed buttons, at least one stays on. Emits "placechange" with the active keys.
  function initPlaceToggles(root) {
    root.querySelectorAll("[data-place-toggle]").forEach((group) => {
      const buttons = Array.from(group.querySelectorAll("button[data-place]"));
      const status = group.querySelector("[data-place-status]");
      const active = () => buttons.filter((b) => b.getAttribute("aria-pressed") === "true").map((b) => b.dataset.place);
      buttons.forEach((b) => b.addEventListener("click", () => {
        const on = b.getAttribute("aria-pressed") === "true";
        if (on && active().length === 1) {
          if (status) status.textContent = "Co najmniej jeden typ miejscowości musi zostać zaznaczony.";
          return;
        }
        b.setAttribute("aria-pressed", String(!on));
        if (status) status.textContent = "";
        group.dispatchEvent(new CustomEvent("placechange", { detail: { active: active() }, bubbles: true }));
      }));
    });
  }

  // Year player: range input + play/pause. Emits "yearchange". Under reduced motion the player still
  // steps (the user started it) but charts are told not to tween (detail.animate = false).
  function initYearPlayers(root) {
    root.querySelectorAll("[data-year-player]").forEach((wrap) => {
      const range = wrap.querySelector('input[type="range"]');
      const out = wrap.querySelector("output");
      const btn = wrap.querySelector("[data-play]");
      const step = parseInt(getComputedStyle(document.documentElement).getPropertyValue("--play-step"), 10) || 450;
      let timer = null;
      const emit = () => {
        out.textContent = range.value;
        wrap.dispatchEvent(new CustomEvent("yearchange", { detail: { year: +range.value, animate: !reducedMotion() }, bubbles: true }));
      };
      const stop = () => {
        clearInterval(timer); timer = null;
        btn.setAttribute("aria-pressed", "false");
        btn.setAttribute("aria-label", "Odtwórz zmiany w czasie");
        btn.querySelector("[data-icon-play]").hidden = false;
        btn.querySelector("[data-icon-pause]").hidden = true;
      };
      const play = () => {
        if (+range.value >= +range.max) range.value = range.min;
        btn.setAttribute("aria-pressed", "true");
        btn.setAttribute("aria-label", "Zatrzymaj odtwarzanie");
        btn.querySelector("[data-icon-play]").hidden = true;
        btn.querySelector("[data-icon-pause]").hidden = false;
        timer = setInterval(() => {
          if (+range.value >= +range.max) { stop(); return; }
          range.value = +range.value + (+range.step || 1);
          emit();
        }, step);
      };
      range.addEventListener("input", () => { stop(); emit(); });
      btn.addEventListener("click", () => (timer ? stop() : play()));
      out.textContent = range.value;
    });
  }

  // Chapter navigation: prev/next buttons move between [data-chapter] sections and update progress.
  function initChapterNav(root) {
    root.querySelectorAll("[data-chapter-nav]").forEach((nav) => {
      const chapters = Array.from(nav.querySelectorAll("[data-chapter-link]"));
      const segs = Array.from(nav.querySelectorAll(".chapter-nav__progress span"));
      const title = nav.querySelector("[data-chapter-title]");
      const count = nav.querySelector("[data-chapter-count]");
      const prev = nav.querySelector("[data-chapter-prev]");
      const next = nav.querySelector("[data-chapter-next]");
      let current = Math.max(0, chapters.findIndex((a) => a.getAttribute("aria-current") === "step"));
      const render = () => {
        chapters.forEach((a, i) => (i === current ? a.setAttribute("aria-current", "step") : a.removeAttribute("aria-current")));
        segs.forEach((s, i) => (s.dataset.state = i < current ? "done" : i === current ? "current" : "todo"));
        title.textContent = chapters[current].textContent;
        count.textContent = `Rozdział ${current + 1} z ${chapters.length}`;
        prev.disabled = current === 0;
        next.disabled = current === chapters.length - 1;
      };
      prev.addEventListener("click", () => { current = Math.max(0, current - 1); render(); });
      next.addEventListener("click", () => { current = Math.min(chapters.length - 1, current + 1); render(); });
      chapters.forEach((a, i) => a.addEventListener("click", (e) => { e.preventDefault(); current = i; render(); }));
      render();
    });
  }

  function init(root = document) {
    initMenus(root);
    initTabs(root);
    initPlaceToggles(root);
    initYearPlayers(root);
    initChapterNav(root);
  }

  window.VotwComponents = { init, reducedMotion };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => init());
  else init();
})();
