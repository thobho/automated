(function () {
  const host = document.getElementById("figures");
  window.SpecsCatalogue.forEach((s) => { s.className = "span-all lg-span-6"; Votw.figure(host, s); });
  // The two wide ones get the full row
  ["heatmap", "small-multiples", "slope"].forEach((id) => document.querySelector(`[data-chart-card="${id}"]`)?.classList.remove("lg-span-6"));
})();
