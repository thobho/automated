// Chart catalogue specs. Each spec = { id, title, subtitle, source, load, build, csv, ... } consumed by Votw.figure.
(function () {
  "use strict";
  const V = window.Votw, C = window.VotwCore;
  const S = V.DEMO_SOURCE;
  const P = C.PLACE_TYPES, L = C.PLACE_LABEL;
  const load = () => V.data.regions();
  const yearsOf = (d) => d.years.map(String);
  const avg = (d, k) => d.years.map((_, i) => Math.round((d.regions.reduce((a, r) => a + r.shares[k][i], 0) / d.regions.length) * 10) / 10);
  const last = (a) => a[a.length - 1];
  const short = (n) => C.cap(n);
  const regionCsv = (d, ks) => ({ header: ["year", ...ks.map((k) => L[k] + " (%)")], rows: d.years.map((y, i) => [y, ...ks.map((k) => avg(d, k)[i])]) });
  const yAxisPct = (extra) => V.valueAxis(Object.assign({ axisLabel: Object.assign(V.textStyle(), { formatter: "{value}%" }) }, extra));
  const axisTip = (unit) => (ps) => {
    const arr = Array.isArray(ps) ? ps : [ps];
    return V.tipRows(arr[0].axisValueLabel || arr[0].name, arr.map((p) => ({ color: p.color, label: p.seriesName, value: V.fmt(Array.isArray(p.value) ? p.value[1] : p.value, 1) + (unit || "") })));
  };
  const lineSeries = (name, data, color, extra) => Object.assign({ name, type: "line", data, symbol: "none", showSymbol: false, lineStyle: { width: 2, color }, itemStyle: { color }, emphasis: { focus: "series" }, endLabel: { show: true, formatter: "{a}", color: V.cssVar("--color-text-primary"), fontWeight: 600, fontSize: 12 } }, extra);
  const placeLegendHtml = () => P.map((k) => ({ color: V.placeColor(k), label: L[k] }));
  const pick = (d, names) => names.map((n) => d.regions.find((r) => r.name === n));
  const SIX = ["mazowieckie", "małopolskie", "śląskie", "wielkopolskie", "pomorskie", "podkarpackie"];

  const specs = [
    { id: "line", title: "Villages gain share while big cities lose it", subtitle: "Line chart. Share of population by place type, %, 2000-2025 (synthetic national average)",
      source: S, load, csv: regionCsv.bind(null), build(d) {
        return V.base({ legend: V.legend(), grid: V.grid({ right: 96 }), tooltip: V.tooltip({ formatter: axisTip("%") }),
          xAxis: V.catAxis(yearsOf(d), { boundaryGap: false, axisLabel: Object.assign(V.textStyle(), { interval: window.innerWidth < 600 ? 7 : 4 }) }), yAxis: yAxisPct({ min: 20, max: 50 }),
          series: P.map((k) => lineSeries(L[k], avg(d, k), V.placeColor(k))) });
      } },
    { id: "area", title: "Stacked area: three shares always add up to 100%", subtitle: "Area chart. Share of population by place type, %, 2000-2025 (synthetic)",
      source: S, load, csv: (d) => regionCsv(d, P), build(d) {
        return V.base({ legend: V.legend(), grid: V.grid(), tooltip: V.tooltip({ formatter: axisTip("%") }),
          xAxis: V.catAxis(yearsOf(d), { boundaryGap: false, axisLabel: Object.assign(V.textStyle(), { interval: window.innerWidth < 600 ? 7 : 4 }) }), yAxis: yAxisPct({ max: 100 }),
          series: P.map((k) => ({ name: L[k], type: "line", stack: "all", areaStyle: { opacity: 0.85 }, symbol: "none", lineStyle: { width: 1, color: V.cssVar("--color-chart-surface") }, itemStyle: { color: V.placeColor(k) }, color: V.placeColor(k), emphasis: { focus: "series" }, data: avg(d, k) })) });
      } },
    { id: "stacked-bar", title: "Stacked bars compare the mix at five moments", subtitle: "Stacked bar. Share of population by place type, %, selected years (synthetic)",
      source: S, load, csv: (d) => { const ix = [0, 5, 10, 15, 20, 25]; return { header: ["year", ...P.map((k) => L[k] + " (%)")], rows: ix.map((i) => [d.years[i], ...P.map((k) => avg(d, k)[i])]) }; },
      build(d) {
        const ix = [0, 5, 10, 15, 20, 25];
        return V.base({ legend: V.legend(), grid: V.grid(), tooltip: V.tooltip({ formatter: axisTip("%"), axisPointer: { type: "shadow" } }),
          xAxis: V.catAxis(ix.map((i) => String(d.years[i]))), yAxis: yAxisPct({ max: 100 }),
          series: P.map((k, j) => ({ name: L[k], type: "bar", stack: "s", barMaxWidth: 56, data: ix.map((i) => avg(d, k)[i]), color: V.placeColor(k), itemStyle: { color: V.placeColor(k), borderColor: V.cssVar("--color-chart-surface"), borderWidth: 1, borderRadius: j === 2 ? [4, 4, 0, 0] : 0 }, emphasis: { focus: "series" } })) });
      } },
    { id: "grouped-bar", title: "Grouped bars: villages share in six voivodeships", subtitle: "Grouped bar. Villages, % of population, three years (synthetic)",
      source: S, load, csv: (d) => ({ header: ["voivodeship", "2000", "2012", "2025"], rows: pick(d, SIX).map((r) => [r.name, r.shares.villages[0], r.shares.villages[12], last(r.shares.villages)]) }),
      build(d) {
        const rs = pick(d, SIX), ix = [0, 12, 25];
        return V.base({ legend: V.legend(), grid: V.grid({ bottom: 8 }), tooltip: V.tooltip({ formatter: axisTip("%"), axisPointer: { type: "shadow" } }),
          xAxis: V.catAxis(rs.map((r) => r.name), { axisLabel: Object.assign(V.textStyle(), { interval: 0, rotate: window.innerWidth < 600 ? 40 : 0 }) }), yAxis: yAxisPct(),
          series: ix.map((i, j) => ({ name: String(d.years[i]), type: "bar", barMaxWidth: 28, color: V.catColors()[j], itemStyle: { color: V.catColors()[j], borderRadius: [4, 4, 0, 0] }, data: rs.map((r) => r.shares.villages[i]), emphasis: { focus: "series" } })) });
      }, height: (w) => (w < 600 ? 380 : 340) },
    { id: "scatter", title: "Scatter: where villages started high they grew less", subtitle: "Scatter plot. Villages share in 2000 (x, %) against change to 2025 (y, percentage points); one dot per voivodeship (synthetic)",
      source: S, load, csv: (d) => ({ header: ["voivodeship", "villages 2000 (%)", "change 2000-2025 (pp)"], rows: d.regions.map((r) => [r.name, r.shares.villages[0], Math.round((last(r.shares.villages) - r.shares.villages[0]) * 10) / 10]) }),
      build(d) {
        const pts = d.regions.map((r) => ({ name: r.name, value: [r.shares.villages[0], Math.round((last(r.shares.villages) - r.shares.villages[0]) * 10) / 10] }));
        return V.base({ legend: V.legend({ show: false }), grid: V.grid({ top: 24, bottom: 28 }),
          tooltip: V.tooltip({ trigger: "item", formatter: (p) => V.tipRows(p.name, [{ color: V.placeColor("villages"), label: "Villages 2000", value: V.fmt(p.value[0]) + "%" }, { color: V.placeColor("villages"), label: "Change", value: V.fmt(p.value[1]) + " pp" }]) }),
          xAxis: V.valueAxis({ name: "Villages 2000, %", nameLocation: "middle", nameGap: 28, splitLine: { show: false }, min: "dataMin", scale: true, axisLine: { show: true, lineStyle: { color: V.cssVar("--color-chart-axis") } } }),
          yAxis: V.valueAxis({ name: "pp", scale: true }),
          series: [{ name: "Voivodeships", type: "scatter", symbolSize: 12, data: pts, itemStyle: { color: V.placeColor("villages"), borderColor: V.cssVar("--color-chart-surface"), borderWidth: 1.5 }, emphasis: { scale: 1.5 } }] });
      }, height: 340 },
    { id: "bubble", title: "Bubble: a third variable as area", subtitle: "Bubble chart. Big cities share (x, %) against villages share (y, %) in 2025; bubble area = synthetic weight index (synthetic)",
      source: S, load, csv: (d) => ({ header: ["voivodeship", "big cities 2025 (%)", "villages 2025 (%)", "weight index"], rows: d.regions.map((r) => [r.name, last(r.shares.big_cities), last(r.shares.villages), r.weight_index]) }),
      build(d) {
        const pts = d.regions.map((r) => ({ name: r.name, value: [last(r.shares.big_cities), last(r.shares.villages), r.weight_index] }));
        return V.base({ grid: V.grid({ top: 24, bottom: 28 }),
          tooltip: V.tooltip({ trigger: "item", formatter: (p) => V.tipRows(p.name, [{ color: V.placeColor("big_cities"), label: "Big cities", value: V.fmt(p.value[0]) + "%" }, { color: V.placeColor("villages"), label: "Villages", value: V.fmt(p.value[1]) + "%" }, { color: V.cssVar("--color-chart-axis"), label: "Weight index", value: V.fmt(p.value[2], 2) }]) }),
          xAxis: V.valueAxis({ name: "Big cities 2025, %", nameLocation: "middle", nameGap: 28, scale: true, splitLine: { show: false }, axisLine: { show: true, lineStyle: { color: V.cssVar("--color-chart-axis") } } }),
          yAxis: V.valueAxis({ name: "Villages, %", scale: true }),
          series: [{ type: "scatter", name: "Voivodeships", data: pts, symbolSize: (v) => 10 + Math.sqrt(v[2]) * 8, itemStyle: { color: V.placeColor("big_cities"), opacity: 0.75, borderColor: V.cssVar("--color-chart-surface"), borderWidth: 1.5 }, emphasis: { itemStyle: { opacity: 1 } } }] });
      }, height: 360 },
    { id: "heatmap", title: "Heatmap: every voivodeship, every year", subtitle: "Heatmap. Villages, % of population, 16 voivodeships x 26 years (synthetic)",
      source: S, load, csv: (d) => ({ header: ["voivodeship", ...yearsOf(d)], rows: d.regions.map((r) => [r.name, ...r.shares.villages]) }),
      build(d) {
        const cells = []; d.regions.forEach((r, ri) => r.shares.villages.forEach((v, yi) => cells.push([yi, ri, v])));
        const ramp = V.mapRamp().slice().reverse();
        return V.base({ grid: V.grid({ top: 8, bottom: 70, left: 4, right: 8 }),
          tooltip: V.tooltip({ trigger: "item", formatter: (p) => V.tipRows(d.regions[p.value[1]].name + ", " + d.years[p.value[0]], [{ color: p.color, label: "Villages", value: V.fmt(p.value[2]) + "%" }]) }),
          xAxis: V.catAxis(yearsOf(d), { splitArea: { show: false }, axisLabel: Object.assign(V.textStyle(), { interval: window.innerWidth < 600 ? 7 : 4 }) }),
          yAxis: V.catAxis(d.regions.map((r) => r.name), { inverse: true, axisLabel: Object.assign(V.textStyle(), { fontSize: 11 }), axisLine: { show: false }, axisTick: { show: false } }),
          visualMap: V.visualMapBase({ type: "piecewise", orient: "horizontal", left: 0, bottom: 0, splitNumber: 7, min: 20, max: 70, precision: 0, inRange: { color: ramp }, formatter: (a, b) => `${a}-${b}%`, itemGap: 6, textStyle: V.textStyle({ fontSize: 11 }) }),
          series: [{ type: "heatmap", data: cells, itemStyle: { borderColor: V.cssVar("--color-chart-surface"), borderWidth: 1 }, emphasis: { itemStyle: { borderColor: V.cssVar("--color-text-primary"), borderWidth: 2 } } }] });
      }, height: (w) => (w < 600 ? 520 : 480) },
    { id: "treemap", title: "Treemap: size = weight, colour = place type", subtitle: "Treemap. Synthetic population by voivodeship and place type, 2025 (weight index x share; synthetic)",
      source: S, load, htmlLegend: placeLegendHtml,
      csv: (d) => ({ header: ["voivodeship", "place type", "weight x share"], rows: d.regions.flatMap((r) => P.map((k) => [r.name, L[k], Math.round(r.weight_index * last(r.shares[k])) / 100])) }),
      build(d) {
        const tree = d.regions.map((r) => ({ name: C.cap(r.name), children: P.map((k) => ({ name: L[k], value: Math.round(r.weight_index * last(r.shares[k])) / 100, itemStyle: { color: V.placeColor(k) } })) }));
        return V.base({ tooltip: V.tooltip({ trigger: "item", formatter: (p) => V.tipRows(p.treePathInfo.slice(1).map((x) => x.name).join(" / "), [{ color: p.color || V.cssVar("--color-chart-axis"), label: "Weight x share", value: V.fmt(p.value, 2) }]) }),
          series: [{ type: "treemap", roam: false, nodeClick: "zoomToNode", breadcrumb: { show: true, bottom: 0, itemStyle: { color: V.cssVar("--color-bg-sunken"), textStyle: { color: V.cssVar("--color-text-primary") }, borderColor: V.cssVar("--color-border-subtle") } }, top: 0, left: 0, right: 0, bottom: 28, data: tree,
            label: { show: true, color: "#fff", fontSize: 11, formatter: "{b}" }, upperLabel: { show: true, height: 20, color: V.cssVar("--color-text-primary"), fontSize: 12, fontWeight: 600 },
            itemStyle: { borderColor: V.cssVar("--color-chart-surface"), borderWidth: 2, gapWidth: 1 }, levels: [{ itemStyle: { borderWidth: 0, gapWidth: 3 } }, { itemStyle: { gapWidth: 1 } }] }] });
      }, height: 400 },
    { id: "sunburst", title: "Sunburst: place type first, then voivodeship", subtitle: "Sunburst. Same synthetic weights as the treemap, 2025; click a ring segment to zoom in (synthetic)",
      source: S, load, htmlLegend: placeLegendHtml,
      csv: (d) => ({ header: ["place type", "voivodeship", "weight x share"], rows: P.flatMap((k) => d.regions.map((r) => [L[k], r.name, Math.round(r.weight_index * last(r.shares[k])) / 100])) }),
      build(d) {
        const tree = P.map((k) => ({ name: L[k], itemStyle: { color: V.placeColor(k) }, children: d.regions.map((r) => ({ name: C.cap(r.name), value: Math.round(r.weight_index * last(r.shares[k])) / 100 })) }));
        return V.base({ tooltip: V.tooltip({ trigger: "item", formatter: (p) => V.tipRows(p.treePathInfo.slice(1).map((x) => x.name).join(" / "), [{ color: p.color, label: "Weight x share", value: V.fmt(p.value, 2) }]) }),
          series: [{ type: "sunburst", radius: ["12%", "92%"], center: ["50%", "50%"], data: tree, sort: undefined, nodeClick: "rootToNode",
            itemStyle: { borderColor: V.cssVar("--color-chart-surface"), borderWidth: 1.5, opacity: 0.9 }, label: { color: V.cssVar("--color-text-primary"), fontSize: 10, minAngle: 8 },
            levels: [{}, { r0: "12%", r: "38%", label: { rotate: 0, color: "#fff", fontSize: 12, fontWeight: 600 } }, { r0: "38%", r: "92%", label: { align: "right", minAngle: 12 }, itemStyle: { opacity: 0.55 } }] }] });
      }, height: 400 },
    { id: "small-multiples", title: "Small multiples: one panel per voivodeship", subtitle: "Small multiples. Villages, % of population, 2000-2025, same scale in every panel (synthetic)",
      source: S, load, csv: (d) => ({ header: ["voivodeship", ...yearsOf(d)], rows: d.regions.map((r) => [r.name, ...r.shares.villages]) }),
      build(d, ctx) {
        const cols = ctx.width < 600 ? 3 : 4, rows = Math.ceil(16 / cols), w = ctx.width, ph = ctx.width < 600 ? 92 : 120;
        const grids = [], xs = [], ys = [], ser = [], titles = [];
        d.regions.forEach((r, i) => {
          const c = i % cols, rw = Math.floor(i / cols), cw = (w - 8) / cols;
          grids.push({ left: c * cw + 6, top: rw * ph + 22, width: cw - 14, height: ph - 44, containLabel: false });
          xs.push(V.catAxis(yearsOf(d), { gridIndex: i, show: false, boundaryGap: false }));
          ys.push(V.valueAxis({ gridIndex: i, min: 20, max: 70, axisLabel: { show: false }, splitNumber: 2 }));
          titles.push({ text: C.cap(r.name.length > 14 && cols === 3 ? r.name.slice(0, 12) + "." : r.name), left: c * cw + 6, top: rw * ph + 2, textStyle: V.textStyle({ color: V.cssVar("--color-text-primary"), fontSize: 11, fontWeight: 600 }) });
          ser.push({ type: "line", xAxisIndex: i, yAxisIndex: i, name: r.name, data: r.shares.villages, symbol: "none", lineStyle: { width: 1.8, color: V.placeColor("villages") }, areaStyle: { color: V.placeColor("villages"), opacity: 0.15 }, color: V.placeColor("villages") });
        });
        return V.base({ title: titles, grid: grids, xAxis: xs, yAxis: ys, series: ser,
          tooltip: V.tooltip({ trigger: "axis", formatter: (ps) => V.tipRows(ps[0].seriesName + ", " + ps[0].axisValueLabel, [{ color: V.placeColor("villages"), label: "Villages", value: V.fmt(ps[0].value) + "%" }]) }),
          axisPointer: { link: [{ xAxisIndex: "all" }] } });
      }, height: (w) => Math.ceil(16 / (w < 600 ? 3 : 4)) * (w < 600 ? 92 : 120) + 8,
      htmlLegend: () => [{ color: V.placeColor("villages"), label: "Villages, share of population (every panel 20-70%)" }] },
    { id: "slope", title: "Slope chart: who rose, who fell, 2000 to 2025", subtitle: "Slope chart. Villages, % of population, two years, one line per voivodeship; blue rose, red fell (synthetic)",
      source: S, load, csv: (d) => ({ header: ["voivodeship", "2000 (%)", "2025 (%)"], rows: d.regions.map((r) => [r.name, r.shares.villages[0], last(r.shares.villages)]) }),
      htmlLegend: () => [{ color: V.cssVar("--data-div-5"), label: "Share rose" }, { color: V.cssVar("--data-div-3"), label: "Share fell" }],
      build(d, ctx) {
        const mob = ctx.width < 600;
        return V.base({ grid: V.grid({ top: 28, bottom: 8, left: mob ? 96 : 150, right: mob ? 96 : 150, containLabel: false }),
          tooltip: V.tooltip({ trigger: "item", formatter: (p) => V.tipRows(p.seriesName, [{ color: p.color, label: "2000", value: V.fmt(p.data.v0) + "%" }, { color: p.color, label: "2025", value: V.fmt(p.data.v1) + "%" }]) }),
          xAxis: V.catAxis(["2000", "2025"], { position: "top", boundaryGap: false, axisLine: { show: false }, axisTick: { show: false }, axisLabel: Object.assign(V.textStyle({ fontWeight: 600, color: V.cssVar("--color-text-primary") }), {}) }),
          yAxis: V.valueAxis({ show: false, min: 20, max: 72 }),
          series: d.regions.map((r) => {
            const a = r.shares.villages[0], b = last(r.shares.villages), col = b >= a ? V.cssVar("--data-div-5") : V.cssVar("--data-div-3");
            return { name: C.cap(r.name), type: "line", data: [{ value: a, v0: a, v1: b, label: { show: true, position: "left", formatter: `${C.cap(r.name)} ${V.fmt(a)}`, color: V.cssVar("--color-chart-text"), fontSize: 10 } }, { value: b, v0: a, v1: b, label: { show: true, position: "right", formatter: `${V.fmt(b)} ${C.cap(r.name)}`, color: V.cssVar("--color-chart-text"), fontSize: 10 } }], symbolSize: 7, lineStyle: { width: 2, color: col }, itemStyle: { color: col }, labelLayout: { hideOverlap: true }, emphasis: { focus: "series", lineStyle: { width: 3.5 } } };
          }) });
      }, height: (w) => (w < 600 ? 520 : 560) },
    { id: "bump", title: "Bump chart: rank changes over time", subtitle: "Ranking (bump) chart. Rank of villages share among 16 voivodeships, 1 = highest, eight selected voivodeships (synthetic)",
      source: S, load, csv: (d) => { const rs = pick(d, SIX.concat(["lubelskie", "łódzkie"])); const rk = C.rankByColumn(d.regions.map((r) => r.name), d.regions.map((r) => r.shares.villages)); return { header: ["year", ...rs.map((r) => r.name)], rows: d.years.map((y, i) => [y, ...rs.map((r) => rk[d.regions.indexOf(r)][i])]) }; },
      build(d) {
        const rk = C.rankByColumn(d.regions.map((r) => r.name), d.regions.map((r) => r.shares.villages));
        const rs = pick(d, SIX.concat(["lubelskie", "łódzkie"]));
        return V.base({ legend: V.legend({ type: "scroll" }), grid: V.grid({ right: 96, top: 48 }),
          tooltip: V.tooltip({ trigger: "axis", formatter: (ps) => V.tipRows(ps[0].axisValueLabel, ps.slice().sort((a, b) => a.value - b.value).map((p) => ({ color: p.color, label: p.seriesName, value: "#" + p.value }))) }),
          xAxis: V.catAxis(yearsOf(d), { boundaryGap: false, axisLabel: Object.assign(V.textStyle(), { interval: window.innerWidth < 600 ? 7 : 4 }) }),
          yAxis: V.valueAxis({ inverse: true, min: 1, max: 16, interval: 3, axisLabel: Object.assign(V.textStyle(), { formatter: "#{value}" }) }),
          series: rs.map((r, j) => lineSeries(C.cap(r.name), rk[d.regions.indexOf(r)], V.catColors()[j], { symbol: "circle", symbolSize: 5, showSymbol: false, endLabel: { show: true, formatter: "{a}", fontSize: 11, color: V.cssVar("--color-text-primary") } })) });
      }, height: 380 },
    { id: "indexed", title: "Indexed series: everything starts at 100 in 2000", subtitle: "Indexed line chart. Villages share, 2000 = 100, national average and four voivodeships (synthetic)",
      source: S, load, csv: (d) => { const nat = C.indexSeries(avg(d, "villages"), 0); const rs = pick(d, ["mazowieckie", "podkarpackie", "łódzkie", "pomorskie"]); return { header: ["year", "national average", ...rs.map((r) => r.name)], rows: d.years.map((y, i) => [y, nat[i], ...rs.map((r) => C.indexSeries(r.shares.villages, 0)[i])]) }; },
      build(d) {
        const rs = pick(d, ["mazowieckie", "podkarpackie", "łódzkie", "pomorskie"]);
        const cols = V.catColors();
        return V.base({ legend: V.legend(), grid: V.grid({ right: 110 }), tooltip: V.tooltip({ formatter: axisTip() }),
          xAxis: V.catAxis(yearsOf(d), { boundaryGap: false, axisLabel: Object.assign(V.textStyle(), { interval: window.innerWidth < 600 ? 7 : 4 }) }),
          yAxis: V.valueAxis({ scale: true }),
          series: [lineSeries("National average", C.indexSeries(avg(d, "villages"), 0), V.cssVar("--color-text-primary"), { lineStyle: { width: 3, color: V.cssVar("--color-text-primary") }, markLine: { silent: true, symbol: "none", label: { show: false }, lineStyle: { type: "dashed", color: V.cssVar("--color-chart-annotation"), width: 1 }, data: [{ yAxis: 100 }] } })]
            .concat(rs.map((r, j) => lineSeries(C.cap(r.name), C.indexSeries(r.shares.villages, 0), cols[j])))
        });
      }, height: 380 },
  ];
  window.SpecsCatalogue = specs;
})();
