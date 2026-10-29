(function () {
  "use strict";
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const BADGE = {
    works: ['badge--good', "Works", '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="m3 8.5 3 3 7-7"/></svg>'],
    limits: ['badge--warning', "Works with limits", '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M8 2 1.5 14h13L8 2zM8 6.5v3.5M8 12v.3"/></svg>'],
    no: ['badge--danger', "Not possible", '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 4l8 8M12 4l-8 8"/></svg>'],
  };
  let rows = [], filter = "all";
  function draw() {
    const shown = rows.filter((r) => filter === "all" || r.status === filter);
    document.getElementById("count").textContent = `${shown.length} of ${rows.length} capabilities`;
    document.getElementById("table").innerHTML = `<div class="table-scroll" tabindex="0" role="region" aria-label="Capabilities table"><table class="data-table matrix"><thead><tr><th scope="col">Capability</th><th scope="col">Status</th><th scope="col">Notes and limits</th><th scope="col">Code</th><th scope="col">Docs</th></tr></thead><tbody>${shown.map((r) => { const b = BADGE[r.status]; return `<tr><th scope="row"><span class="small secondary">${esc(r.group)}</span><br>${esc(r.capability)}</th><td><span class="badge ${b[0]}">${b[2]}${b[1]}</span></td><td>${esc(r.notes)}</td><td><code>${esc(r.code)}</code></td><td>${r.docs ? `<a href="${esc(r.docs)}">docs</a>` : "-"}</td></tr>`; }).join("")}</tbody></table></div>`;
  }
  fetch("data/capabilities.json").then((r) => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); }).then((j) => {
    rows = j.capabilities;
    const f = document.getElementById("filters");
    const counts = (s) => rows.filter((r) => s === "all" || r.status === s).length;
    f.innerHTML = [["all", "All"], ["works", "Works"], ["limits", "Works with limits"], ["no", "Not possible"]].map(([k, t]) => `<button class="btn btn--secondary" type="button" data-f="${k}" aria-pressed="${k === "all"}">${t} (${counts(k)})</button>`).join("");
    f.addEventListener("click", (e) => { const b = e.target.closest("[data-f]"); if (!b) return; filter = b.dataset.f; f.querySelectorAll("[data-f]").forEach((x) => x.setAttribute("aria-pressed", String(x === b))); draw(); });
    draw();
  }).catch((e) => { document.getElementById("table").innerHTML = `<div class="state state--error" role="alert"><p class="state__title">Could not load the matrix</p><p class="state__text">${esc(e.message)}</p></div>`; });
})();
