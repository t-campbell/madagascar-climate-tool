import { baselineMonth, expectedFinalMonth, rainfallDifference } from "./recent.js";
import { displayMonth, language, subscribeLanguageChange, t } from "./i18n.js";

const MONTHS = Array.from({ length: 12 }, (_, index) => index);
// The 1991–2020 national CHIRPS land-cell baseline peaks at 800.1 mm/month.
const RAIN_AXIS_MAX_MM = 1000;
const TEMPERATURE_AXIS_MIN_C = 0;
const TEMPERATURE_AXIS_MAX_C = 40;
const MADAGASCAR_BOUNDS = { south: -26, north: -11, west: 43, east: 51 };

const locale = () => language() === "mg" ? "mg-MG" : "en";
const formatMillimeters = (value) => (Math.round(value) || 0).toLocaleString(locale());
const formatDays = (value) => (Math.round(value) || 0).toLocaleString(locale());
const formatTemperature = (value) => (Math.round(value) || 0).toLocaleString(locale());

const elements = {
  report: document.querySelector("#report"),
  placeForm: document.querySelector("#place-form"),
  placeInput: document.querySelector("#place-input"),
  suggestions: document.querySelector("#suggestions"),
  coordinateForm: document.querySelector("#coordinate-form"),
  locationButton: document.querySelector("#location-button"),
  formStatus: document.querySelector("#form-status"),
  reportRegion: document.querySelector("#report-region"),
  reportTitle: document.querySelector("#report-title"),
  reportCoordinates: document.querySelector("#report-coordinates"),
  annualRain: document.querySelector("#annual-rain"),
  rainSeason: document.querySelector("#rain-season"),
  dryRisk: document.querySelector("#dry-risk"),
  drySeason: document.querySelector("#dry-season"),
  warmestHigh: document.querySelector("#warmest-high"),
  warmestMonth: document.querySelector("#warmest-month"),
  coolestLow: document.querySelector("#coolest-low"),
  coolestMonth: document.querySelector("#coolest-month"),
  rainChart: document.querySelector("#rain-chart"),
  temperatureChart: document.querySelector("#temperature-chart"),
  showRainfall: document.querySelector("#show-rainfall"),
  showRainyDays: document.querySelector("#show-rainy-days"),
  showHeavyDays: document.querySelector("#show-heavy-days"),
  rainTableBody: document.querySelector("#rain-table tbody"),
  temperatureTableBody: document.querySelector("#temperature-table tbody"),
  interpretationList: document.querySelector("#interpretation-list"),
  cellDetails: document.querySelector("#cell-details"),
  offlineStatus: document.querySelector("#offline-status"),
  recentChart: document.querySelector("#recent-chart"),
  recentTableBody: document.querySelector("#recent-table tbody"),
  recentStatus: document.querySelector("#recent-status"),
  recentFreshness: document.querySelector("#recent-freshness"),
};

let manifest;
let locationRequestId = 0;
let latestRainChartData = null;
let latestReport = null;
let offlineStatusKey = "checkingOffline";
const placeShards = new Map();

function normalizeText(value) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function tileIdFor(lat, lon) {
  const latOrigin = Math.floor(lat);
  const lonOrigin = Math.floor(lon);
  const latPrefix = latOrigin < 0 ? "S" : "N";
  const lonPrefix = lonOrigin < 0 ? "W" : "E";
  return `${latPrefix}${String(Math.abs(latOrigin)).padStart(2, "0")}_${lonPrefix}${String(Math.abs(lonOrigin)).padStart(3, "0")}`;
}

function withinMadagascar(lat, lon) {
  return lat >= MADAGASCAR_BOUNDS.south && lat <= MADAGASCAR_BOUNDS.north && lon >= MADAGASCAR_BOUNDS.west && lon <= MADAGASCAR_BOUNDS.east;
}

function distanceKm(aLat, aLon, bLat, bLon) {
  const rad = Math.PI / 180;
  const a = Math.sin((bLat - aLat) * rad / 2) ** 2
    + Math.cos(aLat * rad) * Math.cos(bLat * rad) * Math.sin((bLon - aLon) * rad / 2) ** 2;
  return 12742 * Math.asin(Math.sqrt(a));
}

