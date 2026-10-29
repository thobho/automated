// Pure logic, no DOM and no ECharts, so it runs in the browser (global VotwCore) and under `node --test`.
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.VotwCore = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  const PLACE_TYPES = ["big_cities", "small_cities", "villages"];
  const PLACE_LABEL = { big_cities: "Big cities", small_cities: "Small cities", villages: "Villages" };

  // RFC 4180 style parser: quoted fields, doubled quotes, CRLF, embedded newlines. Returns array of row objects.
  function parseCsv(text) {
    const rows = [];
    let row = [], field = "", inQ = false;
    text = text.replace(/^﻿/, "");
    for (let i = 0; i < text.length; i++) {
      const c = text[i];
      if (inQ) {
        if (c === '"') { if (text[i + 1] === '"') { field += '"'; i++; } else inQ = false; }
        else field += c;
      } else if (c === '"') inQ = true;
      else if (c === ",") { row.push(field); field = ""; }
      else if (c === "\n" || c === "\r") {
        if (c === "\r" && text[i + 1] === "\n") i++;
        row.push(field); field = "";
        if (row.length > 1 || row[0] !== "") rows.push(row);
        row = [];
      } else field += c;
    }
    if (field !== "" || row.length) { row.push(field); rows.push(row); }
    if (!rows.length) return [];
    const head = rows[0];
    return rows.slice(1).map((r) => Object.fromEntries(head.map((h, i) => [h, r[i] === undefined ? "" : r[i]])));
  }

  function csvCell(v) {
    if (v === null || v === undefined) return "";
    const s = String(v);
    return /[",\r\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }

  // header: array of column names; rows: array of arrays. Always ends with a DEMO line when meta.note is given.
  function toCsv(header, rows) {
    return [header, ...rows].map((r) => r.map(csvCell).join(",")).join("\r\n") + "\r\n";
  }

  // Indexed series: base year = 100. Missing base (null/0) gives all nulls, never a guess.
  function indexSeries(values, baseIdx) {
    const base = values[baseIdx];
    if (!base) return values.map(() => null);
    return values.map((v) => (v === null || v === undefined ? null : Math.round((v / base) * 1000) / 10));
  }

  // Rank 1..n per column (year) for named series, higher value = rank 1. Ties broken by name for stability.
  function rankByColumn(names, matrix) {
    const out = names.map(() => []);
    const cols = matrix[0].length;
    for (let c = 0; c < cols; c++) {
      const order = names.map((n, i) => ({ n, i, v: matrix[i][c] })).sort((a, b) => b.v - a.v || (a.n < b.n ? -1 : 1));
      order.forEach((o, rank) => (out[o.i][c] = rank + 1));
    }
    return out;
  }

  // Keep only the active place types, in canonical order.
  function filterPlaces(keys, active) {
    return keys.filter((k) => active.includes(k));
  }

  // Equal-width bins; returns edges array of length n+1 and a classifier. null/NaN -> -1 (no data).
  function makeBins(values, n) {
    const v = values.filter((x) => x !== null && x !== undefined && !Number.isNaN(x));
    const lo = Math.floor(Math.min(...v)), hi = Math.ceil(Math.max(...v));
    const step = (hi - lo) / n;
    const edges = Array.from({ length: n + 1 }, (_, i) => Math.round((lo + step * i) * 10) / 10);
    const bin = (x) => (x === null || x === undefined || Number.isNaN(x) ? -1 : Math.min(n - 1, Math.floor((x - lo) / step)));
    return { edges, bin };
  }

  // Bounding box [minLon, minLat, maxLon, maxLat] of GeoJSON features (Polygon / MultiPolygon / Point).
  function bbox(features) {
    let b = [Infinity, Infinity, -Infinity, -Infinity];
    const walk = (c) => {
      if (typeof c[0] === "number") { b = [Math.min(b[0], c[0]), Math.min(b[1], c[1]), Math.max(b[2], c[0]), Math.max(b[3], c[1])]; return; }
      c.forEach(walk);
    };
    features.forEach((f) => walk(f.geometry.coordinates));
    return b;
  }

  // Zoom factor and centre so that a bbox fills a map view. ECharts geo zoom 1 = whole registered map
  // fitted in the view, so the factor is the ratio of the full extent to the bbox extent (capped).
  function zoomTo(box, fullBox, cap) {
    const rw = (fullBox[2] - fullBox[0]) / (box[2] - box[0] || 1e-6);
    const rh = (fullBox[3] - fullBox[1]) / (box[3] - box[1] || 1e-6);
    return { center: [(box[0] + box[2]) / 2, (box[1] + box[3]) / 2], zoom: Math.min(cap || 12, Math.max(1, Math.min(rw, rh) * 0.9)) };
  }

  // Parse the rows of demo-regions.csv into {teryt: {name, big_cities:[], ...}} ordered by year.
  function regionsFromCsv(rows) {
    const out = new Map(), years = [];
    rows.forEach((r) => {
      // Map, not a plain object: integer-like keys such as "10" would be re-ordered before "02"
      const o = out.get(r.teryt) || (out.set(r.teryt, { teryt: r.teryt, name: r.name, shares: { big_cities: [], small_cities: [], villages: [] } }), out.get(r.teryt));
      PLACE_TYPES.forEach((k) => o.shares[k].push(r[k] === "" ? null : Number(r[k])));
      if (!years.includes(+r.year)) years.push(+r.year);
    });
    return { years, regions: Array.from(out.values()) };
  }

  // Sum of the three shares must be 100 +- tolerance (rounding of one decimal each).
  function sharesConsistent(region, tol) {
    const n = region.shares.villages.length;
    for (let i = 0; i < n; i++) {
      const s = PLACE_TYPES.reduce((a, k) => a + region.shares[k][i], 0);
      if (Math.abs(s - 100) > (tol || 0.25)) return false;
    }
    return true;
  }

  const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);

  return { PLACE_TYPES, PLACE_LABEL, parseCsv, toCsv, csvCell, indexSeries, rankByColumn, filterPlaces, makeBins, bbox, zoomTo, regionsFromCsv, sharesConsistent, cap };
});
