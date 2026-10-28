"use strict";

const API = "https://api.open-meteo.com/v1/forecast" +
  "?latitude=51.08&longitude=16.88" +
  "&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,precipitation" +
  "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum" +
  "&timezone=Europe%2FWarsaw&forecast_days=7";

// WMO weather interpretation codes -> emoji + text
const WMO = {
  0: ["☀️", "Clear sky"], 1: ["🌤️", "Mainly clear"], 2: ["⛅", "Partly cloudy"], 3: ["☁️", "Overcast"],
  45: ["🌫️", "Fog"], 48: ["🌫️", "Rime fog"],
  51: ["🌦️", "Light drizzle"], 53: ["🌦️", "Drizzle"], 55: ["🌧️", "Dense drizzle"],
  56: ["🌧️", "Freezing drizzle"], 57: ["🌧️", "Heavy freezing drizzle"],
  61: ["🌧️", "Light rain"], 63: ["🌧️", "Rain"], 65: ["🌧️", "Heavy rain"],
  66: ["🌧️", "Freezing rain"], 67: ["🌧️", "Heavy freezing rain"],
  71: ["🌨️", "Light snow"], 73: ["🌨️", "Snow"], 75: ["❄️", "Heavy snow"], 77: ["❄️", "Snow grains"],
  80: ["🌦️", "Light showers"], 81: ["🌧️", "Showers"], 82: ["⛈️", "Violent showers"],
  85: ["🌨️", "Snow showers"], 86: ["❄️", "Heavy snow showers"],
  95: ["⛈️", "Thunderstorm"], 96: ["⛈️", "Thunderstorm with hail"], 99: ["⛈️", "Severe thunderstorm with hail"]
};

function describe(code) {
  return WMO[code] || ["❓", "Unknown (" + code + ")"];
}

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
}

function compass(deg) {
  const dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"];
  return dirs[Math.round(deg / 45) % 8];
}

function showError(msg) {
  document.getElementById("loading").hidden = true;
  const err = document.getElementById("error");
  err.textContent = msg;
  err.hidden = false;
}

function render(data) {
  const c = data.current, cu = data.current_units, d = data.daily;
  if (!c || !d || !d.time || !d.time.length) throw new Error("Unexpected response from the weather service.");

  const [icon, text] = describe(c.weather_code);
  const box = document.getElementById("current");
  box.textContent = "";
  const now = el("div", "now");
  now.append(el("div", "icon", icon));
  const main = el("div");
  main.append(el("div", "temp", Math.round(c.temperature_2m) + cu.temperature_2m));
  main.append(el("div", "cond", text));
  now.append(main);
  box.append(now);
  const stats = el("ul", "stats");
  const items = [
    ["Feels like", Math.round(c.apparent_temperature) + cu.apparent_temperature],
    ["Wind", Math.round(c.wind_speed_10m) + " " + cu.wind_speed_10m + " " + compass(c.wind_direction_10m)],
    ["Precipitation", c.precipitation + " " + cu.precipitation]
  ];
  for (const [k, v] of items) {
    const li = el("li");
    li.append(el("b", null, k), document.createTextNode(v));
    stats.append(li);
  }
  box.append(stats);
  box.append(el("p", "muted foot", "Updated " + c.time.replace("T", " ") + " (Europe/Warsaw)"));

  const list = document.getElementById("days");
  list.textContent = "";
  d.time.forEach((day, i) => {
    const [ic, tx] = describe(d.weather_code[i]);
    const date = new Date(day + "T12:00:00");
    const label = i === 0 ? "Today" : date.toLocaleDateString("en-GB", { weekday: "short", day: "numeric" });
    const li = el("li");
    li.append(el("span", "d", label), el("span", "i", ic), el("span", "c", tx));
    const t = el("span", "t", Math.round(d.temperature_2m_max[i]) + "° ");
    t.append(el("span", null, Math.round(d.temperature_2m_min[i]) + "°"));
    li.append(t);
    list.append(li);
  });

  document.getElementById("loading").hidden = true;
  box.hidden = false;
  document.getElementById("forecast").hidden = false;
}

async function load() {
  try {
    const res = await fetch(API);
    if (!res.ok) throw new Error("Weather service returned HTTP " + res.status + ".");
    render(await res.json());
  } catch (e) {
    showError("Could not load the weather for Smolec. " + (e && e.message ? e.message : "") + " Please check your connection and reload.");
  }
}

load();
