(function () {
  const host = document.getElementById("figures");
  window.SpecsFormats.forEach((s) => Votw.figure(host, s));
  window.formatsCompare().then((r) => {
    document.getElementById("compare").innerHTML = `CSV and JSON carry the same numbers: <span class="${r.sameVals ? "cmp-ok" : "cmp-bad"}">${r.sameVals ? "yes" : "NO"}</span> (${r.n} voivodeships). GeoJSON and TopoJSON describe the same ${r.nGeo} voivodeships (same TERYT code and name): <span class="${r.sameGeo ? "cmp-ok" : "cmp-bad"}">${r.sameGeo ? "yes" : "NO"}</span>.`;
  }).catch((e) => { document.getElementById("compare").textContent = "Could not compare: " + e.message; });
})();