async function loadTile(tileId, template, errorKey) {
  const path = template.replace("{tileId}", tileId);
  const response = await fetch(path);
  if (!response.ok) throw new Error(t(errorKey));
  return response.json();
}

function nearestInTile(tile, lat, lon) {
  let nearest = null;
  for (const cell of tile.cells) {
    const cellLat = tile.lat[cell[0]];
    const cellLon = tile.lon[cell[1]];
    const distance = distanceKm(lat, lon, cellLat, cellLon);
    if (!nearest || distance < nearest.distance) nearest = { cell, lat: cellLat, lon: cellLon, distance };
  }
  return nearest;
}

async function loadCoordinate(lat, lon, place = null) {
  const requestId = ++locationRequestId;
  if (!withinMadagascar(lat, lon)) {
    throw new Error(t("outsideCoverage"));
  }
  const tileId = tileIdFor(lat, lon);
  const [rainTile, temperatureTile] = await Promise.all([
    loadTile(tileId, manifest.tileTemplate, "noCell"),
    loadTile(tileId, manifest.temperatureTileTemplate, "noTemperatureCell"),
  ]);
  const rain = nearestInTile(rainTile, lat, lon);
  const temperature = nearestInTile(temperatureTile, lat, lon);
  if (!rain || rain.distance > manifest.maxCellDistanceKm) {
    throw new Error(t("noCell12"));
  }
  if (!temperature || temperature.distance > manifest.maxTemperatureCellDistanceKm) {
    throw new Error(t("noTemperatureCell20"));
  }
  if (requestId !== locationRequestId) return;
  const nearest = { rain, temperature, recent: null, recentError: false };
  const request = { requestedLat: lat, requestedLon: lon, tileId, place };
  renderReport(nearest, request);
  if (manifest.recentRainfall) {
    try {
      const tile = await loadTile(tileId, manifest.recentRainfall.tileTemplate, "recentUnavailable");
      if (tile.release !== manifest.recentRainfall.release
        || JSON.stringify(tile.months) !== JSON.stringify(manifest.recentRainfall.months)) throw new Error("wrong recent rainfall release");
      const recent = nearestInTile(tile, lat, lon);
      if (!recent || Math.abs(recent.lat - rain.lat) > 0.00001 || Math.abs(recent.lon - rain.lon) > 0.00001) throw new Error("recent and historical cells differ");
      nearest.recent = { ...recent, months: tile.months };
    } catch (error) {
      nearest.recentError = true;
    }
    if (requestId === locationRequestId) renderReport(nearest, request);
  }
}

function shardFor(query) {
  let match = null;
  for (let length = 3; length <= query.length; length += 1) {
    const prefix = query.slice(0, length);
    if (manifest.searchPrefixesSet.has(prefix)) match = prefix;
  }
  return match;
}

async function matchingPlaces(query) {
  const normalized = normalizeText(query);
  if (normalized.length < 3) return [];
  const prefix = shardFor(normalized);
  if (!prefix) return [];
  if (!placeShards.has(prefix)) {
    const pending = fetch(manifest.placesTemplate.replace("{prefix}", prefix))
      .then((response) => {
        if (!response.ok) throw new Error(t("placeUnavailable"));
        return response.json();
      }).then((data) => data.places);
    placeShards.set(prefix, pending);
    pending.catch(() => placeShards.delete(prefix));
  }
  const places = await placeShards.get(prefix);
  return places.filter((place) =>
    [place.name, ...place.aliases].some((name) => normalizeText(name).startsWith(normalized))
  ).sort((a, b) => {
    const exact = (place) => [place.name, ...place.aliases].some((name) => normalizeText(name) === normalized);
    return Number(exact(b)) - Number(exact(a)) || b.population - a.population || a.name.localeCompare(b.name);
  });
}

function renderSuggestions(matches) {
  elements.suggestions.replaceChildren();
  if (!matches.length) {
    elements.suggestions.hidden = true;
    return;
  }
  for (const place of matches.slice(0, 6)) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "suggestion";
    button.setAttribute("role", "option");
    button.textContent = place.name;
    const context = document.createElement("small");
    context.textContent = [place.district, place.region].filter(Boolean).join(", ") || "Madagascar";
    button.append(context);
    button.addEventListener("click", () => choosePlace(place));
    elements.suggestions.append(button);
  }
  elements.suggestions.hidden = false;
}

