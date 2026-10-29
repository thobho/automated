// Style-guide page: renders token swatches from tokens.json and demo charts from sample data.
// Plain SVG, no chart library: the real site will use ECharts (see research/viz-libraries) themed
// with the same tokens; these demos fix the look the theme must reproduce.
(function () {
  "use strict";
  const html = document.documentElement;
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const cssVar = (name) => getComputedStyle(html).getPropertyValue(name).trim();
  const NS = "http://www.w3.org/2000/svg";
  const fmt1 = new Intl.NumberFormat("pl-PL", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  const fmtSigned = (v) => (v > 0 ? "+" : v < 0 ? "−" : "") + fmt1.format(Math.abs(v));
  const PLACES = [
    { key: "big-cities", label: "Duże miasta" },
    { key: "small-cities", label: "Małe miasta" },
    { key: "villages", label: "Wsie" },
  ];
  const MAP_BREAKS = [30, 35, 40, 45, 50, 55]; // 7 classes
  const state = { year: 2024, active: new Set(PLACES.map((p) => p.key)), data: null, tokens: null };
  const onTheme = [];

  // ---------- colour helpers (for live contrast read-outs and label ink on map tiles) ----------
  function lum(hex) {
    const m = /^#?([0-9a-f]{6})$/i.exec(hex);
    if (!m) return null;
    const c = [0, 2, 4].map((i) => parseInt(m[1].slice(i, i + 2), 16) / 255)
      .map((v) => (v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
  }
  function ratio(a, b) {
    const la = lum(a), lb = lum(b);
    if (la === null || lb === null) return null;
    return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
  }
  const inkOn = (hex) => (ratio(hex, "#ffffff") >= ratio(hex, "#000000") ? "#ffffff" : "#0b1014");

  // ---------- direction / theme switcher ----------
  function initSwitcher() {
    const dirSel = $("#sg-direction"), themeSel = $("#sg-theme");
    dirSel.value = html.classList.contains("dir-beton") ? "beton" : html.classList.contains("dir-noc") ? "noc" : "baltyk";
    themeSel.value = html.classList.contains("theme-dark") ? "dark" : html.classList.contains("theme-light") ? "light" : "auto";
    dirSel.addEventListener("change", () => {
      html.classList.remove("dir-beton", "dir-noc");
      if (dirSel.value !== "baltyk") html.classList.add("dir-" + dirSel.value);
    });
    themeSel.addEventListener("change", () => {
      html.classList.remove("theme-light", "theme-dark");
      if (themeSel.value !== "auto") html.classList.add("theme-" + themeSel.value);
    });
    new MutationObserver(() => onTheme.forEach((f) => f())).observe(html, { attributes: true, attributeFilter: ["class"] });
    matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => onTheme.forEach((f) => f()));
  }

  // ---------- states ----------
  function skeleton(el) {
    el.innerHTML = '<div class="skeleton" role="status" aria-label="Wczytywanie danych">' +
      [40, 85, 65, 95, 55].map((w) => `<div class="skeleton__bar" style="width:${w}%"></div>`).join("") + "</div>";
  }
  function errorState(el, retry, what) {
    el.innerHTML = '<div class="state state--error" role="alert">' +
      '<svg class="state__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M12 3 2 20h20L12 3zM12 10v4M12 17v.5"/></svg>' +
      `<p class="state__title">Nie udało się wczytać ${what}</p>` +
      '<p class="state__text">Sprawdź połączenie i spróbuj ponownie.</p>' +
      '<button class="btn btn--secondary" type="button" data-retry>Spróbuj ponownie</button></div>';
    $("[data-retry]", el).addEventListener("click", retry);
  }
  async function getJSON(url) {
    const res = await fetch(url, { cache: "no-cache" });
    if (!res.ok) throw new Error(`${url}: HTTP ${res.status}`);
    return res.json();
  }

  // ---------- token sections ----------
  const FG_TOKENS = /^(text-|link$|accent$|accent-text$|focus-ring$|border-strong$|chart-text$|chart-annotation$|chart-axis$)|-text$/;
  function fgBackground(name) {
    if (name === "text-inverse") return "bg-inverse";
    if (name === "text-on-accent") return "accent";
    return "bg-page";
  }
  function renderSwatches() {
    $$("[data-swatches]").forEach((wrap) => {
      wrap.innerHTML = wrap.dataset.swatches.split(" ").map((name) => {
        const fg = FG_TOKENS.test(name);
        const chip = fg ? `background:var(--color-${fgBackground(name)});color:var(--color-${name})`
          : `background:var(--color-${name});color:var(--color-text-primary)`;
        return `<div class="swatch" data-token="${name}"><div class="swatch__chip" style="${chip}">Aa</div>` +
          `<div class="swatch__meta"><span class="swatch__name">${name}</span><span class="swatch__hex" data-hex></span></div></div>`;
      }).join("");
    });
    updateSwatchValues();
  }
  function updateSwatchValues() {
    $$("[data-token]").forEach((sw) => {
      const name = sw.dataset.token, hex = cssVar(`--color-${name}`);
      let text = hex;
      if (FG_TOKENS.test(name)) {
        const r = ratio(hex, cssVar(`--color-${fgBackground(name)}`));
        if (r) text += ` · ${r.toFixed(2)}:1`;
      }
      $("[data-hex]", sw).textContent = text;
    });
    $$("[data-ramp='neutral'] span").forEach((s) => (s.title = cssVar(`--neutral-${s.dataset.step}`)));
  }
  function renderNeutral(tokens) {
    const steps = Object.keys(tokens.directions.baltyk.neutral);
    $("[data-ramp='neutral']").innerHTML = steps.map((k) =>
      `<span data-step="${k}" style="--chip:var(--neutral-${k});color:${+k >= 500 ? "#fff" : "#151c21"}">${k}</span>`).join("");
  }
  function renderData(tokens) {
    const d = tokens.data;
    $$("[data-data-swatches]").forEach((wrap) => {
      const set = wrap.dataset.dataSwatches;
      const names = set === "categorical" ? d.categorical.names.map((n, i) => `${i + 1} · ${n}`) : d.placeType.keys.map((k) => d.placeType.labels[k]);
      const vars = set === "categorical" ? names.map((_, i) => `--data-cat-${i + 1}`) : d.placeType.keys.map((k) => `--data-place-${k}`);
      wrap.innerHTML = names.map((n, i) => `<div class="swatch" data-data-var="${vars[i]}"><div class="swatch__chip" style="--chip:var(${vars[i]})"></div>` +
        `<div class="swatch__meta"><span class="swatch__name">${n}</span><span class="swatch__hex" data-hex></span></div></div>`).join("");
    });
    $$("[data-seq]").forEach((wrap) => {
      const ramp = d.sequential[wrap.dataset.seq];
      wrap.innerHTML = Object.entries(ramp).map(([k, hex]) => `<span style="--chip:${hex};color:${inkOn(hex)}">${k}</span>`).join("");
    });
    $$("[data-data-ramp]").forEach((wrap) => {
      const set = wrap.dataset.dataRamp, n = d[set].light.length;
      const prefix = set === "map" ? "--data-map-" : "--data-div-";
      wrap.innerHTML = Array.from({ length: n }, (_, i) => `<span style="--chip:var(${prefix}${i + 1})"></span>`).join("");
    });
    $("[data-status-swatches]").innerHTML = ["good", "warning", "serious", "critical"].map((k) =>
      `<div class="swatch"><div class="swatch__chip" style="--chip:var(--data-status-${k})"></div><div class="swatch__meta"><span class="swatch__name">${k}</span><span class="swatch__hex">${d.status[k]}</span></div></div>`).join("");
    updateDataValues();
  }
  function updateDataValues() {
    const surface = cssVar("--color-chart-surface");
    $$("[data-data-var]").forEach((sw) => {
      const hex = cssVar(sw.dataset.dataVar), r = ratio(hex, surface);
      $("[data-hex]", sw).textContent = `${hex} · ${r ? r.toFixed(2) : "?"}:1`;
    });
  }
  function renderDirections(tokens) {
    $("[data-directions]").innerHTML = Object.entries(tokens.directions).map(([key, d]) => {
      const L = d.light, D = d.dark;
      const sample = (t, label) => `<div class="direction__sample" style="background:${t["bg-page"]};color:${t["text-primary"]};border-color:${t["border-subtle"]}">` +
        `<b style="font-family:${d.fonts.display.replace(/"/g, "'")}">Gdzie mieszkamy</b>` +
        `<span style="font-family:${d.fonts.text.replace(/"/g, "'")};color:${t["text-secondary"]};font-size:0.875rem">${label}: 15 284 tys. na wsi</span>` +
        `<div class="direction__accentbar" style="background:${t.accent}"></div></div>`;
      const family = (s) => s.split(",")[0].replace(/"/g, "").replace(" Variable", "");
      return `<article class="card direction"><h3 style="margin:0">${d.label} ${d.chosen ? '<span class="badge badge--good" style="vertical-align:middle">wybrany</span>' : '<span class="badge badge--info" style="vertical-align:middle">alternatywa</span>'}</h3>` +
        sample(L, "Jasny") + sample(D, "Ciemny") +
        `<dl><dt>Tło</dt><dd>${L["bg-page"]} / ${D["bg-page"]}</dd><dt>Akcent</dt><dd>${L.accent} / ${D.accent}</dd>` +
        `<dt>Nagłówki</dt><dd>${family(d.fonts.display)}</dd><dt>Tekst</dt><dd>${family(d.fonts.text)}</dd>` +
        `<dt>Klasa</dt><dd><code>${d.chosen ? "(none)" : "dir-" + key}</code></dd></dl>` +
        `<p class="small secondary" style="margin:0">${d.rationale}</p>` +
        `<button class="btn btn--secondary" type="button" data-use-direction="${key}">Pokaż w tym stylu</button></article>`;
    }).join("");
    $$("[data-use-direction]").forEach((b) => b.addEventListener("click", () => {
      const sel = $("#sg-direction");
      sel.value = b.dataset.useDirection;
      sel.dispatchEvent(new Event("change"));
    }));
  }
  function renderTypeScale(tokens) {
    const samples = { figure: "38,1 mln", "3xl": "Ilu nas jest", "2xl": "Miasta się kurczą", xl: "Wieś rośnie najszybciej pod miastami", lg: "Ludność według typu miejscowości",
      story: "Od 2000 roku coraz więcej osób przeprowadza się z dużych miast do gmin wiejskich wokół nich. Zjawisko jest najsilniejsze pod Warszawą, Krakowem i Gdańskiem.",
      md: "Wybierz rok i typ miejscowości, aby zobaczyć zmiany.", sm: "Odsetek ludności, %, 2000-2024", xs: "Źródło: GUS, Bank Danych Lokalnych, dostęp 29.10.2026" };
    const display = new Set(["figure", "3xl", "2xl", "xl", "lg"]);
    $("[data-type-scale]").innerHTML = Object.entries(tokens.typography.scale).map(([k, s]) =>
      `<div class="specimen"><span class="specimen__meta">--text-${k} · ${s.size} · line ${s.line} · ${s.use}</span>` +
      `<p class="specimen__sample" style="font-size:var(--text-${k});line-height:var(--leading-${k});${display.has(k) ? "font-family:var(--font-display);font-weight:700;letter-spacing:var(--tracking-display)" : ""}">${samples[k] || "Zażółć gęślą jaźń"}</p></div>`).join("");
  }
  function renderSpaceRadius(tokens) {
    $("[data-space-rows]").innerHTML = Object.entries(tokens.space).filter(([k]) => k !== "0").map(([k, v]) =>
      `<div class="token-row"><code>--space-${k} · ${v}</code><div class="space-bar" style="width:var(--space-${k})"></div></div>`).join("");
    $("[data-radius-boxes]").innerHTML = Object.entries(tokens.radius).map(([k, v]) =>
      `<div class="box" style="border-radius:var(--radius-${k})">--radius-${k}<br>${v}</div>`).join("");
  }
  function renderMotion(tokens) {
    const wrap = $("[data-motion-demo]");
    wrap.innerHTML = Object.keys(tokens.motion.duration).map((k) =>
      `<div class="token-row"><code>--dur-${k} · ${tokens.motion.duration[k]}</code><div class="motion-track" style="--dur:var(--dur-${k})"><div class="motion-dot"></div></div></div>`).join("") +
      '<div><button class="btn btn--secondary" type="button" data-motion-play>Uruchom animację</button></div>';
    $("[data-motion-play]", wrap).addEventListener("click", () => $$(".motion-track", wrap).forEach((t) => t.classList.toggle("is-on")));
    const mq = matchMedia("(prefers-reduced-motion: reduce)");
    const say = () => ($("[data-motion-status]").textContent = mq.matches ? "Your system asks for reduced motion: durations are 0 ms now." : "Your system allows motion.");
    say(); mq.addEventListener("change", say);
  }

  // ---------- svg helpers ----------
  function el(name, attrs = {}, parent) {
    const n = document.createElementNS(NS, name);
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
    if (parent) parent.appendChild(n);
    return n;
  }
  function text(parent, x, y, str, attrs = {}) {
    const t = el("text", { x, y, ...attrs }, parent);
    t.textContent = str;
    return t;
  }
  // horizontal bar with 4px rounding on the value end only (square at the baseline)
  function hbar(x0, x1, y, h, r = 4) {
    const w = Math.abs(x1 - x0);
    r = Math.min(r, w, h / 2);
    if (x1 >= x0) return `M${x0},${y}H${x1 - r}Q${x1},${y} ${x1},${y + r}V${y + h - r}Q${x1},${y + h} ${x1 - r},${y + h}H${x0}Z`;
    return `M${x0},${y}H${x1 + r}Q${x1},${y} ${x1},${y + r}V${y + h - r}Q${x1},${y + h} ${x1 + r},${y + h}H${x0}Z`;
  }
  function tooltip(chartEl) {
    let tip = $(".tooltip", chartEl);
    if (!tip) { tip = document.createElement("div"); tip.className = "tooltip"; tip.hidden = true; chartEl.appendChild(tip); }
    return {
      show(htmlStr, x, y) {
        tip.innerHTML = htmlStr; tip.hidden = false;
        const w = chartEl.clientWidth, tw = tip.offsetWidth, th = tip.offsetHeight;
        let left = x + 12; if (left + tw > w) left = Math.max(0, x - tw - 12);
        let top = Math.max(0, y - th - 8);
        tip.style.left = left + "px"; tip.style.top = top + "px";
      },
      hide() { tip.hidden = true; },
    };
  }
  const row = (swatchVar, label, value) => `<div class="tooltip__row"><span class="legend__swatch" style="--swatch:var(${swatchVar})"></span>${label}<span class="tooltip__value">${value}</span></div>`;

  // ---------- line chart ----------
  function drawLine() {
    const host = $("[data-chart='line']"), data = state.data;
    const W = Math.max(280, host.clientWidth), H = Math.round(Math.max(240, Math.min(340, W * 0.58)));
    const m = { t: 24, r: 92, b: 28, l: 30 };
    const years = data.years, x0 = years[0], x1 = years[years.length - 1];
    const X = (yr) => m.l + ((yr - x0) / (x1 - x0)) * (W - m.l - m.r);
    const Y = (v) => H - m.b - (v / 50) * (H - m.t - m.b);
    host.querySelector("svg")?.remove();
    const visible = PLACES.filter((p) => state.active.has(p.key));
    const last = visible.map((p) => `${p.label} ${fmt1.format(data.placeShare.series[p.key].at(-1))}%`).join(", ");
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: "img", tabindex: "0",
      "aria-label": `Wykres liniowy, odsetek ludności 2000-2024. W 2024: ${last}. Strzałki zmieniają rok.` });
    host.prepend(svg);
    for (const v of [10, 20, 30, 40, 50]) {
      el("line", { class: "grid-line", x1: m.l, x2: W - m.r, y1: Y(v), y2: Y(v) }, svg);
      text(svg, m.l - 6, Y(v) + 4, String(v), { class: "tick", "text-anchor": "end" });
    }
    el("line", { class: "axis-line", x1: m.l, x2: W - m.r, y1: Y(0), y2: Y(0) }, svg);
    text(svg, m.l - 6, Y(0) + 4, "0", { class: "tick", "text-anchor": "end" });
    const xt = W < 480 ? [2000, 2012, 2024] : [2000, 2006, 2012, 2018, 2024];
    xt.forEach((yr) => text(svg, X(yr), H - 8, String(yr), { class: "tick", "text-anchor": yr === x0 ? "start" : yr === x1 ? "end" : "middle" }));
    // annotation
    el("line", { class: "annotation-line", x1: X(2011), x2: X(2011), y1: m.t - 6, y2: Y(0) }, svg);
    text(svg, X(2011) + 4, m.t - 10, "Spis powszechny 2011", { class: "annotation-text" });
    // series
    visible.forEach((p) => {
      const vals = data.placeShare.series[p.key];
      el("path", { class: "series-line", style: `stroke:var(--data-place-${p.key})`, d: vals.map((v, i) => `${i ? "L" : "M"}${X(years[i]).toFixed(1)},${Y(v).toFixed(1)}`).join("") }, svg);
    });
    // direct labels, de-collided
    const labels = visible.map((p) => ({ p, y: Y(data.placeShare.series[p.key].at(-1)) })).sort((a, b) => a.y - b.y);
    for (let i = 1; i < labels.length; i++) if (labels[i].y - labels[i - 1].y < 15) labels[i].y = labels[i - 1].y + 15;
    labels.forEach(({ p, y }) => {
      el("rect", { x: W - m.r + 8, y: y - 1, width: 8, height: 2, rx: 1, style: `fill:var(--data-place-${p.key})` }, svg);
      text(svg, W - m.r + 20, y + 4, p.label, { class: "direct-label" });
    });
    // interaction: crosshair + tooltip, pointer and keyboard
    const cross = el("line", { class: "crosshair", y1: m.t, y2: Y(0), visibility: "hidden" }, svg);
    const markers = visible.map((p) => el("circle", { class: "marker", r: 4, style: `fill:var(--data-place-${p.key})`, visibility: "hidden" }, svg));
    const hit = el("rect", { class: "hit", x: m.l, y: 0, width: W - m.l - m.r, height: H }, svg);
    const tip = tooltip(host);
    let idx = years.length - 1;
    const show = (i) => {
      idx = Math.max(0, Math.min(years.length - 1, i));
      const x = X(years[idx]);
      cross.setAttribute("x1", x); cross.setAttribute("x2", x); cross.setAttribute("visibility", "visible");
      visible.forEach((p, k) => { markers[k].setAttribute("cx", x); markers[k].setAttribute("cy", Y(data.placeShare.series[p.key][idx])); markers[k].setAttribute("visibility", "visible"); });
      const rows = visible.map((p) => ({ p, v: data.placeShare.series[p.key][idx] })).sort((a, b) => b.v - a.v);
      tip.show(`<div class="tooltip__title">${years[idx]}</div>` + rows.map(({ p, v }) => row(`--data-place-${p.key}`, p.label, fmt1.format(v) + "%")).join(""), x, m.t + 10);
    };
    const hide = () => { cross.setAttribute("visibility", "hidden"); markers.forEach((mk) => mk.setAttribute("visibility", "hidden")); tip.hide(); };
    hit.addEventListener("pointermove", (e) => {
      const r = svg.getBoundingClientRect(), px = (e.clientX - r.left) * (W / r.width);
      show(Math.round(((px - m.l) / (W - m.l - m.r)) * (x1 - x0)));
    });
    hit.addEventListener("pointerleave", hide);
    svg.addEventListener("focus", () => show(idx));
    svg.addEventListener("blur", hide);
    svg.addEventListener("keydown", (e) => {
      const d = { ArrowRight: 1, ArrowLeft: -1, ArrowUp: 1, ArrowDown: -1 }[e.key];
      if (d) { e.preventDefault(); show(idx + d); } else if (e.key === "Home") { e.preventDefault(); show(0); } else if (e.key === "End") { e.preventDefault(); show(years.length - 1); } else if (e.key === "Escape") hide();
    });
  }
  function drawLineTable() {
    const data = state.data;
    $("[data-chart='line-table']").innerHTML = '<div class="table-scroll" tabindex="0" role="region" aria-label="Tabela: odsetek ludności według typu miejscowości"><table class="data-table">' +
      "<caption>Odsetek ludności według typu miejscowości, %</caption><thead><tr><th scope=\"col\">Rok</th>" +
      PLACES.map((p) => `<th scope="col" class="n">${p.label}</th>`).join("") + "</tr></thead><tbody>" +
      data.years.map((y, i) => `<tr><th scope="row">${y}</th>` + PLACES.map((p) => `<td class="n">${fmt1.format(data.placeShare.series[p.key][i])}</td>`).join("") + "</tr>").join("") +
      "</tbody></table></div>";
  }

  // ---------- tile map ----------
  const mapClass = (v) => MAP_BREAKS.filter((b) => v >= b).length; // 0..6
  function legendMarkup() {
    const ticks = ["<30", ...MAP_BREAKS.slice(1, -1).map(String), "55+"];
    return '<div class="legend-scale__title">Odsetek ludności na wsi, %</div><div class="legend-scale__bins">' +
      Array.from({ length: 7 }, (_, i) => `<span style="--swatch:var(--data-map-${i + 1})"></span>`).join("") +
      `</div><div class="legend-scale__ticks"><span>&lt;30</span><span>35</span><span>40</span><span>45</span><span>50</span><span>55+</span></div>` +
      '<div class="legend-scale__nodata"><span class="swatch-nodata" aria-hidden="true"></span>brak danych</div>';
  }
  function drawMap() {
    const host = $("[data-chart='map']"), data = state.data, yi = data.years.indexOf(state.year);
    const W = Math.max(260, host.clientWidth), cell = Math.min(72, Math.floor(W / 5)), H = cell * 4 + 4;
    const ox = Math.floor((W - cell * 5) / 2);
    host.querySelector("svg")?.remove();
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: "img", tabindex: "0",
      "aria-label": `Kartogram kafelkowy województw, rok ${state.year}. Strzałki wybierają województwo.` });
    host.prepend(svg);
    const pat = el("pattern", { id: "nodata-hatch", width: 6, height: 6, patternUnits: "userSpaceOnUse", patternTransform: "rotate(45)" }, el("defs", {}, svg));
    el("rect", { width: 6, height: 6, style: "fill:var(--color-map-nodata)" }, pat);
    el("line", { x1: 0, y1: 0, x2: 0, y2: 6, style: "stroke:var(--color-map-nodata-hatch);stroke-width:2" }, pat);
    const tip = tooltip(host);
    const tiles = data.regions.map((r) => {
      const v = r.values[yi], x = ox + r.col * cell, y = r.row * cell + 2;
      const fillVar = v == null ? null : `--data-map-${mapClass(v) + 1}`;
      const g = el("g", {}, svg);
      const rect = el("rect", { class: "tile", x, y, width: cell, height: cell, rx: 4, style: fillVar ? `fill:var(${fillVar})` : "fill:url(#nodata-hatch)" }, g);
      const ink = fillVar ? inkOn(cssVar(fillVar)) : cssVar("--color-text-primary");
      text(g, x + cell / 2, y + cell / 2 + 4, r.code, { class: "tile-label", "text-anchor": "middle", style: `fill:${ink}` });
      return { r, v, rect, x, y };
    });
    const tileHtml = (t) => `<div class="tooltip__title">${t.r.name}</div>` +
      (t.v == null ? '<div class="tooltip__row">brak danych w tym roku</div>' : row(`--data-map-${mapClass(t.v) + 1}`, "Ludność na wsi", fmt1.format(t.v) + "%"));
    let active = -1;
    const focusTile = (i) => {
      tiles.forEach((t) => t.rect.classList.remove("is-active"));
      active = (i + tiles.length) % tiles.length;
      const t = tiles[active];
      t.rect.classList.add("is-active");
      t.rect.parentNode.appendChild(t.rect.nextSibling); // keep label above
      svg.appendChild(t.rect.parentNode); // active stroke above neighbours
      const s = host.clientWidth / W;
      tip.show(tileHtml(t), (t.x + cell) * s, (t.y + 8) * s);
    };
    tiles.forEach((t, i) => {
      t.rect.addEventListener("pointerenter", () => focusTile(i));
      t.rect.addEventListener("pointerleave", () => { t.rect.classList.remove("is-active"); tip.hide(); });
    });
    svg.addEventListener("focus", () => focusTile(active < 0 ? 0 : active));
    svg.addEventListener("blur", () => { tiles.forEach((t) => t.rect.classList.remove("is-active")); tip.hide(); });
    svg.addEventListener("keydown", (e) => {
      const d = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
      if (d) { e.preventDefault(); focusTile(active + d); } else if (e.key === "Escape") tip.hide();
    });
    $("[data-map-year]").textContent = state.year;
  }

  // ---------- ranked bars ----------
  function drawBars() {
    const host = $("[data-chart='bars']"), data = state.data, yi = data.years.indexOf(state.year);
    const rows = data.regions.map((r) => ({ r, v: r.values[yi] })).sort((a, b) => (b.v ?? -1) - (a.v ?? -1));
    const W = Math.max(280, host.clientWidth), bh = 16, gap = 6, m = { t: 4, r: 44, b: 22, l: W < 420 ? 128 : 150 };
    const H = m.t + rows.length * (bh + gap) + m.b;
    const X = (v) => m.l + (v / 70) * (W - m.l - m.r);
    host.querySelector("svg")?.remove();
    const top = rows[0];
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: "img", tabindex: "0",
      "aria-label": `Wykres słupkowy, odsetek ludności na wsi w ${state.year}. Najwyżej: ${top.r.name}, ${fmt1.format(top.v)}%. Strzałki wybierają województwo.` });
    host.prepend(svg);
    for (const v of [20, 40, 60]) {
      el("line", { class: "grid-line", x1: X(v), x2: X(v), y1: m.t, y2: H - m.b }, svg);
      text(svg, X(v), H - 6, String(v), { class: "tick", "text-anchor": "middle" });
    }
    const tip = tooltip(host);
    const bars = rows.map((d, i) => {
      const y = m.t + i * (bh + gap);
      text(svg, m.l - 8, y + bh / 2 + 4, d.r.name, { class: "tick", "text-anchor": "end" });
      let bar = null;
      if (d.v == null) text(svg, X(0) + 4, y + bh / 2 + 4, "brak danych", { class: "value-label" });
      else {
        bar = el("path", { class: "bar", d: hbar(X(0), X(d.v), y, bh), style: "fill:var(--data-place-villages)" }, svg);
        text(svg, X(d.v) + 4, y + bh / 2 + 4, fmt1.format(d.v), { class: "value-label" });
      }
      return { d, y, bar };
    });
    el("line", { class: "axis-line", x1: X(0), x2: X(0), y1: m.t, y2: H - m.b }, svg);
    let active = -1;
    const focusBar = (i) => {
      active = (i + bars.length) % bars.length;
      bars.forEach((b, k) => b.bar && b.bar.classList.toggle("is-dim", k !== active));
      const b = bars[active], s = host.clientWidth / W;
      tip.show(`<div class="tooltip__title">${b.d.r.name}</div>` + (b.d.v == null ? '<div class="tooltip__row">brak danych</div>' : row("--data-place-villages", "Ludność na wsi", fmt1.format(b.d.v) + "%")), (b.d.v == null ? X(0) : X(b.d.v)) * s, b.y * s);
    };
    const clear = () => { bars.forEach((b) => b.bar && b.bar.classList.remove("is-dim")); tip.hide(); };
    bars.forEach((b, i) => {
      const hit = el("rect", { class: "hit", x: 0, y: b.y - gap / 2, width: W, height: bh + gap }, svg);
      hit.addEventListener("pointerenter", () => focusBar(i));
      hit.addEventListener("pointerleave", clear);
    });
    svg.addEventListener("focus", () => focusBar(active < 0 ? 0 : active));
    svg.addEventListener("blur", clear);
    svg.addEventListener("keydown", (e) => {
      const d = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[e.key];
      if (d) { e.preventDefault(); focusBar(active + d); } else if (e.key === "Escape") clear();
    });
    $("[data-bars-year]").textContent = state.year;
  }

  // ---------- diverging bars ----------
  function drawDiverging() {
    const host = $("[data-chart='diverging']"), data = state.data;
    const rows = data.regions.map((r) => ({ r, v: r.change })).sort((a, b) => b.v - a.v);
    const W = Math.max(280, host.clientWidth), bh = 16, gap = 6, m = { t: 22, r: 40, b: 22, l: W < 420 ? 128 : 150 };
    const H = m.t + rows.length * (bh + gap) + m.b;
    const max = 10, mid = m.l + (W - m.l - m.r) / 2;
    const X = (v) => mid + (v / max) * ((W - m.l - m.r) / 2);
    host.querySelector("svg")?.remove();
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: "img", tabindex: "0",
      "aria-label": `Wykres rozbieżny: zmiana liczby mieszkańców wsi 2014-2024. Największy wzrost: ${rows[0].r.name} ${fmtSigned(rows[0].v)}%, największy spadek: ${rows.at(-1).r.name} ${fmtSigned(rows.at(-1).v)}%.` });
    host.prepend(svg);
    text(svg, X(-max), 12, "← spadek", { class: "axis-title" });
    text(svg, X(max), 12, "wzrost →", { class: "axis-title", "text-anchor": "end" });
    for (const v of [-10, -5, 5, 10]) {
      el("line", { class: "grid-line", x1: X(v), x2: X(v), y1: m.t, y2: H - m.b }, svg);
      text(svg, X(v), H - 6, fmtSigned(v), { class: "tick", "text-anchor": "middle" });
    }
    text(svg, X(0), H - 6, "0", { class: "tick", "text-anchor": "middle" });
    const tip = tooltip(host);
    const bars = rows.map((d, i) => {
      const y = m.t + i * (bh + gap);
      text(svg, m.l - 8, y + bh / 2 + 4, d.r.name, { class: "tick", "text-anchor": "end" });
      const bar = el("path", { class: "bar", d: hbar(X(0), X(d.v), y, bh), style: `fill:var(--data-div-${d.v < 0 ? 2 : 6})` }, svg);
      const label = fmtSigned(d.v);
      if (d.v >= 0) text(svg, X(d.v) + 4, y + bh / 2 + 4, label, { class: "value-label" });
      else text(svg, X(d.v) - 4, y + bh / 2 + 4, label, { class: "value-label", "text-anchor": "end" });
      return { d, y, bar };
    });
    el("line", { class: "axis-line", x1: X(0), x2: X(0), y1: m.t, y2: H - m.b }, svg);
    let active = -1;
    const focusBar = (i) => {
      active = (i + bars.length) % bars.length;
      bars.forEach((b, k) => b.bar.classList.toggle("is-dim", k !== active));
      const b = bars[active], s = host.clientWidth / W;
      tip.show(`<div class="tooltip__title">${b.d.r.name}</div>` + row(`--data-div-${b.d.v < 0 ? 2 : 6}`, "Zmiana 2014-2024", fmtSigned(b.d.v) + "%"), X(Math.max(0, b.d.v)) * s, b.y * s);
    };
    const clear = () => { bars.forEach((b) => b.bar.classList.remove("is-dim")); tip.hide(); };
    bars.forEach((b, i) => {
      const hit = el("rect", { class: "hit", x: 0, y: b.y - gap / 2, width: W, height: bh + gap }, svg);
      hit.addEventListener("pointerenter", () => focusBar(i));
      hit.addEventListener("pointerleave", clear);
    });
    svg.addEventListener("focus", () => focusBar(active < 0 ? 0 : active));
    svg.addEventListener("blur", clear);
    svg.addEventListener("keydown", (e) => {
      const d = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[e.key];
      if (d) { e.preventDefault(); focusBar(active + d); } else if (e.key === "Escape") clear();
    });
  }

  function drawTableDemo() {
    const data = state.data, cols = [2000, 2012, 2024].map((y) => data.years.indexOf(y));
    $("[data-table-demo]").innerHTML = '<div class="table-scroll" tabindex="0" role="region" aria-label="Tabela: ludność na wsi według województw"><table class="data-table">' +
      "<caption>Odsetek ludności na wsi według województw, % (dane przykładowe)</caption><thead><tr><th scope=\"col\">Województwo</th>" +
      [2000, 2012, 2024].map((y) => `<th scope="col" class="n">${y}</th>`).join("") + '<th scope="col" class="n">Zmiana 2014-2024, %</th></tr></thead><tbody>' +
      data.regions.map((r) => `<tr><th scope="row">${r.name}</th>` + cols.map((i) => r.values[i] == null ? '<td class="n missing">brak</td>' : `<td class="n">${fmt1.format(r.values[i])}</td>`).join("") +
        `<td class="n">${fmtSigned(r.change)}</td></tr>`).join("") +
      '</tbody></table></div><footer class="chart-source"><span class="chart-source__label">Źródło:</span><a href="sample/sample-data.json">dane przykładowe (nie GUS)</a></footer>';
  }

  const DATA_VIEWS = [
    ["[data-chart='line']", () => { drawLine(); drawLineTable(); }],
    ["[data-chart='map']", drawMap],
    ["[data-chart='bars']", drawBars],
    ["[data-chart='diverging']", drawDiverging],
    ["[data-table-demo]", drawTableDemo],
  ];
  function drawAll() { DATA_VIEWS.forEach(([, f]) => f()); }

  async function loadSample() {
    state.data = null;
    DATA_VIEWS.forEach(([sel]) => skeleton($(sel)));
    $("[data-map-legend]").innerHTML = "";
    try {
      state.data = await getJSON("sample/sample-data.json");
      DATA_VIEWS.forEach(([sel]) => ($(sel).innerHTML = ""));
      $("[data-map-legend]").innerHTML = legendMarkup();
      drawAll();
      document.body.dataset.sample = "ok";
    } catch (err) {
      console.info("sample data not loaded:", err.message); // expected in the failure-path test
      DATA_VIEWS.forEach(([sel]) => errorState($(sel), loadSample, "danych"));
      document.body.dataset.sample = "error";
    }
  }

  async function loadTokens() {
    try {
      state.tokens = await getJSON("tokens.json");
    } catch (err) {
      console.info("tokens.json not loaded:", err.message);
      ["[data-directions]", "[data-type-scale]"].forEach((sel) => errorState($(sel), () => location.reload(), "tokenów"));
      return;
    }
    const t = state.tokens;
    renderDirections(t); renderNeutral(t); renderSwatches(); renderData(t); renderTypeScale(t); renderSpaceRadius(t); renderMotion(t);
  }

  function wireControls() {
    document.addEventListener("placechange", (e) => {
      // both toggles drive the same state; keep them in sync
      state.active = new Set(e.detail.active);
      $$("[data-place-toggle] button[data-place]").forEach((b) => b.setAttribute("aria-pressed", String(state.active.has(b.dataset.place))));
      if (state.data) drawLine();
    });
    document.addEventListener("yearchange", (e) => {
      state.year = e.detail.year;
      if (state.data) { drawMap(); drawBars(); }
    });
    $("[data-map-legend-static]").innerHTML = legendMarkup();
    let raf = 0, lastW = 0;
    new ResizeObserver(() => {
      if (!state.data || document.body.clientWidth === lastW) return;
      lastW = document.body.clientWidth;
      cancelAnimationFrame(raf); raf = requestAnimationFrame(drawAll);
    }).observe(document.body);
    $("#line-panel-chart").closest("[data-tabs]").addEventListener("tabchange", () => state.data && drawLine());
    onTheme.push(() => { updateSwatchValues(); updateDataValues(); if (state.data) drawMap(); });
  }

  initSwitcher();
  wireControls();
  Promise.all([loadTokens(), loadSample(), document.fonts.ready]).then(() => { window.__ready = true; });
})();
