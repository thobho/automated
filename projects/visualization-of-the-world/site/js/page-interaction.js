(function () {
  const I = window.SpecsInteraction, st = I.state, host = document.getElementById("figures");
  I.specs.forEach((s) => { I.figs[s.id] = Votw.figure(host, s); });
  const all = () => I.rerender("rank", "map", "timeline", "brush", "brushsum");
  document.addEventListener("yearchange", (e) => { st.year = e.detail.year; document.getElementById("year-live").textContent = st.year; I.rerender("rank", "map", "timeline"); });
  document.addEventListener("placechange", (e) => { st.active = e.detail.active.map((k) => k.replace(/-/g, "_")); st.brushed = null; st.brushedPts = null; all(); });
  document.getElementById("reset-sel").addEventListener("click", () => { st.region = null; I.rerender("rank", "map", "timeline"); });
})();
