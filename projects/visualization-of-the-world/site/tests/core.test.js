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
test("regionsFromCsv keeps file order (integer-like TERYT keys must not reorder)", () => {
  const rows = C.parseCsv("teryt,name,year,big_cities,small_cities,villages\n02,a,2000,1,1,98\n10,b,2000,1,1,98\n04,c,2000,1,1,98\n");
  assert.deepStrictEqual(C.regionsFromCsv(rows).regions.map((r) => r.teryt), ["02", "10", "04"]);
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

// ---- real data shaping (site/data/real/, verbatim research processed CSVs) ----
const real = (f) => C.parseCsv(fs.readFileSync(path.join(__dirname, "..", "data", "real", f), "utf-8"));
const research = (f) => path.join(__dirname, "..", "..", "research", "poland-demography-housing", "data", "processed", f);
const REAL_FILES = ["population_by_class.csv", "housing_completions_by_class.csv", "housing_vs_population.csv", "housing_stock_by_class.csv", "migration_by_place_class.csv", "europe_summary.csv", "europe_annual.csv", "big_city_list.csv"];

test("numOrNull keeps gaps as null, never 0", () => {
  assert.strictEqual(C.numOrNull(""), null);
  assert.strictEqual(C.numOrNull(undefined), null);
  assert.strictEqual(C.numOrNull("0"), 0);
  assert.strictEqual(C.numOrNull("3.22"), 3.22);
  assert.strictEqual(C.numOrNull("n/a"), null);
});
test("filterRows matches every field", () => {
  const rows = [{ a: "1", b: "x" }, { a: "1", b: "y" }, { a: "2", b: "x" }];
  assert.deepStrictEqual(C.filterRows(rows, { a: "1", b: "x" }), [rows[0]]);
  assert.strictEqual(C.filterRows(rows, {}).length, 3);
});
test("pivotSeries aligns years, keeps key order and carries metadata", () => {
  const p = C.pivotSeries([
    { year: "2001", class: "b", value: "2", source_id: "S1" },
    { year: "2000", class: "a", value: "1", source_id: "S1" },
    { year: "2001", class: "a", value: "3", source_id: "S2" },
  ], { valueField: "value", meta: ["source_id"] });
  assert.deepStrictEqual(p.years, [2000, 2001]);
  assert.deepStrictEqual(p.keys, ["b", "a"]);
  assert.deepStrictEqual(p.values.b, [null, 2]);
  assert.deepStrictEqual(p.values.a, [1, 3]);
  assert.deepStrictEqual(p.meta.a.source_id, ["S1", "S2"]);
  assert.strictEqual(p.raw.a[0].value, "1");
});
test("pivotSeries accepts a composite key function", () => {
  const p = C.pivotSeries([{ year: "2000", class: "x", type: "house", v: "4" }], { keyFn: (r) => r.class + "|" + r.type, valueField: "v" });
  assert.deepStrictEqual(p.keys, ["x|house"]);
  assert.deepStrictEqual(p.values["x|house"], [4]);
});
test("sumSeries and percentShare: missing stays missing", () => {
  assert.deepStrictEqual(C.sumSeries([[1, null], [2, 2]]), [3, 2]);
  assert.deepStrictEqual(C.sumSeries([[null, null], [null, 2]]), [null, 2]);
  assert.deepStrictEqual(C.percentShare([1, 2, null], [4, 0, 4]), [25, null, null]);
  assert.deepStrictEqual(C.percentShare([1, 1], [3, 3], 0), [33, 33]);
});
test("basisRanges groups contiguous proxy and direct years", () => {
  assert.deepStrictEqual(C.basisRanges([2007, 2008, 2009, 2010, 2011], ["proxy", "proxy", "direct", "direct", "direct"]),
    [{ basis: "proxy", start: 2007, end: 2008 }, { basis: "direct", start: 2009, end: 2011 }]);
  assert.deepStrictEqual(C.basisRanges([2000, 2001, 2002], ["proxy", "direct", "proxy"]).map((r) => r.basis), ["proxy", "direct", "proxy"]);
});
test("csvWithSourceIds appends a source_id column from rows, arrays, a constant or a fallback", () => {
  const t = { header: ["year", "v"], rows: [[2000, 1], [2001, 2]] };
  assert.deepStrictEqual(C.csvWithSourceIds(t, "S41"), { header: ["year", "v", "source_id"], rows: [[2000, 1, "S41"], [2001, 2, "S41"]] });
  assert.deepStrictEqual(C.csvWithSourceIds(Object.assign({}, t, { sourceId: ["S1", "S2"] }), "S41").rows.map((r) => r[2]), ["S1", "S2"]);
  assert.deepStrictEqual(C.csvWithSourceIds(Object.assign({}, t, { sourceId: (r) => (r[0] === 2001 ? "S43" : "S41") })).rows.map((r) => r[2]), ["S41", "S43"]);
  assert.deepStrictEqual(C.csvWithSourceIds(Object.assign({}, t, { sourceId: "S29" })).rows.map((r) => r[2]), ["S29", "S29"]);
  assert.deepStrictEqual(C.csvWithSourceIds(t).rows.map((r) => r[2]), ["", ""]);
});
test("housingVsPopulation splits flats and houses with their per-row source ids", () => {
  const rows = C.parseCsv("year,class,measure,value,source_id,notes\n2000,big_cities,flats_per_1000,3.22,S41;S42,\n2009,big_cities,flats_per_1000,5.2,S43,\n2000,big_cities,houses_per_1000,0.61,S42,\n");
  const v = C.housingVsPopulation(rows, "flats_per_1000");
  assert.deepStrictEqual(v.keys, ["big_cities|flats_per_1000"]);
  assert.deepStrictEqual(v.values["big_cities|flats_per_1000"], [3.22, 5.2]);
  assert.deepStrictEqual(v.meta["big_cities|flats_per_1000"].source_id, ["S41;S42", "S43"]);
  assert.strictEqual(C.housingVsPopulation(rows).keys.length, 2);
});
test("europeByGeo filters indicator and sex", () => {
  const rows = C.parseCsv("geo,geo_name,year,indicator,sex,value,source_id\nPL,Poland,2000,life_expectancy_at_birth,total,73.8,S32\nPL,Poland,2000,life_expectancy_at_birth,men,69.6,S32\nCZ,Czechia,2000,life_expectancy_at_birth,total,75.1,S32\n");
  const e = C.europeByGeo(rows, "life_expectancy_at_birth", "total");
  assert.deepStrictEqual(e.keys, ["PL", "CZ"]);
  assert.deepStrictEqual(e.values.PL, [73.8]);
  assert.strictEqual(e.meta.CZ.geo_name[0], "Czechia");
});
test("bigCities sorts by population and drops missing values", () => {
  const rows = C.parseCsv("unit_id,city,population_latest_year,latest_year,source_id\n2,B,200,2025,S1\n1,A,500,2025,S1\n3,C,,2025,S1\n");
  const b = C.bigCities(rows);
  assert.deepStrictEqual(b.map((c) => c.city), ["A", "B"]);
  assert.deepStrictEqual(b[0], { unit_id: "1", city: "A", population: 500, year: 2025, source_id: "S1" });
});

test("real data: the 8 shipped CSVs are byte-identical to the processed research files", () => {
  REAL_FILES.forEach((f) => {
    const there = path.join(__dirname, "..", "data", "real", f);
    assert.ok(fs.existsSync(there), f);
    assert.ok(fs.readFileSync(there).equals(fs.readFileSync(research(f))), `${f} must be a verbatim copy`);
  });
});
test("real data: every file keeps a source_id column, no demo flag", () => {
  REAL_FILES.forEach((f) => {
    const rows = real(f);
    assert.ok(rows.length > 0, f);
    assert.ok("source_id" in rows[0], f + " has source_id");
    assert.ok(!("demo_flag" in rows[0]), f + " has no demo_flag");
    rows.forEach((r) => assert.ok(/^S\d+(;S\d+)*$/.test(r.source_id), `${f}: bad source_id "${r.source_id}"`));
  });
});
test("real data: population by class, 2000-2025", () => {
  const p = C.populationByClass(real("population_by_class.csv"));
  assert.deepStrictEqual(p.years, Array.from({ length: 26 }, (_, i) => 2000 + i));
  assert.deepStrictEqual(p.keys, ["big_cities", "small_cities", "villages"]);
  assert.strictEqual(p.values.big_cities[0], 10614664);
  assert.strictEqual(p.values.villages[25], 15180106);
  assert.ok(p.values.big_cities[25] < p.values.big_cities[0], "big cities lost population");
  assert.ok(p.values.villages[25] > p.values.villages[0], "villages gained population");
  assert.deepStrictEqual(C.indexSeries(p.values.big_cities, 0).slice(-1), [95]);
});
test("real data: completions separate proxy (2000-2008) from direct (2009-2025)", () => {
  const c = C.completionsByClass(real("housing_completions_by_class.csv"));
  const house = c.values["big_cities|house"], basis = c.meta["big_cities|house"].basis;
  assert.deepStrictEqual(basis.slice(0, 2), [null, null]);
  assert.strictEqual(basis[c.years.indexOf(2008)], null);
  assert.strictEqual(basis[c.years.indexOf(2009)], "direct");
  assert.strictEqual(basis[c.years.indexOf(2025)], "direct");
  assert.strictEqual(house[c.years.indexOf(2008)], null, "no direct house value before 2009");
  assert.strictEqual(c.meta["big_cities|house"].source_id[c.years.indexOf(2009)], "S43");
  assert.strictEqual(c.meta["big_cities|house_proxy_individual"].basis[0], "proxy");
  assert.strictEqual(c.meta["big_cities|house_proxy_individual"].source_id[0], "S42");
  const total = c.values["big_cities|total"];
  assert.strictEqual(total[c.years.indexOf(2000)], 40696);
  assert.ok(total.every((v) => v !== null), "the direct total covers every year");
});
test("real data: houses vs population per 1000 and the 2000-2008 proxy band", () => {
  const rows = real("housing_vs_population.csv");
  const f = C.housingVsPopulation(rows, "flats_per_1000");
  const i2000 = f.years.indexOf(2000), i2025 = f.years.indexOf(2025);
  assert.strictEqual(f.values["big_cities|flats_per_1000"][i2000], 3.22);
  assert.strictEqual(f.values["big_cities|flats_per_1000"][i2025], 6.84);
  assert.strictEqual(f.meta["big_cities|flats_per_1000"].source_id[i2000], "S41;S42");
  assert.strictEqual(f.meta["big_cities|flats_per_1000"].source_id[i2025], "S43");
  const ranges = C.basisRanges(f.years, f.years.map((y) => (y <= 2008 ? "proxy" : "direct")));
  assert.deepStrictEqual(ranges, [{ basis: "proxy", start: 2000, end: 2008 }, { basis: "direct", start: 2009, end: 2025 }]);
});
test("real data: Europe index for PL and EU-27, 2000-2025", () => {
  const e = C.europeByGeo(real("europe_annual.csv"), "population_index_2000_eq_100", "total");
  assert.deepStrictEqual(e.keys.slice().sort(), ["CZ", "DE", "EU27_2020", "HU", "LT", "PL", "RO", "SK"]);
  assert.strictEqual(e.values.PL[e.years.indexOf(2025)], 95.39);
  assert.strictEqual(e.values.EU27_2020[e.years.indexOf(2025)], 105.32);
  assert.strictEqual(e.meta.PL.geo_name[0], "Poland");
  assert.strictEqual(e.meta.PL.source_id[0], "S29");
});
test("real data: 34 big cities, sized by real 2025 population", () => {
  const cities = C.bigCities(real("big_city_list.csv"));
  assert.strictEqual(cities.length, 34);
  assert.deepStrictEqual(cities[0], { unit_id: "071412865011", city: "Warszawa", population: 1866729, year: 2025, source_id: "S1" });
  assert.ok(cities.every((c) => c.year === 2025 && c.source_id === "S1" && c.population > 100000));
  assert.strictEqual(new Set(cities.map((c) => c.city)).size, 34);
  const geo = JSON.parse(data("geo/cities.geojson")).features.filter((f) => f.properties.big_city);
  assert.strictEqual(geo.length, cities.length);
  cities.forEach((c) => assert.ok(geo.some((f) => f.properties.name === c.city), c.city + " has a real city point"));
});
