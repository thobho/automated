// Motion and interaction specs. One shared state (year, active place types, selected region, brushed cities)
// drives several linked figures; any control change re-renders them (setOption merge keeps transitions).
(function () {
  "use strict";
  const V = window.Votw, C = window.VotwCore;
  const S = V.DEMO_SOURCE;
  const state = { year: 2025, active: ["villages"], region: null, brushed: null, kind: "bar" };
  const figs = {};
  const rerender = (...ids) => ids.forEach((id) => figs[id]?.render());
  const metric = (r, yi) => Math.round(state.active.reduce((a, k) => a + r.shares[k][yi], 0) * 10) / 10;
  const label = () => state.active.map((k) => C.PLACE_LABEL[k]).join(" + ");
  const yi = (d) => d.years.indexOf(state.year);
  const reg = () => V.data.regions();
  const barColor = () => (state.active.length === 1 ? V.placeColor(state.active[0]) : V.cssVar("--data-seq-blue-400"));

  const rank = {
    id: "rank", title: "Ranking redraws as the year changes", className: "span-all lg-span-6", merge: true, source: S, load: reg, height: 470,
    subtitle: "Animated horizontal bars, re-sorted live. Share of population in the selected place types, % (synthetic)",
    csv: (d) => ({ header: ["voivodeship", `${label()} ${state.year} (%)`], rows: d.regions.map((r) => [r.name, metric(r, yi(d))]).sort((a, b) => b[1] - a[1]) }),
    onChart(chart) { chart.on("click", (p) => { if (p.componentType === "series") { state.region = state.region === p.data.teryt ? null : p.data.teryt; rerender("rank", "map", "timeline"); } }); },
    build(d) {
      const i = yi(d);
      const rows = d.regions.map((r) => ({ name: C.cap(r.name), value: metric(r, i), teryt: r.teryt }));
      return V.base({ grid: V.grid({ top: 8, left: 4, right: 40 }), tooltip: V.tooltip({ trigger: "item", formatter: (p) => V.tipRows(p.name + ", " + state.year, [{ color: p.color, label: label(), value: V.fmt(p.value) + "%" }]) }),
        xAxis: V.valueAxis({ max: 100, axisLabel: Object.assign(V.textStyle(), { formatter: "{value}%" }) }),
        yAxis: V.catAxis(rows.map((r) => r.name), { inverse: true, max: 15, animationDuration: 0, animationDurationUpdate: 200, axisLabel: Object.assign(V.textStyle({ fontSize: 11 }), { interval: 0 }), axisLine: { show: false }, axisTick: { show: false } }),
        series: [{ type: "bar", realtimeSort: true, name: label(), data: rows.map((r) => ({ name: r.name, value: r.value, teryt: r.teryt, itemStyle: { color: barColor(), borderRadius: [0, 4, 4, 0], borderColor: r.teryt === state.region ? V.cssVar("--color-text-primary") : "transparent", borderWidth: r.teryt === state.region ? 2 : 0 } })),
          label: { show: true, position: "right", valueAnimation: true, color: V.cssVar("--color-text-primary"), fontSize: 11, formatter: (p) => V.fmt(p.value) }, barMaxWidth: 20, animationDuration: 0, animationDurationUpdate: V.reduced() ? 0 : 450, animationEasingUpdate: "linear" }] });
    } };

  const map = {
    id: "map", title: "Linked map follows the same year and filter", className: "span-all lg-span-6", merge: true, source: { label: "GUGiK PRG boundaries (simplified) + synthetic demo values", url: "https://www.geoportal.gov.pl/pl/dane/panstwowy-rejestr-granic-prg/", meta: "values: synthetic demo data" }, height: 470,
    subtitle: "Choropleth of the same metric. Click a voivodeship to pick it in the ranking and the timeline; click again to clear (synthetic)",
    async load() { const [maps, d] = await Promise.all([V.ensureMaps(), reg()]); return Object.assign({}, d, { maps }); },
    csv: (d) => ({ header: ["voivodeship", `${label()} ${state.year} (%)`], rows: d.regions.map((r) => [r.name, metric(r, yi(d))]) }),
    onChart(chart) { chart.on("click", (p) => { if (p.componentType === "series") { state.region = state.region === p.name ? null : p.name; rerender("rank", "map", "timeline"); } }); },
    build(d) {
      const all = d.regions.flatMap((r) => d.years.map((_, i) => metric(r, i)));
      const { edges } = C.makeBins(all, 5), ramp = V.mapRamp(), cols = [0, 2, 3, 4, 6].map((i) => ramp[i]);
      const i = yi(d), nm = Object.fromEntries(d.regions.map((r) => [r.teryt, r.name]));
      return V.base({ tooltip: V.tooltip({ trigger: "item", formatter: (p) => V.tipRows(C.cap(nm[p.name] || p.name), [{ color: p.color, label: label() + ", " + state.year, value: V.fmt(p.value) + "%" }]) }),
        visualMap: V.visualMapBase({ type: "piecewise", orient: "horizontal", left: 0, bottom: 0, pieces: cols.map((c, k) => ({ gte: edges[k], lt: k === 4 ? edges[5] + 0.01 : edges[k + 1], label: edges[k] + "-" + edges[k + 1], color: c })), itemGap: 6, itemWidth: 12, textGap: 4, textStyle: V.textStyle({ fontSize: 11 }) }),
        series: [{ type: "map", map: "pl", nameProperty: "teryt", roam: true, top: 4, bottom: 40, data: d.regions.map((r) => ({ name: r.teryt, value: metric(r, i) })), itemStyle: { borderColor: V.cssVar("--color-map-boundary"), borderWidth: 1 }, select: { itemStyle: { borderColor: V.cssVar("--color-text-primary"), borderWidth: 2.5 } }, selectedMode: "single", emphasis: { label: { show: false }, itemStyle: { borderColor: V.cssVar("--color-text-primary"), borderWidth: 2 } }, label: { show: false } }] });
    },
    afterRender(ctl) { ctl.chart.dispatchAction({ type: "unselect", name: state.region ? undefined : undefined }); if (state.region) ctl.chart.dispatchAction({ type: "select", name: state.region }); } };

  const timeline = {
    id: "timeline", title: "Timeline with zoom and pan", className: "span-all", merge: false, source: S, load: reg, height: 400,
    subtitle: "Line chart of the selected region (or the national average) with a marker on the chosen year. Drag the slider handles, scroll or pinch inside the chart to zoom, drag to pan (synthetic)",
    csv: (d) => { const rs = state.region ? d.regions.filter((r) => r.teryt === state.region) : d.regions; return { header: ["year", ...state.active.map((k) => C.PLACE_LABEL[k] + " (%)")], rows: d.years.map((y, i) => [y, ...state.active.map((k) => Math.round(rs.reduce((a, r) => a + r.shares[k][i], 0) / rs.length * 10) / 10)]) }; },
    build(d, ctl) {
      const rs = state.region ? d.regions.filter((r) => r.teryt === state.region) : d.regions;
      const name = state.region ? C.cap(rs[0].name) : "National average";
      const ser = state.active.map((k) => ({ name: C.PLACE_LABEL[k], type: "line", symbol: "none", color: V.placeColor(k), lineStyle: { width: 2, color: V.placeColor(k) }, itemStyle: { color: V.placeColor(k) }, emphasis: { focus: "series" }, data: d.years.map((_, i) => Math.round(rs.reduce((a, r) => a + r.shares[k][i], 0) / rs.length * 10) / 10) }));
      ser[0].markLine = { silent: true, symbol: "none", animation: false, label: { formatter: String(state.year), color: V.cssVar("--color-chart-annotation") }, lineStyle: { type: "dashed", color: V.cssVar("--color-chart-annotation"), width: 1 }, data: [{ xAxis: String(state.year) }] };
      return V.base({ legend: V.legend({ data: ser.map((s) => s.name) }), title: { text: name, right: 0, top: 0, textStyle: V.textStyle({ color: V.cssVar("--color-text-primary"), fontWeight: 600, fontSize: 13 }) },
        grid: V.grid({ bottom: 52 }), tooltip: V.tooltip({ formatter: (ps) => V.tipRows(ps[0].axisValueLabel, ps.map((p) => ({ color: p.color, label: p.seriesName, value: V.fmt(p.value) + "%" }))) }),
        dataZoom: [{ type: "inside", filterMode: "none" }, { type: "slider", height: 24, bottom: 6, borderColor: V.cssVar("--color-border-subtle"), fillerColor: V.cssVar("--color-accent-subtle"), textStyle: V.textStyle(), handleStyle: { color: V.cssVar("--color-accent"), borderColor: V.cssVar("--color-accent") }, dataBackground: { lineStyle: { color: V.cssVar("--color-chart-axis") }, areaStyle: { color: V.cssVar("--color-chart-grid") } } }],
        xAxis: V.catAxis(d.years.map(String), { boundaryGap: false }), yAxis: V.valueAxis({ min: 0, max: 100, axisLabel: Object.assign(V.textStyle(), { formatter: "{value}%" }) }), series: ser });
    } };

  const brush = {
    id: "brush", title: "Brush cities to filter the linked bars", className: "span-all lg-span-6", merge: false, source: { label: "Synthetic demo values; city names from GeoNames via poland-geography", url: "https://www.geonames.org", meta: "CC BY; values made up" }, height: 430,
    subtitle: "Scatter of 1,020 cities: size index (x, log scale) against growth (y, %). Drag a rectangle on the plot to select; the bars on the right count the selection per voivodeship (synthetic)",
    async load() { return V.data.cities(); },
    csv: (d) => ({ header: ["city", "place type", "size index", "growth (%)"], rows: d.filter((r) => state.active.includes(r.place_type)).map((r) => [r.name, C.PLACE_LABEL[r.place_type], Number(r.size_index), Number(r.growth_pct)]) }),
    onChart(chart) {
      chart.on("brushSelected", (p) => {
        const sel = p.batch[0]?.selected || [];
        const idx = new Set(); sel.forEach((s) => s.dataIndex.forEach((i) => idx.add(s.seriesName + ":" + i)));
        state.brushed = idx.size ? sel : null;
        state.brushedPts = sel.map((s) => s.dataIndex.map((i) => figs.brush.series[s.seriesName]?.[i]).filter(Boolean)).flat();
        figs.brushsum?.render();
      });
    },
    build(d, ctl) {
      const act = ["big_cities", "small_cities"].filter((k) => state.active.includes(k));
      ctl.series = {};
      if (!act.length) return "empty";
      const series = act.map((k) => { const rows = d.filter((r) => r.place_type === k); ctl.series[C.PLACE_LABEL[k]] = rows; return { name: C.PLACE_LABEL[k], type: "scatter", symbolSize: 6, color: V.placeColor(k), data: rows.map((r) => ({ name: r.name, value: [Number(r.size_index), Number(r.growth_pct)] })), itemStyle: { color: V.placeColor(k), opacity: 0.7 }, emphasis: { scale: 1.6 }, large: false }; });
      return V.base({ legend: V.legend(), grid: V.grid({ top: 52, bottom: 30 }), tooltip: V.tooltip({ trigger: "item", formatter: (p) => V.tipRows(p.name, [{ color: p.color, label: "Size index", value: V.fmt(p.value[0]) }, { color: p.color, label: "Growth", value: V.fmt(p.value[1]) + "%" }]) }),
        brush: { toolbox: ["rect", "clear"], xAxisIndex: 0, brushStyle: { borderColor: V.cssVar("--color-accent"), color: V.cssVar("--color-accent-subtle"), borderWidth: 1.5 }, outOfBrush: { colorAlpha: 0.15 } },
        toolbox: { right: 0, top: 0, itemSize: 18, iconStyle: { borderColor: V.cssVar("--color-text-secondary") }, feature: { brush: { type: ["rect", "clear"], title: { rect: "Select area", clear: "Clear selection" } } } },
        xAxis: V.valueAxis({ type: "log", name: "Size index (log)", nameLocation: "middle", nameGap: 26, min: 1, splitLine: { show: false }, axisLine: { show: true, lineStyle: { color: V.cssVar("--color-chart-axis") } } }), yAxis: V.valueAxis({ name: "%", scale: true }), series });
    }, afterRender(ctl) { ctl.chart.dispatchAction({ type: "takeGlobalCursor", key: "brush", brushOption: { brushType: "rect", brushMode: "single" } }); } };

  const brushsum = {
    id: "brushsum", title: "Linked bars: cities in the selection, by voivodeship", className: "span-all lg-span-6", merge: false, source: { label: "Synthetic demo values; city names from GeoNames via poland-geography", url: "https://www.geonames.org", meta: "CC BY; values made up" }, height: 430,
    subtitle: "Count of selected cities per voivodeship. With no selection, every city of the chosen place types is counted (synthetic)",
    async load() { return Promise.all([V.data.cities(), V.data.regions()]).then(([c, r]) => ({ cities: c, regions: r.regions })); },
    csv: (d) => ({ header: ["voivodeship", "cities in selection"], rows: counts(d).map((c) => [c.name, c.n]) }),
    build(d) {
      const cs = counts(d);
      return V.base({ grid: V.grid({ top: 8, left: 4, right: 32 }), tooltip: V.tooltip({ trigger: "item", formatter: (p) => V.tipRows(p.name, [{ color: p.color, label: "Cities", value: String(p.value) }]) }),
        xAxis: V.valueAxis({ minInterval: 1 }), yAxis: V.catAxis(cs.map((c) => C.cap(c.name)), { inverse: true, axisLabel: Object.assign(V.textStyle({ fontSize: 11 }), { interval: 0 }), axisLine: { show: false }, axisTick: { show: false } }),
        series: [{ type: "bar", data: cs.map((c) => c.n), itemStyle: { color: V.cssVar("--data-seq-blue-400"), borderRadius: [0, 4, 4, 0] }, barMaxWidth: 18, label: { show: true, position: "right", color: V.cssVar("--color-text-primary"), fontSize: 11 } }] });
    } };
  function counts(d) {
    let pts;
    if (state.brushedPts && state.brushedPts.length) pts = state.brushedPts;
    else pts = d.cities.filter((r) => state.active.includes(r.place_type));
    return d.regions.map((r) => ({ name: r.name, n: pts.filter((p) => p.voivodeship_teryt === r.teryt).length }));
  }

  const morph = {
    id: "morph", title: "One dataset, three shapes, animated", className: "span-all", merge: true, source: S, load: reg, height: 380,
    subtitle: "Switch between bars, pie and treemap: the same marks move between shapes (ECharts universalTransition). National villages / small cities / big cities mix, 2025 (synthetic)",
    controls(c, ctl) {
      c.innerHTML = '<div class="place-toggle__options" role="group" aria-label="Shape">' + [["bar", "Bars"], ["pie", "Pie"], ["treemap", "Treemap"]].map(([k, t]) => `<button class="btn btn--secondary" type="button" data-kind="${k}" aria-pressed="${k === state.kind}">${t}</button>`).join("") + "</div>";
      c.addEventListener("click", (e) => { const b = e.target.closest("[data-kind]"); if (!b) return; state.kind = b.dataset.kind; c.querySelectorAll("[data-kind]").forEach((x) => x.setAttribute("aria-pressed", String(x === b))); ctl.render(); });
    },
    setOpt: { replaceMerge: ["series", "xAxis", "yAxis", "grid"] },
    csv: (d) => ({ header: ["place type", "share 2025 (%)"], rows: C.PLACE_TYPES.map((k) => [C.PLACE_LABEL[k], nat(d, k)]) }),
    htmlLegend: () => C.PLACE_TYPES.map((k) => ({ color: V.placeColor(k), label: C.PLACE_LABEL[k] })),
    build(d) {
      const items = C.PLACE_TYPES.map((k) => ({ name: C.PLACE_LABEL[k], value: nat(d, k), groupId: k, itemStyle: { color: V.placeColor(k) } }));
      const common = { universalTransition: { enabled: true, divideShape: "clone" }, dataGroupId: "mix" };
      const tip = V.tooltip({ trigger: "item", formatter: (p) => V.tipRows(p.name, [{ color: p.color, label: "Share 2025", value: V.fmt(p.value) + "%" }]) });
      if (state.kind === "pie") return V.base({ tooltip: tip, series: [Object.assign({ type: "pie", radius: ["35%", "75%"], data: items, label: { color: V.cssVar("--color-text-primary"), formatter: "{b}\n{c}%" }, itemStyle: { borderColor: V.cssVar("--color-chart-surface"), borderWidth: 2 } }, common)] });
      if (state.kind === "treemap") return V.base({ tooltip: tip, series: [Object.assign({ type: "treemap", roam: false, breadcrumb: { show: false }, top: 0, bottom: 0, left: 0, right: 0, data: items, label: { color: "#fff", fontSize: 13, formatter: "{b}\n{c}%" }, itemStyle: { borderColor: V.cssVar("--color-chart-surface"), borderWidth: 2 } }, common)] });
      return V.base({ tooltip: tip, grid: V.grid({ top: 16 }), xAxis: V.catAxis(items.map((i) => i.name)), yAxis: V.valueAxis({ max: 60, axisLabel: Object.assign(V.textStyle(), { formatter: "{value}%" }) }),
        series: [Object.assign({ type: "bar", data: items, barMaxWidth: 90, itemStyle: { borderRadius: [4, 4, 0, 0] }, label: { show: true, position: "top", color: V.cssVar("--color-text-primary"), formatter: "{c}%" } }, common)] });
    } };
  const nat = (d, k) => Math.round(d.regions.reduce((a, r) => a + r.shares[k][d.years.length - 1], 0) / d.regions.length * 10) / 10;

  window.SpecsInteraction = { state, figs, specs: [rank, map, timeline, brush, brushsum, morph], rerender };
})();
