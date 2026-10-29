(function () {
  const host = document.getElementById("figures");
  window.SpecsPolish.forEach((s) => Votw.figure(host, s));
  const upd = () => { const w = window.innerWidth; document.getElementById("vp").textContent = w + " px"; document.getElementById("bp").textContent = w < 600 ? "Phone layout: 4 columns, menu button" : w < 960 ? "Tablet layout: 8 columns, menu button" : "Desktop layout: 12 columns, full navigation"; };
  upd(); window.addEventListener("resize", upd);
  const names = ["--data-place-big-cities", "--data-place-small-cities", "--data-place-villages", "--data-div-3", "--data-div-5", "--data-map-2", "--data-map-6"];
  const draw = () => { document.getElementById("sw").innerHTML = names.map((n) => `<span><i style="--c:var(${n})"></i>${n.replace("--data-", "")}</span>`).join(""); };
  draw();
})();
