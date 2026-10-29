// Formats: the same villages-share numbers loaded from CSV and JSON, the same boundaries from GeoJSON and TopoJSON.
(function () {
  "use strict";
  const V = window.Votw, C = window.VotwCore;
  const mk = (fmt, file) => ({ label: `Synthetic demo data, ${file}`, url: file, meta: `loaded as ${fmt}` });
  const last = (a) => a[a.length - 1];
  const bars = (id, fmt, file, loadFn) => ({
    id, title: `Bars from ${fmt}`, className: "span-all lg-span-6", height: 400, source: mk(fmt, file),
    subtitle: `Villages, % of population, 2025, read from ${file} with ${fmt === "CSV" ? "the built-in CSV parser (VotwCore.parseCsv)" : "JSON.parse"} (synthetic)`,
    load: loadFn, csv: (d) => ({ header: ["voivodeship", "villages 2025 (%)"], rows: d.map((r) => [r.name, r.v]) }),
    build(d) {
      const rows = d.slice().sort((a, b) => b.v - a.v);
      return V.base({ grid: V.grid({ top: 8, right: 36 }), tooltip: V.tooltip({ trigger: "item", formatter: (p) => V.tipRows(C.cap(p.name), [{ color: p.color, label: "Villages 2025", value: V.fmt(p.value) + "%" }]) }),
        xAxis: V.valueAxis({ axisLabel: Object.assign(V.textStyle(), { formatter: "{value}%" }) }), yAxis: V.catAxis(rows.map((r) => r.name), { inverse: true, axisLabel: Object.assign(V.textStyle({ fontSize: 11 }), { interval: 0 }), axisLine: { show: false }, axisTick: { show: false } }),
        series: [{ type: "bar", data: rows.map((r) => ({ name: r.name, value: r.v })), barMaxWidth: 16, itemStyle: { color: V.placeColor("villages"), borderRadius: [0, 4, 4, 0] }, label: { show: true, position: "right", color: V.cssVar("--color-text-primary"), fontSize: 11 } }] });
    } });
  const fromCsv = async () => { const { regions } = C.regionsFromCsv(C.parseCsv(await (await fetch("data/demo-regions.csv")).text())); return regions.map((r) => ({ teryt: r.teryt, name: r.name, v: last(r.shares.villages) })); };
  const fromJson = async () => { const j = await (await fetch("data/demo.json")).json(); return j.regions.map((r) => ({ teryt: r.teryt, name: r.name, v: last(r.shares.villages) })); };
  const choro = (id, fmt, file, mapLoader) => ({
    id, title: `Map from ${fmt}`, className: "span-all lg-span-6", height: 400, source: { label: `GUGiK PRG boundaries (simplified), ${file}`, url: file, meta: `loaded as ${fmt}; values: synthetic demo CSV` },
    subtitle: `Boundaries read from ${file}${fmt === "TopoJSON" ? " and converted with topojson-client 3.1.0" : " directly"}; values from the CSV above (synthetic)`,
    async load() { const [name, rows] = await Promise.all([mapLoader(), fromCsv()]); return { name, rows }; },
    csv: (d) => ({ header: ["voivodeship", "teryt", "villages 2025 (%)"], rows: d.rows.map((r) => [r.name, r.teryt, r.v]) }),
    build(d) {
      const r = V.mapRamp(), cols = [0, 2, 3, 4, 6].map((i) => r[i]), nm = Object.fromEntries(d.rows.map((x) => [x.teryt, x.name]));
      return V.base({ tooltip: V.tooltip({ trigger: "item", formatter: (p) => V.tipRows(C.cap(nm[p.name] || p.name), [{ color: p.color, label: "Villages 2025", value: V.fmt(p.value) + "%" }]) }),
        visualMap: V.visualMapBase({ type: "piecewise", orient: "horizontal", left: 0, bottom: 0, pieces: [20, 30, 40, 50, 60].map((lo, i) => ({ gte: lo, lt: lo + 10, label: lo + "-" + (lo + 10), color: cols[i] })), itemGap: 6, itemWidth: 12, textGap: 4, textStyle: V.textStyle({ fontSize: 11 }) }),
        series: [{ type: "map", map: d.name, nameProperty: "teryt", roam: true, top: 4, bottom: 40, data: d.rows.map((x) => ({ name: x.teryt, value: x.v })), itemStyle: { borderColor: V.cssVar("--color-map-boundary"), borderWidth: 1 }, emphasis: { label: { show: false }, itemStyle: { borderColor: V.cssVar("--color-text-primary"), borderWidth: 2 } }, label: { show: false } }] });
    } });
  const geoJsonLoader = async () => { const g = await V.data.voivGeo(); if (!echarts.getMap("pl-geojson")) echarts.registerMap("pl-geojson", g); return "pl-geojson"; };
  const topoLoader = async () => { await V.ensureMaps(); return "pl"; };
  window.SpecsFormats = [bars("fmt-csv", "CSV", "data/demo-regions.csv", fromCsv), bars("fmt-json", "JSON", "data/demo.json", fromJson), choro("fmt-geojson", "GeoJSON", "data/geo/voivodeships.geojson", geoJsonLoader), choro("fmt-topojson", "TopoJSON", "data/geo/voivodeships.topojson", topoLoader)];
  // Cross-check shown on the page: do the formats agree?
  window.formatsCompare = async () => {
    const [a, b, g, t] = await Promise.all([fromCsv(), fromJson(), V.data.voivGeo(), V.data.voivTopo()]);
    const tf = V.topoFeatures(t, "voivodeships").features;
    const sameVals = a.length === b.length && a.every((x, i) => x.teryt === b[i].teryt && x.v === b[i].v);
    const sameGeo = g.features.length === tf.length && g.features.every((f) => tf.some((h) => h.properties.teryt === f.properties.teryt && h.properties.name === f.properties.name));
    return { sameVals, sameGeo, n: a.length, nGeo: g.features.length };
  };
})();