async function updateSuggestions() {
  const query = elements.placeInput.value;
  const normalized = normalizeText(query);
  if (normalized.length < 3) {
    renderSuggestions([]);
    elements.formStatus.textContent = query ? t("typeThree") : "";
    return [];
  }
  if (!shardFor(normalized)) {
    renderSuggestions([]);
    elements.formStatus.textContent = manifest.searchPrefixes.some((prefix) => prefix.startsWith(normalized))
      ? t("keepTyping") : t("noMatch");
    return [];
  }
  try {
    const matches = await matchingPlaces(query);
    if (elements.placeInput.value !== query) return [];
    renderSuggestions(matches);
    elements.formStatus.textContent = matches.length ? ""
      : manifest.searchPrefixes.some((prefix) => prefix.startsWith(normalized))
        ? t("keepTyping") : t("noMatch");
    return matches;
  } catch (error) {
    if (elements.placeInput.value === query) elements.formStatus.textContent = error.message;
    return [];
  }
}

async function choosePlace(place) {
  elements.suggestions.hidden = true;
  elements.placeInput.value = place.name;
  elements.formStatus.textContent = t("loadingRainfall");
  try {
    await loadCoordinate(place.lat, place.lon, place);
    elements.formStatus.textContent = "";
  } catch (error) {
    elements.formStatus.textContent = error.message;
  }
}

function svgElement(name, attributes = {}) {
  const node = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
  return node;
}

