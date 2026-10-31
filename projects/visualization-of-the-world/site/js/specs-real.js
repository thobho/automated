// Real-data specs for real.html. Every number comes from site/data/real/*.csv, verbatim copies of
// research/poland-demography-housing/data/processed/. All specs are `real: true`: REAL DATA badge,
// no DEMO wording in the aria-label/footer, and CSV exports carry a source_id column.
// Proxy years (2000-2008) and direct years (2009-2025) are never drawn as one unlabelled line.
(function () {
  "use strict";
  const V = window.Votw, C = window.VotwCore;
  const P = C.PLACE_TYPES, L = C.PLACE_LABEL;
  const ACCESSED = "2026-10-29";

  // Source ids and the GUS/Eurostat variables exactly as registered in research/poland-demography-housing/sources.csv.
  const SRC = {
    housingVsPop: {
      label: "GUS BDL var 748601/748247/430 completions per 1000 residents, population var 60641 (S41;S42;S43;S1)",
      url: "https://bdl.stat.gov.pl/api/v1/data/by-variable/748601?unit-level=6&year=2025",
      meta: "flats = total minus individual construction; houses = individual construction; 2000-2008 split is proxy, 2009-2025 direct",
      ids: "S41;S42;S43;S1", accessed: ACCESSED,
    },
    directSplit: {
      label: "GUS BDL var 748247 single-/multi-family dwellings, var 748601 total (S41;S43)",
      url: "https://bdl.stat.gov.pl/api/v1/data/by-variable/748247?unit-level=6&year=2025",
      meta: "direct basis only, 2009-2025; houses = single-family, flats = multi-family, other = remaining completed dwellings",
      ids: "S41;S43", accessed: ACCESSED,
    },
    europe: {
      label: "Eurostat demo_gind, population 1 Jan, index 2000 = 100 (S29)",
      url: "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_gind?geo=PL&geo=CZ&geo=SK&geo=HU&geo=DE&geo=RO&geo=LT&geo=EU27_2020&indic_de=JAN&sinceTimePeriod=2000",
      meta: "PL, CZ, SK, HU, DE, RO, LT, EU-27; Eurostat reference date 1 January",
      ids: "S29", accessed: ACCESSED,
    },
    cities: {
      label: "GUS BDL var 60641, population of the 34 big cities, 31 Dec 2025 (S1)",
      url: "https://bdl.stat.gov.pl/api/v1/data/by-variable/60641?unit-level=6&year=2025",
      meta: "city points and boundaries: GUGiK PRG / GeoNames via poland-geography (already real); no synthetic value is added",
      ids: "S1", accessed: ACCESSED,
    },
  };

  const PLACES = P;
  const yearsOf = (years) => years.map(String);
  const ixOf = (years, y) => years.indexOf(y);
  const axisInterval = (w) => (w < 600 ? 7 : 4);
  const yAxisPct = (extra) => V.valueAxis(Object.assign({ axisLabel: Object.assign(V.textStyle(), { formatter: "{value}%" }) }, extra));
  const axisTip = (unit) => (ps) => {
    const arr = Array.isArray(ps) ? ps : [ps];
    return V.tipRows(arr[0].axisValueLabel || arr[0].name, arr.map((p) => ({ color: p.color, label: p.seriesName, value: V.fmt(Array.isArray(p.value) ? p.value[1] : p.value, 1) + (unit || "") })));
  };
  const line = (name, data, color, extra) => Object.assign({ name, type: "line", data, symbol: "none", showSymbol: false, lineStyle: { width: 2, color }, itemStyle: { color }, emphasis: { focus: "series" } }, extra);

  // Annotated "proxy basis" band on a category axis. The hatch itself is a custom series (see hatchSeries);
  // this keeps the label and, when fill is on, a dashed outline. Proxy years are never silently mixed in.
  function proxyBand(label, from, to, opts) {
    const o = opts || {};
    return {
      silent: true,
      itemStyle: o.fill === false
        ? { color: "transparent" }
        : { color: V.cssVar("--color-map-nodata-hatch"), opacity: 0.3, borderColor: V.cssVar("--color-chart-annotation"), borderWidth: 1, borderType: "dashed" },
      label: { show: true, position: "insideTop", distance: 6, color: V.cssVar("--color-text-primary"), fontSize: 11, fontWeight: 600, formatter: label },
      data: [[{ xAxis: String(from) }, { xAxis: String(to) }]],
    };
  }
  // Real hatch inside the 2000-2008 band (custom series), plus a markArea label. Decals are not reliably
  // painted on markArea in every renderer, so the diagonals are drawn explicitly and clipped to the band.
  function hatchSeries(fromIdx, toIdx) {
    return {
      type: "custom", silent: true, z: 0, name: "proxy band", data: [[fromIdx, toIdx]],
      renderItem(params, api) {
        const x0 = api.coord([fromIdx, 0])[0], x1 = api.coord([toIdx, 0])[0];
        const cs = params.coordSys, yTop = cs.y, yBot = cs.y + cs.height, H = yBot - yTop;
        const kids = [{ type: "rect", shape: { x: x0, y: yTop, width: x1 - x0, height: H }, style: { fill: V.cssVar("--color-map-nodata-hatch"), opacity: 0.18 } }];
        for (let s = x0 - H; s < x1; s += 9) {
          const xs = Math.max(x0, s), xe = Math.min(x1, s + H);
          if (xe - xs < 1) continue;
          kids.push({ type: "line", shape: { x1: xs, y1: yBot - (xs - s), x2: xe, y2: yBot - (xe - s) }, style: { stroke: V.cssVar("--color-chart-annotation"), lineWidth: 1, opacity: 0.22 } });
        }
        kids.push({ type: "rect", shape: { x: x0, y: yTop, width: x1 - x0, height: H }, style: { fill: "none", stroke: V.cssVar("--color-chart-annotation"), lineWidth: 1, opacity: 0.55, lineDash: [4, 4] } });
        return { type: "group", children: kids };
      },
    };
  }

  const basisSourceIds = (meta, i) => Array.from(new Set(PLACES.map((k) => meta[k + "|flats_per_1000"].source_id[i]).filter(Boolean))).join(";");

  const specs = [
    {
      id: "real-indexed", real: true, className: "span-all",
      title: "Big cities lose people while villages’ housing output rises fastest",
      subtitle: "Indexed line chart. Population (solid, 31 Dec, S1) and dwellings completed (dashed, all forms, S41), 2000 = 100, by place class, 2000-2025. Completions are the direct reported total in every year; the houses/flats split is not used here.",
      source: {
        label: "GUS BDL var 60641 (S1) and var 748601 (S41)",
        url: "https://bdl.stat.gov.pl/api/v1/data/by-variable/60641?unit-level=0&year=2025&format=json",
        meta: "population 31 Dec, completions total; big cities = 34 gminas",
        ids: "S1;S41", accessed: ACCESSED,
      },
      height: (w) => (w < 600 ? 380 : 400),
      load: async () => ({ population: await V.data.realPopulation(), completions: await V.data.realCompletions() }),
      htmlLegend: () => PLACES.map((k) => ({ color: V.placeColor(k), label: L[k] + " (solid = population, dashed = completed dwellings)" })),
      csv(d) {
        const pop = C.populationByClass(d.population), comp = C.completionsByClass(d.completions);
        const p0 = ixOf(pop.years, 2000), c0 = ixOf(comp.years, 2000);
        return {
          header: ["year", ...PLACES.map((k) => L[k] + " population, 2000=100"), ...PLACES.map((k) => L[k] + " dwellings, 2000=100")],
          rows: pop.years.map((y, i) => [y, ...PLACES.map((k) => C.indexSeries(pop.values[k], p0)[i]), ...PLACES.map((k) => C.indexSeries(comp.values[k + "|total"], c0)[i])]),
          sourceId: "S1;S41",
        };
      },
      build(d) {
        const pop = C.populationByClass(d.population), comp = C.completionsByClass(d.completions);
        const p0 = ixOf(pop.years, 2000), c0 = ixOf(comp.years, 2000);
        const series = PLACES.map((k) => line(L[k] + " population", C.indexSeries(pop.values[k], p0), V.placeColor(k), { lineStyle: { width: 2.4, color: V.placeColor(k) } }))
          .concat(PLACES.map((k) => line(L[k] + " dwellings", C.indexSeries(comp.values[k + "|total"], c0), V.placeColor(k), { lineStyle: { width: 2, color: V.placeColor(k), type: "dashed" } })));
        return V.base({
          legend: V.legend({ top: 0, itemGap: 10 }),
          grid: V.grid({ top: 62, right: 24 }),
          tooltip: V.tooltip({ formatter: axisTip("") }),
          xAxis: V.catAxis(yearsOf(pop.years), { boundaryGap: false, axisLabel: Object.assign(V.textStyle(), { interval: axisInterval(window.innerWidth) }) }),
          yAxis: V.valueAxis({ scale: true, name: "2000 = 100", nameLocation: "end", nameGap: 12 }),
          series,
        });
      },
    },
    {
      id: "real-housing-vs-pop", real: true, className: "span-all lg-span-6",
      title: "Housing per 1000 residents: flats still win in cities, houses in villages",
      subtitle: "Line chart. Dwellings completed per 1000 residents, flats (solid) and houses (dashed), by place class, 2000-2025. Shaded 2000-2008 = proxy basis (individual construction vs the rest); 2009-2025 = direct single-/multi-family series. The two bases are split by the band and never drawn as one silent series.",
      source: SRC.housingVsPop,
      height: (w) => (w < 600 ? 400 : 420),
      load: () => V.data.realHousingVsPop(),
      htmlLegend: () => PLACES.map((k) => ({ color: V.placeColor(k), label: L[k] + " (solid = flats, dashed = houses)" })).concat([{ color: V.cssVar("--color-map-nodata-hatch"), label: "2000-2008: proxy basis (S41;S42)" }]),
      csv(d) {
        const f = C.housingVsPopulation(d, "flats_per_1000"), h = C.housingVsPopulation(d, "houses_per_1000");
        return {
          header: ["year", ...PLACES.map((k) => L[k] + " flats per 1000"), ...PLACES.map((k) => L[k] + " houses per 1000"), "basis"],
          rows: f.years.map((y, i) => [y, ...PLACES.map((k) => f.values[k + "|flats_per_1000"][i]), ...PLACES.map((k) => h.values[k + "|houses_per_1000"][i]), y <= 2008 ? "proxy" : "direct"]),
          sourceId: (r, i) => basisSourceIds(f.meta, i),
        };
      },
      build(d) {
        const f = C.housingVsPopulation(d, "flats_per_1000"), h = C.housingVsPopulation(d, "houses_per_1000");
        const series = PLACES.map((k) => line(L[k] + " flats", f.values[k + "|flats_per_1000"], V.placeColor(k), { lineStyle: { width: 2.2, color: V.placeColor(k) } }))
          .concat(PLACES.map((k) => line(L[k] + " houses", h.values[k + "|houses_per_1000"], V.placeColor(k), { lineStyle: { width: 2, color: V.placeColor(k), type: "dashed" } })));
        const i2000 = f.years.indexOf(2000), i2008 = f.years.indexOf(2008);
        series[0].markArea = proxyBand("proxy basis 2000-2008", 2000, 2008, { fill: false });
        series.push(hatchSeries(i2000, i2008));
        return V.base({
          legend: V.legend({ top: 0, itemGap: 10, data: series.filter((x) => x.type === "line").map((x) => x.name) }),
          grid: V.grid({ top: 62, right: 24 }),
          tooltip: V.tooltip({ formatter: (ps) => {
            const arr = Array.isArray(ps) ? ps : [ps];
            const y = +arr[0].axisValueLabel;
            return V.tipRows(arr[0].axisValueLabel + (y <= 2008 ? " · proxy basis (S41;S42)" : " · direct (S43)"), arr.map((p) => ({ color: p.color, label: p.seriesName, value: V.fmt(p.value, 2) + " per 1000" })));
          } }),
          xAxis: V.catAxis(yearsOf(f.years), { boundaryGap: false, axisLabel: Object.assign(V.textStyle(), { interval: axisInterval(window.innerWidth) }) }),
          yAxis: V.valueAxis({ scale: true }),
          series,
        });
      },
    },
    {
      id: "real-houses-flats", real: true, className: "span-all lg-span-6",
      title: "Houses are nearly half of new homes nationally",
      subtitle: "100% stacked bar. Share of dwellings completed by building type, %, national total of the three place classes, 2009-2025 (the class split is in the KPI cards). DIRECT basis only (GUS var 748247 houses/flats, var 748601 total): the 2000-2008 proxy split is excluded on purpose.",
      source: SRC.directSplit,
      height: (w) => (w < 600 ? 360 : 400),
      load: () => V.data.realCompletions(),
      htmlLegend: () => [{ color: V.catColors()[0], label: "Flats (multi-family)" }, { color: V.catColors()[1], label: "Houses (single-family)" }, { color: V.catColors()[2], label: "Other completed dwellings" }, { color: V.cssVar("--color-chart-annotation"), label: "Direct basis only, 2009-2025 (S41;S43)" }],
      csv(d) {
        const comp = C.completionsByClass(d);
        const pick = (type) => C.sumSeries(PLACES.map((k) => comp.values[k + "|" + type]).filter(Boolean));
        const houses = pick("house"), flats = pick("flat"), other = pick("other");
        const total = C.sumSeries([houses, flats, other]);
        const hs = C.percentShare(houses, total), fs = C.percentShare(flats, total), os = C.percentShare(other, total);
        return {
          header: ["year", "houses (%)", "flats (%)", "other (%)", "houses (dwellings)", "flats (dwellings)", "other (dwellings)"],
          rows: comp.years.map((y, i) => [y, hs[i], fs[i], os[i], houses[i], flats[i], other[i]]),
          sourceId: "S41;S43",
        };
      },
      build(d) {
        const comp = C.completionsByClass(d);
        const pick = (type) => C.sumSeries(PLACES.map((k) => comp.values[k + "|" + type]).filter(Boolean));
        const houses = pick("house"), flats = pick("flat"), other = pick("other");
        const total = C.sumSeries([houses, flats, other]);
        const hs = C.percentShare(houses, total), fs = C.percentShare(flats, total), os = C.percentShare(other, total);
        const cols = V.catColors();
        const defs = [{ name: "Flats", s: fs, c: cols[0] }, { name: "Houses", s: hs, c: cols[1] }, { name: "Other", s: os, c: cols[2] }];
        return V.base({
          legend: V.legend({ top: 0 }),
          grid: V.grid({ top: 62 }),
          tooltip: V.tooltip({ axisPointer: { type: "shadow" }, formatter: (ps) => V.tipRows(ps[0].axisValueLabel + " · direct basis", ps.map((p) => ({ color: p.color, label: p.seriesName, value: V.fmt(p.value, 1) + "%" }))) }),
          xAxis: V.catAxis(yearsOf(comp.years), { axisLabel: Object.assign(V.textStyle(), { interval: 0, rotate: window.innerWidth < 600 ? 60 : 0 }) }),
          yAxis: yAxisPct({ max: 100 }),
          series: defs.map((s, j) => ({ name: s.name, type: "bar", stack: "basis", barMaxWidth: 28, data: s.s, color: s.c, itemStyle: { color: s.c, borderColor: V.cssVar("--color-chart-surface"), borderWidth: 1, borderRadius: j === 2 ? [4, 4, 0, 0] : 0 }, emphasis: { focus: "series" } })),
        });
      },
    },
    {
      id: "real-europe", real: true, className: "span-all lg-span-6",
      title: "Poland shrinks while most neighbours grow",
      subtitle: "Line chart. Population index, 1 Jan 2000 = 100, Poland against CZ, SK, HU, DE, RO, LT and EU-27, 2000-2025 (Eurostat demo_gind).",
      source: SRC.europe,
      height: (w) => (w < 600 ? 380 : 400),
      load: () => V.data.realEurope(),
      htmlLegend: () => [{ color: V.cssVar("--color-text-primary"), label: "Poland" }, { color: V.catColors()[0], label: "Czechia, Slovakia, Hungary, Germany, Romania, Lithuania" }, { color: V.cssVar("--color-text-muted"), label: "EU-27 (dashed)" }],
      csv(d) {
        const e = C.europeByGeo(d, "population_index_2000_eq_100", "total");
        const order = ["PL", "CZ", "SK", "HU", "DE", "RO", "LT", "EU27_2020"];
        return { header: ["year", ...order.map((g) => (e.meta[g] ? e.meta[g].geo_name[0] : g))], rows: e.years.map((y, i) => [y, ...order.map((g) => (e.values[g] ? e.values[g][i] : null))]), sourceId: "S29" };
      },
      build(d) {
        const e = C.europeByGeo(d, "population_index_2000_eq_100", "total");
        const order = ["PL", "CZ", "SK", "HU", "DE", "RO", "LT", "EU27_2020"];
        const cats = V.catColors();
        const series = order.filter((g) => e.values[g]).map((g, j) => {
          const minor = j > 3 && g !== "EU27_2020";
          const color = g === "PL" ? V.cssVar("--color-text-primary") : g === "EU27_2020" ? V.cssVar("--color-text-muted") : cats[j - 1];
          return line(e.meta[g].geo_name[0], e.values[g], color, {
            lineStyle: { width: g === "PL" ? 3 : minor ? 1.4 : 2, color, type: g === "EU27_2020" ? "dashed" : "solid" },
            z: g === "PL" ? 5 : 2,
          });
        });
        return V.base({
          legend: V.legend({ top: 0, itemGap: 10 }),
          grid: V.grid({ top: 62, right: 24 }),
          tooltip: V.tooltip({ formatter: axisTip("") }),
          xAxis: V.catAxis(yearsOf(e.years), { boundaryGap: false, axisLabel: Object.assign(V.textStyle(), { interval: axisInterval(window.innerWidth) }) }),
          yAxis: V.valueAxis({ scale: true, name: "2000 = 100", nameLocation: "end", nameGap: 12 }),
          series,
        });
      },
    },
    {
      id: "real-cities-map", real: true, className: "span-all lg-span-6",
      title: "The 34 big cities, sized by their real population",
      subtitle: "Bubble map. Bubble area = population, 31 Dec 2025 (S1); real city points and voivodeship boundaries. No voivodeship or powiat indicator is drawn: the research series publishes population by place class, not per region, so no value is invented.",
      source: SRC.cities,
      height: (w) => (w < 600 ? 420 : 520),
      async load() {
        const [rows, geo, maps] = await Promise.all([V.data.realBigCities(), V.data.citiesGeo(), V.ensureMaps()]);
        const by = Object.fromEntries(geo.features.map((f) => [f.properties.name, f]));
        const cities = C.bigCities(rows).map((c) => ({ ...c, feature: by[c.city] || null })).filter((c) => c.feature);
        return { cities, maps };
      },
      htmlLegend: () => [{ color: V.placeColor("big_cities"), label: "34 big cities, bubble area = population 2025 (S1)" }, { color: V.cssVar("--color-border-strong"), label: "Voivodeship boundaries (GUGiK PRG), no fill values" }],
      csv: (d) => ({
        header: ["city", "unit_id", "lon", "lat", "population 2025"],
        rows: d.cities.map((c) => [c.city, c.unit_id, c.feature.geometry.coordinates[0], c.feature.geometry.coordinates[1], c.population]),
        sourceId: (r) => (d.cities.find((c) => c.city === r[0]) || {}).source_id || "S1",
      }),
      build(d) {
        const max = Math.max(...d.cities.map((c) => c.population));
        return V.base({
          tooltip: V.tooltip({ trigger: "item", formatter: (p) => V.tipRows(p.name, [{ color: p.color, label: "Population 2025", value: V.fmt(p.value[2]) }, { color: p.color, label: "Source", value: "S1" }]) }),
          geo: { map: "pl", nameProperty: "teryt", roam: true, scaleLimit: { min: 1, max: 20 }, silent: false, itemStyle: { areaColor: V.cssVar("--color-bg-sunken"), borderColor: V.cssVar("--color-border-strong"), borderWidth: 0.8 }, emphasis: { disabled: true }, select: { disabled: true }, label: { show: false } },
          series: [{
            name: "Big cities", type: "scatter", coordinateSystem: "geo", color: V.placeColor("big_cities"),
            data: d.cities.map((c) => ({ name: c.city, value: [...c.feature.geometry.coordinates, c.population], unit_id: c.unit_id })),
            symbolSize: (v) => Math.max(5, (Math.sqrt(v[2]) / Math.sqrt(max)) * 30),
            itemStyle: { color: V.placeColor("big_cities"), opacity: 0.72, borderColor: V.cssVar("--color-bg-surface"), borderWidth: 0.9 },
            emphasis: { itemStyle: { opacity: 1, borderColor: V.cssVar("--color-text-primary"), borderWidth: 2 } },
            label: { show: false },
          }],
        });
      },
    },
  ];
  window.SpecsReal = specs;
})();
