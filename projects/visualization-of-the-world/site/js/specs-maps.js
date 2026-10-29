// Map specs: voivodeship choropleth with powiat drill-down, and city bubbles on a Poland outline.
(function () {
  "use strict";
  const V = window.Votw, C = window.VotwCore;
  const GEO_SRC = { label: "GUGiK PRG boundaries (simplified) + synthetic demo values", url: "https://www.geoportal.gov.pl/pl/dane/panstwowy-rejestr-granic-prg/", meta: "values: synthetic demo data; city names: GeoNames CC BY via poland-geography" };
  const CHECK = '<svg class="place-toggle__check" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="m3 8.5 3 3 7-7"/></svg>';
  const placeToggle = (id) => `<fieldset class="place-toggle" data-place-toggle id="${id}"><legend>Place type</legend><div class="place-toggle__options">${C.PLACE_TYPES.filter((k) => k !== "villages").map((k) => `<button type="button" data-place="${k.replace(/_/g, "-")}" aria-pressed="true" style="--swatch:var(--data-place-${k.replace(/_/g, "-")})"><span class="place-toggle__swatch" aria-hidden="true"></span>${C.PLACE_LABEL[k]}${CHECK}</button>`).join("")}</div><p class="field__error" data-place-status aria-live="polite"></p></fieldset>`;
  const regionSelect = (id, feats) => `<div class="field"><label for="${id}">Zoom to region</label><select class="select" id="${id}"><option value="">Whole of Poland</option>${feats.map((f) => `<option value="${f.properties.teryt}">${V.esc(f.properties.name)}</option>`).join("")}</select></div>`;
  const BINS = [20, 30, 40, 50, 60];
  const binColors = () => { const r = V.mapRamp(); return [0, 2, 3, 4, 6].map((i) => r[i]); };
  const noData = () => ({ areaColor: V.cssVar("--color-map-nodata"), borderColor: V.cssVar("--color-map-boundary"), decal: { symbol: "rect", rotation: Math.PI / 4, color: V.cssVar("--color-map-nodata-hatch"), dashArrayX: 1, dashArrayY: [1, 4], symbolSize: 1 } });
  const bboxOf = (feats) => C.bbox(feats);
  const FULL = [14.1, 49.0, 24.2, 54.9];

  const choropleth = {
    id: "choropleth", title: "Villages share by voivodeship, drill down to powiats", className: "span-all",
    subtitle: "Choropleth. Villages, % of population, 2025. Tap or click a voivodeship to open its powiats; drag and pinch or scroll to pan and zoom (synthetic)",
    source: GEO_SRC, height: (w) => (w < 600 ? 420 : 560), merge: false,
    async load() { const [maps, regs, pow] = await Promise.all([V.ensureMaps(), V.data.regions(), V.data.powiats()]); return { maps, regs, pow }; },
    htmlLegend: () => [{ color: V.cssVar("--color-map-nodata"), label: "No data (Opolskie is deliberately missing in this demo)" }],
    csv(d, ctl) {
      if (ctl.extra.level) return { header: ["powiat", "teryt", "villages 2025 (%)"], rows: d.pow.filter((p) => p.voivodeship_teryt === ctl.extra.level).map((p) => [p.name, p.teryt, Number(p.villages)]) };
      return { header: ["voivodeship", "teryt", "villages 2025 (%)"], rows: d.regs.regions.map((r) => [r.name, r.teryt, r.teryt === d.regs.meta.no_data_teryt ? null : r.shares.villages[r.shares.villages.length - 1]]) };
    },
    controls(c, ctl) {
      c.innerHTML = `<div class="crumbs" aria-label="Map level"><button class="btn btn--quiet" type="button" data-root>Poland</button><span data-cur></span></div>${regionSelect("zoom-choro", ctl.data.maps.voiv.features)}<button class="btn btn--secondary" type="button" data-back hidden>Back to Poland</button>`;
      const go = (lvl) => { ctl.extra.level = lvl; ctl.extra.zoom = null; $sel.value = ""; sync(); ctl.render(); };
      const $sel = c.querySelector("select");
      const sync = () => {
        const f = ctl.data.maps.voiv.features.find((x) => x.properties.teryt === ctl.extra.level);
        c.querySelector("[data-cur]").textContent = f ? "› " + C.cap(f.properties.name) : "";
        c.querySelector("[data-back]").hidden = !f; $sel.disabled = !!f;
        ctl.status(f ? `Powiats of ${f.properties.name}. Click "Back to Poland" to return.` : "");
      };
      c.querySelector("[data-root]").addEventListener("click", () => go(null));
      c.querySelector("[data-back]").addEventListener("click", () => go(null));
      $sel.addEventListener("change", () => { ctl.extra.zoom = $sel.value || null; ctl.render(); });
      ctl.drill = go;
    },
    onChart(chart, ctl) { chart.on("click", (p) => { if (!ctl.extra.level && p.componentType === "series" && p.name) ctl.drill(p.name); }); },
    build(d, ctl) {
      const lvl = ctl.extra.level, cols = binColors();
      let data, mapName, nameOf, view = {};
      if (lvl) {
        mapName = "pl-" + lvl;
        const rows = d.pow.filter((p) => p.voivodeship_teryt === lvl);
        data = rows.map((p) => ({ name: p.teryt, value: Number(p.villages) }));
        const nm = Object.fromEntries(rows.map((p) => [p.teryt, p.name])); nameOf = (t) => nm[t] || t;
      } else {
        mapName = "pl";
        const nm = Object.fromEntries(d.regs.regions.map((r) => [r.teryt, r.name])); nameOf = (t) => C.cap(nm[t] || t);
        data = d.regs.regions.map((r) => r.teryt === d.regs.meta.no_data_teryt ? { name: r.teryt, itemStyle: noData() } : { name: r.teryt, value: r.shares.villages[r.shares.villages.length - 1] });
        if (ctl.extra.zoom) { const f = d.maps.voiv.features.filter((x) => x.properties.teryt === ctl.extra.zoom); view = C.zoomTo(bboxOf(f), FULL, 8); }
      }
      return V.base({
        tooltip: V.tooltip({ trigger: "item", formatter: (p) => V.tipRows(nameOf(p.name), [{ color: p.color, label: "Villages 2025", value: p.value === undefined || Number.isNaN(p.value) ? "no data" : V.fmt(p.value) + "%" }]) + (!lvl && p.value !== undefined && !Number.isNaN(p.value) ? '<div style="font-size:12px;opacity:.8;margin-top:4px">Click for powiats</div>' : "") }),
        visualMap: V.visualMapBase({ type: "piecewise", orient: "horizontal", left: 0, bottom: 0, pieces: BINS.map((lo, i) => ({ gte: lo, lt: lo + 10, label: lo + "-" + (lo + 10), color: cols[i] })), itemGap: 6, itemWidth: 12, textGap: 4, textStyle: V.textStyle({ fontSize: 11 }) }),
        series: [Object.assign({ type: "map", map: mapName, nameProperty: "teryt", roam: true, scaleLimit: { min: 1, max: 20 }, top: 8, bottom: 40, data,
          itemStyle: { borderColor: V.cssVar("--color-map-boundary"), borderWidth: lvl ? 0.8 : 1, areaColor: V.cssVar("--color-map-nodata") },
          emphasis: { label: { show: false }, itemStyle: { borderColor: V.cssVar("--color-text-primary"), borderWidth: 2 } }, select: { disabled: true }, label: { show: false }, animationDurationUpdate: V.ms("--dur-slow") }, view)],
      });
    },
  };

  const bubbles = {
    id: "bubbles", title: "City bubbles: area shows a synthetic size index", className: "span-all",
    subtitle: "Bubble map. 1,020 real city locations, bubble area = synthetic size index; filter by place type, tap a bubble for details (synthetic values)",
    source: GEO_SRC, height: (w) => (w < 600 ? 420 : 560),
    async load() { const [maps, rows] = await Promise.all([V.ensureMaps(), V.data.cities()]); const geo = await V.data.citiesGeo(); const by = Object.fromEntries(rows.map((r) => [r.teryt, r])); return { maps, cities: geo.features.map((f) => ({ f, r: by[f.properties.teryt] })).filter((x) => x.r) }; },
    htmlLegend: () => ["big_cities", "small_cities"].map((k) => ({ color: V.placeColor(k), label: C.PLACE_LABEL[k] })).concat([{ color: V.cssVar("--color-chart-axis"), label: "Bubble area = size index (synthetic)" }]),
    csv: (d, ctl) => ({ header: ["city", "teryt", "place type", "size index"], rows: d.cities.filter((x) => (ctl.extra.active || ["big_cities", "small_cities"]).includes(x.r.place_type)).map((x) => [x.r.name, x.r.teryt, C.PLACE_LABEL[x.r.place_type], Number(x.r.size_index)]) }),
    onReset(ctl) { ctl.extra.active = ["big_cities", "small_cities"]; ctl.el.querySelectorAll("[data-place]").forEach((b) => b.setAttribute("aria-pressed", "true")); ctl.render(); },
    controls(c, ctl) {
      c.innerHTML = placeToggle("place-bubbles") + regionSelect("zoom-bub", ctl.data.maps.voiv.features);
      c.querySelector("[data-place-toggle]").addEventListener("placechange", (e) => { ctl.extra.active = e.detail.active.map((k) => k.replace(/-/g, "_")); ctl.render(); });
      c.querySelector("select").addEventListener("change", (e) => { ctl.extra.zoom = e.target.value || null; ctl.render(); });
    },
    build(d, ctl) {
      const active = ctl.extra.active || ["big_cities", "small_cities"];
      const pts = d.cities.filter((x) => active.includes(x.r.place_type));
      let view = { zoom: 1 };
      if (ctl.extra.zoom) { const f = d.maps.voiv.features.filter((x) => x.properties.teryt === ctl.extra.zoom); view = C.zoomTo(bboxOf(f), FULL, 8); }
      const series = ["small_cities", "big_cities"].filter((k) => active.includes(k)).map((k) => ({
        name: C.PLACE_LABEL[k], type: "scatter", coordinateSystem: "geo", color: V.placeColor(k),
        data: pts.filter((x) => x.r.place_type === k).map((x) => ({ name: x.r.name, value: [...x.f.geometry.coordinates, Number(x.r.size_index), x.r.place_type] })),
        symbolSize: (v) => Math.sqrt(v[2]) * 1.1 + 3, itemStyle: { color: V.placeColor(k), opacity: 0.75, borderColor: V.cssVar("--color-bg-surface"), borderWidth: 0.8 }, emphasis: { itemStyle: { opacity: 1, borderColor: V.cssVar("--color-text-primary"), borderWidth: 2 } },
      }));
      if (!series.length) return "empty";
      return V.base({
        tooltip: V.tooltip({ trigger: "item", formatter: (p) => V.tipRows(p.name, [{ color: p.color, label: C.PLACE_LABEL[p.value[3]], value: "" }, { color: p.color, label: "Size index", value: V.fmt(p.value[2]) }]) }),
        geo: Object.assign({ map: "pl", nameProperty: "teryt", roam: true, scaleLimit: { min: 1, max: 20 }, silent: false, itemStyle: { areaColor: V.cssVar("--color-bg-sunken"), borderColor: V.cssVar("--color-border-strong"), borderWidth: 0.8 }, emphasis: { disabled: true }, select: { disabled: true }, label: { show: false } }, view),
        series,
      });
    },
  };
  window.SpecsMaps = [choropleth, bubbles];
})();
