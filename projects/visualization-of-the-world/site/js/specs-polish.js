// Forced state demos: loading (never resolves), empty (no rows), error (fails once, then works).
(function () {
  "use strict";
  const V = window.Votw, C = window.VotwCore, S = V.DEMO_SOURCE;
  let failed = false;
  const simple = (d) => V.base({ grid: V.grid({ top: 16 }), xAxis: V.catAxis(d.years.map(String), { boundaryGap: false, axisLabel: Object.assign(V.textStyle(), { interval: 6 }) }), yAxis: V.valueAxis({ min: 20, max: 50 }), tooltip: V.tooltip({ formatter: (ps) => V.tipRows(ps[0].axisValueLabel, [{ color: ps[0].color, label: "Big cities", value: V.fmt(ps[0].value) + "%" }]) }),
    series: [{ type: "line", name: "Big cities", symbol: "none", data: d.regions[0].shares.big_cities, lineStyle: { width: 2, color: V.placeColor("big_cities") }, itemStyle: { color: V.placeColor("big_cities") } }] });
  const csv = (d) => ({ header: ["year", "big cities (%)"], rows: d.years.map((y, i) => [y, d.regions[0].shares.big_cities[i]]) });
  window.SpecsPolish = [
    { id: "state-loading", keepLoading: true, title: "Loading", className: "span-all lg-span-4", subtitle: "Skeleton while data is fetched; the request here never finishes on purpose.", source: S, height: 260, load: () => new Promise(() => {}), build: simple, csv },
    { id: "state-empty", title: "Empty", className: "span-all lg-span-4", subtitle: "The data loaded but has no rows for this selection: say what is missing and offer a reset.", source: S, height: 260, load: async () => [], emptyMsg: { title: "No data for this selection", text: "The demo file has zero rows for these filters." }, onReset: (ctl) => { ctl.load = ctl.load; }, build: simple, csv },
    { id: "state-error", title: "Error", className: "span-all lg-span-4", subtitle: "The request failed: say what happened and offer Try again. The first attempt fails, the retry works.", source: S, height: 260,
      load: async () => { if (!failed) { failed = true; throw new Error("simulated network failure"); } return V.data.regions(); }, build: simple, csv },
  ];
  // Fix the empty card's reset: after reset it loads real data so the page shows recovery
  window.SpecsPolish[1].onReset = (ctl) => { ctl.spec.load = () => V.data.regions(); ctl.load(); };
})();
