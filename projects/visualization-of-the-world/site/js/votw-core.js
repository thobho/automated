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

  // ---------- real data (research/poland-demography-housing processed CSVs) ----------
  // Empty string and missing values are "no data", never 0: a gap must stay visible.
  function numOrNull(v) {
    if (v === null || v === undefined || v === "") return null;
    const n = Number(v);
    return Number.isNaN(n) ? null : n;
  }

  // Keep rows where every field in `where` matches (string comparison, like the CSV).
  function filterRows(rows, where) {
    const ks = Object.keys(where || {});
    return rows.filter((r) => ks.every((k) => r[k] === where[k]));
  }

  // Long rows (year, key, value) -> wide, year-aligned arrays. Keys keep file order, years ascend.
  // opts: { yearField, keyField, keyFn, valueField, meta: ["basis", "source_id"] }
  // result: { years:[2000,...], keys:[...], values:{key:[..]}, meta:{key:{basis:[..]}}, raw:{...} }
  function pivotSeries(rows, opts) {
    const o = Object.assign({ yearField: "year", keyField: "class", valueField: "value", meta: [] }, opts || {});
    const keyOf = o.keyFn || ((r) => r[o.keyField]);
    const years = [], keys = [], lookup = new Map();
    rows.forEach((r) => {
      const y = numOrNull(r[o.yearField]), k = keyOf(r);
      if (y === null || k === null || k === undefined) return;
      if (!years.includes(y)) years.push(y);
      if (!lookup.has(k)) { lookup.set(k, true); keys.push(k); }
    });
    years.sort((a, b) => a - b);
    const yi = new Map(years.map((y, i) => [y, i]));
    const values = {}, meta = {}, raw = {};
    keys.forEach((k) => {
      values[k] = years.map(() => null);
      meta[k] = {};
      o.meta.forEach((m) => (meta[k][m] = years.map(() => null)));
      raw[k] = years.map(() => null);
    });
    rows.forEach((r) => {
      const y = numOrNull(r[o.yearField]), k = keyOf(r);
      if (y === null || k === null || k === undefined) return;
      const i = yi.get(y);
      values[k][i] = numOrNull(r[o.valueField]);
      raw[k][i] = r;
      o.meta.forEach((m) => (meta[k][m][i] = r[m] === undefined ? null : r[m]));
    });
    return { years, keys, values, meta, raw };
  }

  // Element-wise sum of aligned arrays; null only when every input is null at that position.
  function sumSeries(arrays) {
    const n = Math.max(...arrays.map((a) => a.length));
    return Array.from({ length: n }, (_, i) => {
      const vs = arrays.map((a) => (i < a.length ? a[i] : null)).filter((v) => v !== null && v !== undefined);
      return vs.length ? vs.reduce((x, y) => x + y, 0) : null;
    });
  }

  // Element-wise value / total * 100, rounded to `digits`. A missing or zero total gives null.
  function percentShare(values, totals, digits) {
    const d = digits === undefined ? 1 : digits;
    const k = Math.pow(10, d);
    return values.map((v, i) => (v === null || v === undefined || !totals[i] ? null : Math.round((v / totals[i]) * 100 * k) / k));
  }

  // Contiguous runs of one basis, e.g. [{ basis: "proxy", years: [2000..2008] }].
  function basisRanges(years, basis) {
    const out = [];
    years.forEach((y, i) => {
      const b = basis[i];
      const cur = out[out.length - 1];
      if (cur && cur.basis === b && cur.end === years[i - 1]) cur.end = y;
      else out.push({ basis: b, start: y, end: y });
    });
    return out;
  }

  // CSV export/table helper: append a source_id column. Per-row ids (function or array) win;
  // otherwise every row gets the fallback (spec source ids). Never an invented id: unknown -> "".
  function csvWithSourceIds(table, fallback) {
    const n = table.rows.length;
    let ids;
    if (typeof table.sourceId === "function") ids = table.rows.map((r, i) => table.sourceId(r, i));
    else if (Array.isArray(table.sourceId)) ids = table.sourceId;
    else if (table.sourceId) ids = table.rows.map(() => table.sourceId);
    else if (fallback) ids = table.rows.map(() => (Array.isArray(fallback) ? fallback.join(";") : fallback));
    else ids = table.rows.map(() => "");
    return { header: [...table.header, "source_id"], rows: table.rows.map((r, i) => [...r, ids[i] === null || ids[i] === undefined ? "" : String(ids[i])]) };
  }

  // -- the eight shipped real files --
  const populationByClass = (rows) => pivotSeries(rows, { valueField: "population", meta: ["source_id"] });
  // Housing completions keyed "<class>|<type>"; basis and source_id travel with every value so proxy
  // and direct years can be told apart and never plotted as one unlabelled line.
  const completionsByClass = (rows) => pivotSeries(rows, { keyFn: (r) => r.class + "|" + r.type, valueField: "dwellings", meta: ["basis", "source_id"] });
  const housingVsPopulation = (rows, measure) => pivotSeries(measure ? filterRows(rows, { measure }) : rows, { keyFn: (r) => r.class + "|" + r.measure, valueField: "value", meta: ["source_id"] });
  const europeByGeo = (rows, indicator, sex) => pivotSeries(filterRows(rows, { indicator, sex: sex || "total" }), { keyField: "geo", valueField: "value", meta: ["geo_name", "source_id"] });
  const bigCities = (rows) => rows.map((r) => ({ unit_id: r.unit_id, city: r.city, population: numOrNull(r.population_latest_year), year: numOrNull(r.latest_year), source_id: r.source_id }))
    .filter((c) => c.population !== null).sort((a, b) => b.population - a.population || (a.city < b.city ? -1 : 1));

  return { PLACE_TYPES, PLACE_LABEL, parseCsv, toCsv, csvCell, indexSeries, rankByColumn, filterPlaces, makeBins, bbox, zoomTo, regionsFromCsv, sharesConsistent, cap,
    numOrNull, filterRows, pivotSeries, sumSeries, percentShare, basisRanges, csvWithSourceIds,
    populationByClass, completionsByClass, housingVsPopulation, europeByGeo, bigCities };
});
