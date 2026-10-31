// Mounts the real-data specs. KPI cards are static HTML in real.html with manual Source footers.
(function () {
  const host = document.getElementById("figures");
  window.SpecsReal.forEach((s) => Votw.figure(host, s));
})();