function renderRainChart(values, rainyDays, heavyRainDays) {
  latestRainChartData = { values, rainyDays, heavyRainDays };
  const showRainfall = elements.showRainfall.checked;
  const showRainyDays = elements.showRainyDays.checked;
  const showHeavyDays = elements.showHeavyDays.checked;
  const width = 760;
  const height = 250;
  const margin = { top: 22, right: 48, bottom: 34, left: 44 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const maximum = RAIN_AXIS_MAX_MM;
  const svg = svgElement("svg", { viewBox: `0 0 ${width} ${height}`, "aria-hidden": "true" });
  const rainY = (value) => margin.top + plotHeight * (1 - value / maximum);
  const daysY = (value) => margin.top + plotHeight * (1 - value / 31);

  for (let tick = 0; tick <= 4; tick += 1) {
    const value = maximum * tick / 4;
    const y = rainY(value);
    svg.append(svgElement("line", { x1: margin.left, x2: width - margin.right, y1: y, y2: y, class: "axis" }));
    const label = svgElement("text", { x: margin.left - 8, y: y + 4, "text-anchor": "end" });
    label.textContent = `${Math.round(value)}`;
    svg.append(label);
    const dayLabel = svgElement("text", { x: width - margin.right + 8, y: y + 4 });
    dayLabel.textContent = `${Math.round(31 * tick / 4)}`;
    svg.append(dayLabel);
  }

  const slot = plotWidth / values.length;
  values.forEach((value, index) => {
    if (showRainfall) {
      const barWidth = showHeavyDays ? slot * 0.48 : slot * 0.68;
      const rect = svgElement("rect", {
        x: margin.left + index * slot + (showHeavyDays ? slot * 0.12 : slot * 0.16),
        y: rainY(value),
        width: barWidth,
        height: value / maximum * plotHeight,
        rx: 2,
        class: "rain-bar",
      });
      const title = svgElement("title");
      title.textContent = t("rainTooltip", { month: displayMonth(index), value: formatMillimeters(value) });
      rect.append(title);
      svg.append(rect);
    }
    if (showHeavyDays) {
      const barWidth = showRainfall ? slot * 0.20 : slot * 0.42;
      const rect = svgElement("rect", {
        x: margin.left + index * slot + (showRainfall ? slot * 0.64 : slot * 0.29),
        y: daysY(heavyRainDays[index]),
        width: barWidth,
        height: heavyRainDays[index] / 31 * plotHeight,
        rx: 2,
        class: "heavy-days-bar",
      });
      const title = svgElement("title");
      title.textContent = t("heavyTooltip", { month: displayMonth(index), value: formatDays(heavyRainDays[index]) });
      rect.append(title);
      svg.append(rect);
    }
    const label = svgElement("text", { x: margin.left + index * slot + slot / 2, y: height - 12, "text-anchor": "middle" });
    label.textContent = displayMonth(index);
    svg.append(label);
  });
  if (showRainyDays) {
    const points = rainyDays.map((days, index) => ({
      x: margin.left + (index + 0.5) * slot,
      y: daysY(days),
    }));
    svg.append(svgElement("polyline", {
      points: points.map(({ x, y }) => `${x},${y}`).join(" "),
      class: "rain-days-line",
    }));
    points.forEach(({ x, y }, index) => {
      const dot = svgElement("circle", { cx: x, cy: y, r: 4, class: "rain-days-dot" });
      const title = svgElement("title");
      title.textContent = t("rainyTooltip", { month: displayMonth(index), value: formatDays(rainyDays[index]) });
      dot.append(title);
      svg.append(dot);
    });
  }
  const rainUnit = svgElement("text", { x: margin.left - 8, y: 13, "text-anchor": "end" });
  rainUnit.textContent = "mm";
  svg.append(rainUnit);
  const daysUnit = svgElement("text", { x: width - margin.right + 8, y: 13 });
  daysUnit.textContent = t("daysUnit");
  svg.append(daysUnit);
  elements.rainChart.replaceChildren(svg);
  const visible = [
    showRainfall && t("visibleRainfall"),
    showRainyDays && t("visibleRainy"),
    showHeavyDays && t("visibleHeavy"),
  ].filter(Boolean);
  elements.rainChart.setAttribute("aria-label", visible.length
    ? t("chartVisible", { series: visible.join(", ") })
    : t("chartNone"));
}

function renderTemperatureChart(minimum, maximum) {
  const width = 760;
  const height = 250;
  const margin = { top: 22, right: 24, bottom: 34, left: 44 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const slot = plotWidth / minimum.length;
  const y = (value) => margin.top + plotHeight * (
    1 - (value - TEMPERATURE_AXIS_MIN_C) / (TEMPERATURE_AXIS_MAX_C - TEMPERATURE_AXIS_MIN_C)
  );
  const svg = svgElement("svg", { viewBox: `0 0 ${width} ${height}`, "aria-hidden": "true" });

  for (let value = TEMPERATURE_AXIS_MIN_C; value <= TEMPERATURE_AXIS_MAX_C; value += 10) {
    const tickY = y(value);
    svg.append(svgElement("line", { x1: margin.left, x2: width - margin.right, y1: tickY, y2: tickY, class: "axis" }));
    const label = svgElement("text", { x: margin.left - 8, y: tickY + 4, "text-anchor": "end" });
    label.textContent = `${value}`;
    svg.append(label);
  }

  const upper = maximum.map((value, index) => `${margin.left + (index + 0.5) * slot},${y(value)}`);
  const lower = minimum.map((value, index) => `${margin.left + (index + 0.5) * slot},${y(value)}`).reverse();
  svg.append(svgElement("polygon", { points: [...upper, ...lower].join(" "), class: "temperature-band" }));
  for (const [values, className, tooltipKey] of [
    [maximum, "temperature-high-line", "temperatureHighTooltip"],
    [minimum, "temperature-low-line", "temperatureLowTooltip"],
  ]) {
    const points = values.map((value, index) => ({
      x: margin.left + (index + 0.5) * slot,
      y: y(value),
    }));
    svg.append(svgElement("polyline", {
      points: points.map(({ x, y: pointY }) => `${x},${pointY}`).join(" "),
      class: className,
    }));
    points.forEach(({ x, y: pointY }, index) => {
      const dot = svgElement("circle", { cx: x, cy: pointY, r: 4, class: `${className}-dot` });
      const title = svgElement("title");
      title.textContent = t(tooltipKey, { month: displayMonth(index), value: formatTemperature(values[index]) });
      dot.append(title);
      svg.append(dot);
    });
  }
  MONTHS.forEach((index) => {
    const label = svgElement("text", { x: margin.left + (index + 0.5) * slot, y: height - 12, "text-anchor": "middle" });
    label.textContent = displayMonth(index);
    svg.append(label);
  });
  const unit = svgElement("text", { x: margin.left - 8, y: 13, "text-anchor": "end" });
  unit.textContent = "°C";
  svg.append(unit);
  elements.temperatureChart.replaceChildren(svg);
  elements.temperatureChart.setAttribute("aria-label", t("temperatureChartAria"));
}

for (const control of [elements.showRainfall, elements.showRainyDays, elements.showHeavyDays]) {
  control.addEventListener("change", () => {
    if (latestRainChartData) renderRainChart(
      latestRainChartData.values,
      latestRainChartData.rainyDays,
      latestRainChartData.heavyRainDays,
    );
  });
}

function buildInterpretation(rain, heavyRainDays, risk) {
  const annual = rain.reduce((sum, value) => sum + value, 0);
  const wetMonths = rain.filter((value) => value >= 150).length;
  const riskyMonths = risk.filter((value) => value >= 0.6).length;
  const notes = [];
  const mostHeavyDays = Math.max(...heavyRainDays);
  const heavyMonths = MONTHS.filter(
    (index) => heavyRainDays[index] >= mostHeavyDays - 0.5
  ).map(displayMonth);
  notes.push(t("interpretationHeavy", {
    months: heavyMonths.join(", "),
    days: formatDays(mostHeavyDays),
  }));
  if (wetMonths >= 8) {
    notes.push(t("interpretationWet"));
  } else if (wetMonths >= 4) {
    notes.push(t("interpretationSeason"));
  } else {
    notes.push(t("interpretationShort"));
  }
  if (riskyMonths >= 5) {
    notes.push(t("interpretationDry"));
  }
  if (annual > 2000) {
    notes.push(t("interpretationHighRain"));
  }
  return notes;
}

function renderRecent(nearest) {
  elements.recentChart.replaceChildren();
  elements.recentTableBody.replaceChildren();
  elements.recentStatus.classList.remove("stale");
  elements.recentFreshness.textContent = manifest.recentRainfall
    ? t("recentThrough", { date: manifest.recentRainfall.dataThrough }) : "";
  if (!nearest.recent) {
    elements.recentStatus.textContent = t(nearest.recentError ? "recentUnavailable"
      : manifest.recentRainfall ? "recentLoading" : "recentPending");
    return;
  }
  const [,, values, rainy, heavy] = nearest.recent.cell;
  const months = nearest.recent.months;
  const normals = months.map((period) => nearest.rain.cell[2][baselineMonth(period)]);
  const labels = months.map((period) => `${displayMonth(baselineMonth(period))} ${period.slice(2, 4)}`);
  const maximum = manifest.recentRainfall.axisMaxMm;
  const width = 760, height = 250;
  const margin = { left: 44, right: 24, top: 22, bottom: 34 };
  const plotHeight = height - margin.top - margin.bottom;
  const slot = (width - margin.left - margin.right) / months.length;
  const y = (value) => margin.top + plotHeight * (1 - value / maximum);
  const svg = svgElement("svg", { viewBox: `0 0 ${width} ${height}`, "aria-hidden": "true" });
  for (let tick = 0; tick <= 4; tick += 1) {
    const value = maximum * tick / 4, tickY = y(value);
    svg.append(svgElement("line", { x1: margin.left, x2: width - margin.right, y1: tickY, y2: tickY, class: "axis" }));
    const label = svgElement("text", { x: margin.left - 8, y: tickY + 4, "text-anchor": "end" });
    label.textContent = String(Math.round(value));
    svg.append(label);
  }
  values.forEach((value, index) => {
    const bar = svgElement("rect", { x: margin.left + (index + 0.16) * slot, y: y(value), width: slot * 0.68,
      height: plotHeight * value / maximum, rx: 2, class: "rain-bar" });
    const title = svgElement("title");
    title.textContent = t("recentTooltip", { month: labels[index], actual: formatMillimeters(value), normal: formatMillimeters(normals[index]) });
    bar.append(title);
    svg.append(bar);
    const label = svgElement("text", { x: margin.left + (index + 0.5) * slot, y: height - 12, "text-anchor": "middle" });
    label.textContent = labels[index];
    svg.append(label);
  });
  svg.append(svgElement("polyline", { points: normals.map((value, index) => `${margin.left + (index + 0.5) * slot},${y(value)}`).join(" "), class: "recent-normal-line" }));
  elements.recentChart.append(svg);
  elements.recentChart.setAttribute("aria-label", t("recentChartAria"));
  const stale = months.at(-1) < expectedFinalMonth();
  elements.recentStatus.classList.toggle("stale", stale);
  elements.recentStatus.textContent = t(stale ? "recentStale" : "recentAxis", { max: formatMillimeters(maximum) });
  const signed = (number) => `${Math.round(number) > 0 ? "+" : ""}${formatMillimeters(number)}`;
  elements.recentTableBody.replaceChildren(...months.map((period, index) => {
    const row = document.createElement("tr");
    const month = baselineMonth(period), difference = rainfallDifference(values[index], normals[index]);
    const change = `${signed(difference.mm)} mm${difference.percent === null ? "" : ` (${signed(difference.percent)}%)`}`;
    for (const value of [labels[index], `${formatMillimeters(values[index])} mm`, `${formatMillimeters(normals[index])} mm`, change,
      `${formatDays(rainy[index])} / ${formatDays(nearest.rain.cell[5][month])}`,
      `${formatDays(heavy[index])} / ${formatDays(nearest.rain.cell[6][month])}`]) {
      const cell = document.createElement("td"); cell.textContent = value; row.append(cell);
    }
    return row;
  }));
}

function renderReport(nearest, request) {
  latestReport = { nearest, request };
  const [,, rain, p10, p90, rainyDays, heavyRainDays, wetIntensity, dryRisk] = nearest.rain.cell;
  const [,, minimumTemperature, maximumTemperature] = nearest.temperature.cell;
  const wettestIndex = rain.indexOf(Math.max(...rain));
  const highestRiskIndex = dryRisk.indexOf(Math.max(...dryRisk));
  const highestHeavyIndex = heavyRainDays.indexOf(Math.max(...heavyRainDays));
  const annual = rain.reduce((sum, value) => sum + value, 0);
  const warmestIndex = maximumTemperature.indexOf(Math.max(...maximumTemperature));
  const coolestIndex = minimumTemperature.indexOf(Math.min(...minimumTemperature));

  elements.reportRegion.textContent = request.place
    ? [request.place.district, request.place.region].filter(Boolean).join(", ") || "Madagascar"
    : t("coordinateLookup");
  elements.reportTitle.textContent = request.place ? request.place.name : t("coordinateClimate");
  elements.reportCoordinates.textContent = t("requested", {
    lat: request.requestedLat.toFixed(4),
    lon: request.requestedLon.toFixed(4),
  });
  elements.annualRain.textContent = `${formatMillimeters(annual)} mm`;
  elements.rainSeason.textContent = t("seasonSummary", {
    wettest: displayMonth(wettestIndex),
    heavy: displayMonth(highestHeavyIndex),
  });
  elements.dryRisk.textContent = `${Math.round(dryRisk[highestRiskIndex] * 100)}%`;
  elements.drySeason.textContent = t("highestIn", { month: displayMonth(highestRiskIndex) });
  elements.warmestHigh.textContent = `${formatTemperature(maximumTemperature[warmestIndex])} °C`;
  elements.warmestMonth.textContent = t("highestIn", { month: displayMonth(warmestIndex) });
  elements.coolestLow.textContent = `${formatTemperature(minimumTemperature[coolestIndex])} °C`;
  elements.coolestMonth.textContent = t("lowestIn", { month: displayMonth(coolestIndex) });
  elements.cellDetails.textContent = t("cellDetails", {
    rainLat: nearest.rain.lat.toFixed(4),
    rainLon: nearest.rain.lon.toFixed(4),
    rainDistance: nearest.rain.distance.toFixed(1),
    temperatureLat: nearest.temperature.lat.toFixed(4),
    temperatureLon: nearest.temperature.lon.toFixed(4),
    temperatureDistance: nearest.temperature.distance.toFixed(1),
  });

  renderRecent(nearest);
  renderRainChart(rain, rainyDays, heavyRainDays);
  renderTemperatureChart(minimumTemperature, maximumTemperature);
  elements.rainTableBody.replaceChildren(...MONTHS.map((index) => {
    const row = document.createElement("tr");
    for (const value of [
      displayMonth(index),
      `${formatMillimeters(rain[index])} mm`,
      `${formatMillimeters(p10[index])}–${formatMillimeters(p90[index])} mm`,
      formatDays(rainyDays[index]),
      formatDays(heavyRainDays[index]),
      `${formatMillimeters(wetIntensity[index])} mm`,
    ]) {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    }
    return row;
  }));
  elements.temperatureTableBody.replaceChildren(...MONTHS.map((index) => {
    const row = document.createElement("tr");
    for (const value of [
      displayMonth(index),
      `${formatTemperature(minimumTemperature[index])} °C`,
      `${formatTemperature(maximumTemperature[index])} °C`,
    ]) {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    }
    return row;
  }));
  elements.interpretationList.replaceChildren(...buildInterpretation(rain, heavyRainDays, dryRisk).map((note) => {
    const item = document.createElement("li");
    item.textContent = note;
    return item;
  }));
  elements.report.setAttribute("aria-busy", "false");
}

subscribeLanguageChange(() => {
  if (latestReport) renderReport(latestReport.nearest, latestReport.request);
  elements.offlineStatus.textContent = t(offlineStatusKey);
});

elements.placeInput.addEventListener("input", updateSuggestions);
elements.placeForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const matches = await updateSuggestions();
  if (!matches.length) return;
  await choosePlace(matches[0]);
});

