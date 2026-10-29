// Run: node --test site/tests/   (Node 18+, no dependencies)
const test = require("node:test");
const assert = require("node:assert");
const fs = require("fs");
const path = require("path");
const C = require("../js/votw-core.js");

test("parseCsv handles quotes, doubled quotes, CRLF and embedded commas", () => {
  const rows = C.parseCsv('a,b\r\n"x, y","he said ""hi"""\r\n1,2\r\n');
  assert.deepStrictEqual(rows, [{ a: "x, y", b: 'he said "hi"' }, { a: "1", b: "2" }]);
});
test("toCsv round-trips through parseCsv", () => {
  const rows = [["Łódź", 'q"uote'], ["a,b", 3]];
  const back = C.parseCsv(C.toCsv(["name", "v"], rows));
  assert.deepStrictEqual(back.map((r) => [r.name, r.v]), [["Łódź", 'q"uote'], ["a,b", "3"]]);
});
test("indexSeries sets base to 100 and keeps gaps as null", () => {
  assert.deepStrictEqual(C.indexSeries([50, 100, null, 25], 0), [100, 200, null, 50]);
  assert.deepStrictEqual(C.indexSeries([0, 1], 0), [null, null]);
});
test("rankByColumn ranks 1 = highest and is stable on ties", () => {
  const r = C.rankByColumn(["a", "b", "c"], [[1, 5], [3, 5], [2, 1]]);
  assert.deepStrictEqual(r, [[3, 1], [1, 2], [2, 3]]);
});
test("makeBins classifies and flags no data", () => {
  const { edges, bin } = C.makeBins([10, 20, 30, 40], 3);
  assert.strictEqual(edges.length, 4);
  assert.strictEqual(bin(10), 0); assert.strictEqual(bin(40), 2);
  assert.strictEqual(bin(null), -1);
});
test("bbox and zoomTo", () => {
  const f = [{ geometry: { type: "Polygon", coordinates: [[[14, 49], [24, 49], [24, 55], [14, 55]]] } }];
  assert.deepStrictEqual(C.bbox(f), [14, 49, 24, 55]);
  const z = C.zoomTo([18, 50, 20, 52], [14, 49, 24, 55]);
  assert.ok(z.zoom > 2 && z.zoom <= 12);
  assert.deepStrictEqual(z.center, [19, 51]);
});
test("filterPlaces keeps canonical order", () => {
  assert.deepStrictEqual(C.filterPlaces(C.PLACE_TYPES, ["villages", "big_cities"]), ["big_cities", "villages"]);
});

// ---- the shipped demo data ----
const data = (f) => fs.readFileSync(path.join(__dirname, "..", "data", f), "utf-8");
test("demo data: CSV and JSON carry the same numbers", () => {
  const json = JSON.parse(data("demo.json"));
  const csv = C.regionsFromCsv(C.parseCsv(data("demo-regions.csv")));
  assert.strictEqual(csv.regions.length, 16);
  assert.deepStrictEqual(csv.years, json.years);
  json.regions.forEach((r) => {
    const c = csv.regions.find((x) => x.teryt === r.teryt);
    assert.deepStrictEqual(c.shares, r.shares);
    assert.ok(C.sharesConsistent(r), "shares sum to 100 for " + r.name);
  });
});
test("demo data is labelled as not real everywhere", () => {
  assert.match(JSON.parse(data("demo.json")).meta.note, /DEMO DATA, NOT REAL/);
  ["demo-regions.csv", "demo-powiats.csv", "demo-cities.csv"].forEach((f) =>
    C.parseCsv(data(f)).forEach((r) => assert.strictEqual(r.demo_flag, "DEMO DATA, NOT REAL", f)));
});
test("geo data: counts and join keys", () => {
  const v = JSON.parse(data("geo/voivodeships.geojson")).features;
  assert.strictEqual(v.length, 16);
  const cities = JSON.parse(data("geo/cities.geojson")).features;
  const rows = C.parseCsv(data("demo-cities.csv"));
  assert.strictEqual(cities.length, rows.length);
  assert.strictEqual(cities.filter((f) => f.properties.big_city).length, 34);
  const powiats = JSON.parse(data("geo/powiats.topojson")).objects.powiats.geometries;
  assert.strictEqual(powiats.length, C.parseCsv(data("demo-powiats.csv")).length);
});
