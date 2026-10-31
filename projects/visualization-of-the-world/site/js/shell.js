// Page chrome shared by every page: skip link, top bar, nav, provenance banner, theme switch, footer.
// Runs before components.js (which wires the mobile menu). Theme: html.theme-light / .theme-dark / none (auto).
// Provenance comes from <body data-provenance="real">; without it the page is part of the synthetic demo.
(function () {
  "use strict";
  const PAGES = [
    ["index.html", "Overview"], ["real.html", "Real data"], ["charts.html", "Charts"], ["interaction.html", "Interaction"],
    ["maps.html", "Maps"], ["formats.html", "Formats"], ["polish.html", "Layout and polish"], ["matrix.html", "Capabilities"],
  ];
  const html = document.documentElement;
  const here = (location.pathname.split("/").pop() || "index.html");
  const real = document.body.dataset.provenance === "real";
  // Same wording as research/poland-demography-housing; every number is traceable to a source id.
  const REAL_BANNER = "REAL DATA — Statistics Poland (GUS) and Eurostat via the poland-demography-housing research series. Housing completions for 2000-2008 are labelled proxies (see chart annotations); boundaries and city names were already real.";
  const DEMO_BANNER = "DEMO DATA, NOT REAL. Every number on this site is made up to show what the library can do. Only boundaries and place names are real.";
  const store = {
    get() { try { return localStorage.getItem("votw-theme"); } catch (e) { return null; } },
    set(v) { try { localStorage.setItem("votw-theme", v); } catch (e) { /* private mode: theme just is not remembered */ } },
  };
  function applyTheme(t) {
    html.classList.remove("theme-light", "theme-dark");
    if (t === "light" || t === "dark") html.classList.add("theme-" + t);
    document.dispatchEvent(new CustomEvent("themechange", { detail: { theme: t } }));
  }
  const q = new URLSearchParams(location.search).get("theme");
  const saved = (q === "light" || q === "dark") ? q : store.get();
  if (saved === "light" || saved === "dark") html.classList.add("theme-" + saved);

  const links = (cls) => PAGES.map(([h, t]) => `<a href="${h}"${h === here ? ' aria-current="page"' : ""}>${t}</a>`).join("");
  const switcher = (id) => `<div class="theme-switch"><label class="small secondary" for="${id}">Theme</label>
    <select class="select" id="${id}" data-theme-select aria-label="Colour theme"><option value="auto">Auto</option><option value="light">Light</option><option value="dark">Dark</option></select></div>`;
  const top = `
<a class="skip-link" href="#main">Skip to content</a>
<header class="topbar"><div class="container topbar__inner">
  <a class="brand" href="index.html"><svg class="brand__mark" viewBox="0 0 22 22" aria-hidden="true"><rect x="1" y="12" width="5" height="9" rx="1" fill="var(--data-place-big-cities)"/><rect x="8.5" y="6" width="5" height="15" rx="1" fill="var(--data-place-small-cities)"/><rect x="16" y="1" width="5" height="20" rx="1" fill="var(--data-place-villages)"/></svg>Polska w danych · ${real ? "real data" : "demo"}</a>
  <nav class="topbar__nav" aria-label="Main">${links()}</nav>
  ${switcher("theme-top")}
  <button class="btn btn--secondary topbar__menu-btn" type="button" data-menu-button aria-expanded="false" aria-controls="mobile-menu"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg><span data-menu-label>Menu</span></button>
</div></header>
<nav class="mobile-menu" id="mobile-menu" aria-label="Main (mobile)" hidden><ul>${PAGES.map(([h, t]) => `<li><a href="${h}"${h === here ? ' aria-current="page"' : ""}>${t}</a></li>`).join("")}</ul></nav>
<div class="scrim" data-menu-scrim hidden></div>
<div class="provenance-banner provenance-banner--${real ? "real" : "demo"}" role="note"><div class="container">${real
    ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m4 12 5 5L20 6"/></svg>'
    : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 3 2 20h20L12 3zM12 10v4M12 17v.5"/></svg>'}<span>${real ? REAL_BANNER : DEMO_BANNER}</span></div></div>`;
  const foot = real ? `
<footer class="site-footer"><div class="container">
  <h2>About this page</h2>
  <ul><li>Numbers: Statistics Poland (GUS) Bank Danych Lokalnych and Eurostat, compiled in the <code>poland-demography-housing</code> research series. Every chart footer lists the source ids (S1, S15, S29-S32, S41-S44) and the accessed date; CSV and table exports repeat them in a <code>source_id</code> column.</li>
  <li>Housing completions 2009-2025 use the direct series (GUS BDL var 748247 single-family and multi-family, plus var 748601 total). 2000-2008 splits of houses and flats are labelled proxies (var 430 individual construction, var 748601 own use); proxy and direct years are never drawn as one unmarked line.</li>
  <li>Boundaries and city names: GUGiK PRG and GeoNames via the poland-geography research, simplified. Charts: Apache ECharts 6.1.0 (vendored). Look: the project design system.</li>
  <li>Polish "Źródło:" in the design system is shown here as "Source:" because this page text is English.</li></ul>
  <p class="site-footer__legal">REAL DATA — GUS and Eurostat, source ids in every chart footer. Housing 2000-2008 is proxy-based; read the annotations before quoting those years.</p>
</div></footer>` : `
<footer class="site-footer"><div class="container">
  <h2>About this demo</h2>
  <ul><li>Charts: Apache ECharts 6.1.0 (vendored in <code>vendor/lib</code>). Look: the project design system (<code>vendor/design</code>).</li>
  <li>Boundaries and city names: GUGiK PRG and GeoNames via the poland-geography research, simplified. Numbers: <strong>synthetic</strong>, generated by <code>scripts/make_demo_data.py</code>.</li>
  <li>Polish "Źródło:" in the design system is shown here as "Source:" because this demo page text is English.</li></ul>
  <p class="site-footer__legal">DEMO DATA, NOT REAL. Do not quote any number from this site.</p>
</div></footer>`;
  document.body.insertAdjacentHTML("afterbegin", top);
  document.body.insertAdjacentHTML("beforeend", foot);
  document.querySelectorAll("[data-theme-select]").forEach((sel) => {
    sel.value = saved === "light" || saved === "dark" ? saved : "auto";
    sel.addEventListener("change", () => {
      store.set(sel.value);
      document.querySelectorAll("[data-theme-select]").forEach((o) => (o.value = sel.value));
      applyTheme(sel.value);
    });
  });
  // The mobile menu also needs the switch; put a second one inside it
  document.getElementById("mobile-menu").insertAdjacentHTML("beforeend", switcher("theme-menu"));
  document.querySelectorAll("#theme-menu").forEach((sel) => {
    sel.value = saved === "light" || saved === "dark" ? saved : "auto";
    sel.addEventListener("change", () => { store.set(sel.value); document.querySelectorAll("[data-theme-select]").forEach((o) => (o.value = sel.value)); applyTheme(sel.value); });
  });
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => document.dispatchEvent(new CustomEvent("themechange")));
})();