elements.coordinateForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(elements.coordinateForm);
  const lat = Number(form.get("latitude"));
  const lon = Number(form.get("longitude"));
  elements.formStatus.textContent = t("loadingClimate");
  try {
    await loadCoordinate(lat, lon);
    elements.formStatus.textContent = "";
  } catch (error) {
    elements.formStatus.textContent = error.message;
  }
});

elements.locationButton.addEventListener("click", () => {
  if (!navigator.geolocation) {
    elements.formStatus.textContent = t("deviceUnsupported");
    return;
  }
  elements.formStatus.textContent = t("requestingLocation");
  navigator.geolocation.getCurrentPosition(
    async ({ coords }) => {
      document.querySelector("#latitude").value = coords.latitude.toFixed(5);
      document.querySelector("#longitude").value = coords.longitude.toFixed(5);
      try {
        await loadCoordinate(coords.latitude, coords.longitude);
        elements.formStatus.textContent = "";
      } catch (error) {
        elements.formStatus.textContent = error.message;
      }
    },
    () => { elements.formStatus.textContent = t("locationUnavailable"); },
    { enableHighAccuracy: false, timeout: 12000, maximumAge: 600000 },
  );
});

async function initialize() {
  try {
    const manifestResponse = await fetch("data/manifest.json", { cache: "no-cache" });
    if (!manifestResponse.ok) throw new Error(t("manifestUnavailable"));
    manifest = await manifestResponse.json();
    if (manifest.status !== "climate-baseline") throw new Error(t("unexpectedData"));
    manifest.searchPrefixesSet = new Set(manifest.searchPrefixes);
    await loadCoordinate(manifest.defaultLocation.lat, manifest.defaultLocation.lon, manifest.defaultLocation);
  } catch (error) {
    elements.formStatus.textContent = t("dataLoadFailed", { message: error.message });
    elements.report.setAttribute("aria-busy", "false");
  }

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("sw.js")
      .then(() => {
        offlineStatusKey = "offlineReady";
        elements.offlineStatus.textContent = t(offlineStatusKey);
      })
      .catch(() => {
        offlineStatusKey = "offlineUnavailable";
        elements.offlineStatus.textContent = t(offlineStatusKey);
      });
  } else {
    offlineStatusKey = "offlineUnsupported";
    elements.offlineStatus.textContent = t(offlineStatusKey);
  }
}

initialize();
