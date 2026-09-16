const MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"];
const MADAGASCAR_BOUNDS = { south: -26, north: -11, west: 43, east: 51 };

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
  reportThrough: document.querySelector("#report-through"),
  releaseType: document.querySelector("#release-type"),
  annualRain: document.querySelector("#annual-rain"),
  rainSeason: document.querySelector("#rain-season"),
  dryRisk: document.querySelector("#dry-risk"),
  drySeason: document.querySelector("#dry-season"),
  tempRange: document.querySelector("#temp-range"),
  rainChart: document.querySelector("#rain-chart"),
  temperatureChart: document.querySelector("#temperature-chart"),
  rainTableBody: document.querySelector("#rain-table tbody"),
  currentCopy: document.querySelector("#current-copy"),
  anomalyValue: document.querySelector("#anomaly-value"),
  interpretationList: document.querySelector("#interpretation-list"),
  cellDetails: document.querySelector("#cell-details"),
  offlineStatus: document.querySelector("#offline-status"),
};

let manifest;
let places = [];

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

function distanceSquared(aLat, aLon, bLat, bLon) {
  const latitudeScale = Math.cos(((aLat + bLat) / 2) * Math.PI / 180);
  return (aLat - bLat) ** 2 + ((aLon - bLon) * latitudeScale) ** 2;
}

async function loadTile(tileId) {
  const path = manifest.tileTemplate.replace("{tileId}", tileId);
  const response = await fetch(path);
  if (!response.ok) throw new Error(`No prototype tile is available for ${tileId}.`);
  return response.json();
}

async function loadCoordinate(lat, lon, preferredId = null) {
  if (!withinMadagascar(lat, lon)) {
    throw new Error("Those coordinates fall outside the Madagascar coverage box.");
  }
  const tileId = tileIdFor(lat, lon);
  const tile = await loadTile(tileId);
  const location = preferredId
    ? tile.locations.find((item) => item.id === preferredId)
    : [...tile.locations].sort((a, b) =>
        distanceSquared(lat, lon, a.coordinates.lat, a.coordinates.lon) -
        distanceSquared(lat, lon, b.coordinates.lat, b.coordinates.lon)
      )[0];
  if (!location) throw new Error("That tile contains no prototype location.");
  renderReport(location, { requestedLat: lat, requestedLon: lon, tileId });
}

function matchingPlaces(query) {
  const normalized = normalizeText(query);
  if (!normalized) return [];
  return places.filter((place) => {
    const names = [place.name, ...place.aliases, place.district, place.region];
    return names.some((name) => normalizeText(name).includes(normalized));
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
    button.innerHTML = `${place.name}<small>${place.district}, ${place.region}</small>`;
    button.addEventListener("click", () => choosePlace(place));
    elements.suggestions.append(button);
  }
  elements.suggestions.hidden = false;
}

async function choosePlace(place) {
  elements.suggestions.hidden = true;
  elements.placeInput.value = place.name;
  elements.formStatus.textContent = "loading climate tile…";
  try {
    await loadCoordinate(place.lat, place.lon, place.id);
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
  const width = 760;
  const height = 250;
  const margin = { top: 22, right: 48, bottom: 34, left: 44 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const maximum = Math.max(100, Math.ceil(Math.max(...values) / 100) * 100);
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
    const barHeight = value / maximum * plotHeight;
    const rect = svgElement("rect", {
      x: margin.left + index * slot + slot * 0.16,
      y: rainY(value),
      width: slot * 0.68,
      height: barHeight,
      rx: 2,
      class: "rain-bar",
    });
    const title = svgElement("title");
    title.textContent = `${MONTHS[index]}: ${value} mm · ${rainyDays[index]} rainy days · ${heavyRainDays[index]} days ≥20 mm`;
    rect.append(title);
    svg.append(rect);
    const label = svgElement("text", { x: margin.left + index * slot + slot / 2, y: height - 12, "text-anchor": "middle" });
    label.textContent = MONTHS[index];
    svg.append(label);
  });
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
    title.textContent = `${MONTHS[index]}: ${rainyDays[index]} days with ≥1 mm rain; ${values[index]} mm total`;
    dot.append(title);
    svg.append(dot);
  });
  const rainUnit = svgElement("text", { x: margin.left - 8, y: 13, "text-anchor": "end" });
  rainUnit.textContent = "mm";
  svg.append(rainUnit);
  const daysUnit = svgElement("text", { x: width - margin.right + 8, y: 13 });
  daysUnit.textContent = "days";
  svg.append(daysUnit);
  elements.rainChart.replaceChildren(svg);
}

function renderTemperatureChart(minimums, maximums) {
  const width = 760;
  const height = 220;
  const margin = { top: 16, right: 12, bottom: 34, left: 44 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const lower = Math.floor((Math.min(...minimums) - 2) / 5) * 5;
  const upper = Math.ceil((Math.max(...maximums) + 2) / 5) * 5;
  const y = (value) => margin.top + plotHeight - (value - lower) / (upper - lower) * plotHeight;
  const svg = svgElement("svg", { viewBox: `0 0 ${width} ${height}`, "aria-hidden": "true" });
  for (let value = lower; value <= upper; value += 5) {
    const lineY = y(value);
    svg.append(svgElement("line", { x1: margin.left, x2: width - margin.right, y1: lineY, y2: lineY, class: "axis" }));
    const label = svgElement("text", { x: margin.left - 8, y: lineY + 4, "text-anchor": "end" });
    label.textContent = `${value}°`;
    svg.append(label);
  }
  const slot = plotWidth / minimums.length;
  minimums.forEach((minimum, index) => {
    const maximum = maximums[index];
    const x = margin.left + index * slot + slot * 0.24;
    const top = y(maximum);
    const bottom = y(minimum);
    const rect = svgElement("rect", { x, y: top, width: slot * 0.52, height: bottom - top, rx: 5, class: "temperature-band" });
    const title = svgElement("title");
    title.textContent = `${MONTHS[index]}: ${minimum.toFixed(1)}–${maximum.toFixed(1)} °C`;
    rect.append(title);
    svg.append(rect);
    svg.append(svgElement("circle", { cx: x + slot * 0.26, cy: y((minimum + maximum) / 2), r: 2.5, class: "temperature-mid" }));
    const label = svgElement("text", { x: margin.left + index * slot + slot / 2, y: height - 12, "text-anchor": "middle" });
    label.textContent = MONTHS[index];
    svg.append(label);
  });
  elements.temperatureChart.replaceChildren(svg);
}

function buildInterpretation(location) {
  const rain = location.rainfall.monthlyTotalMm;
  const risk = location.rainfall.drySpellRisk10d;
  const heavyRainDays = location.rainfall.heavyRainDays;
  const annual = rain.reduce((sum, value) => sum + value, 0);
  const wetMonths = rain.filter((value) => value >= 150).length;
  const riskyMonths = risk.filter((value) => value >= 0.6).length;
  const notes = [];
  const mostHeavyDays = Math.max(...heavyRainDays);
  const heavyMonths = MONTHS.filter(
    (_, index) => heavyRainDays[index] >= mostHeavyDays - 0.5
  );
  notes.push(
    `Days with at least 20 mm are most frequent in ${heavyMonths.join(", ")} (about ${mostHeavyDays.toFixed(1)} per month in the historical record).`
  );
  if (wetMonths >= 8) {
    notes.push("Rain is distributed through much of the year, so drainage, disease pressure, and short rain-free work windows may matter more than annual water supply.");
  } else if (wetMonths >= 4) {
    notes.push("Rainfall is strongly seasonal. Establishment is generally safer during the sustained wet period than during isolated early rains.");
  } else {
    notes.push("Reliable rain is concentrated in a short period. Water storage, drought-tolerant crops, and conservative planting decisions carry unusual weight.");
  }
  if (riskyMonths >= 5) {
    notes.push("Long dry spells are historically common for a substantial part of the year. Monthly totals alone can therefore overstate crop water reliability.");
  } else {
    notes.push("Ten-day dry spells are less common than in Madagascar's drier zones, but the seasonal maximum still deserves attention for germination and transplanting.");
  }
  if (annual > 2000) {
    notes.push("The high annual rainfall figure should not be read as uniformly benign. Nutrient leaching and saturated soil can remain binding constraints.");
  }
  return notes;
}

function renderReport(location, request) {
  const rain = location.rainfall.monthlyTotalMm;
  const dryRisk = location.rainfall.drySpellRisk10d;
  const heavyRainDays = location.rainfall.heavyRainDays;
  const minimums = location.temperature.monthlyMinC;
  const maximums = location.temperature.monthlyMaxC;
  const wettestIndex = rain.indexOf(Math.max(...rain));
  const driestIndex = rain.indexOf(Math.min(...rain));
  const highestRiskIndex = dryRisk.indexOf(Math.max(...dryRisk));
  const highestHeavyIndex = heavyRainDays.indexOf(Math.max(...heavyRainDays));
  const annual = rain.reduce((sum, value) => sum + value, 0);

  elements.reportRegion.textContent = `${location.district}, ${location.region}`;
  elements.reportTitle.textContent = location.name;
  elements.reportCoordinates.textContent = `${request.requestedLat.toFixed(4)}, ${request.requestedLon.toFixed(4)} · tile ${request.tileId}`;
  elements.reportThrough.textContent = location.current.through;
  elements.releaseType.textContent = location.current.releaseType;
  elements.annualRain.textContent = `${Math.round(annual).toLocaleString()} mm`;
  elements.rainSeason.textContent = `wettest: ${MONTHS[wettestIndex]} · most ≥20 mm days: ${MONTHS[highestHeavyIndex]}`;
  elements.dryRisk.textContent = `${Math.round(dryRisk[highestRiskIndex] * 100)}%`;
  elements.drySeason.textContent = `highest in ${MONTHS[highestRiskIndex]}`;
  elements.tempRange.textContent = `${Math.min(...minimums).toFixed(1)}–${Math.max(...maximums).toFixed(1)} °C`;
  elements.currentCopy.textContent = `${location.current.yearToDateRainMm.toLocaleString()} mm observed versus ${location.current.normalToDateRainMm.toLocaleString()} mm for the matching normal period.`;
  elements.anomalyValue.textContent = `${location.current.anomalyPercent > 0 ? "+" : ""}${location.current.anomalyPercent.toFixed(1)}%`;
  elements.cellDetails.textContent = `rain cell ${location.cells.rain.resolutionDegrees}° centered at ${location.cells.rain.lat}, ${location.cells.rain.lon}; temperature cell ${location.cells.temperature.resolutionDegrees}° centered at ${location.cells.temperature.lat}, ${location.cells.temperature.lon}.`;

  renderRainChart(rain, location.rainfall.rainyDays, heavyRainDays);
  renderTemperatureChart(minimums, maximums);
  elements.rainTableBody.replaceChildren(...MONTHS.map((month, index) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${month}</td><td>${rain[index]} mm</td><td>${location.rainfall.rainyDays[index]}</td><td>${heavyRainDays[index]}</td><td>${location.rainfall.wetDayIntensityMm[index]} mm</td>`;
    return row;
  }));
  elements.interpretationList.replaceChildren(...buildInterpretation(location).map((note) => {
    const item = document.createElement("li");
    item.textContent = note;
    return item;
  }));
  elements.report.setAttribute("aria-busy", "false");
}

elements.placeInput.addEventListener("input", () => renderSuggestions(matchingPlaces(elements.placeInput.value)));
elements.placeForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const matches = matchingPlaces(elements.placeInput.value);
  if (!matches.length) {
    elements.formStatus.textContent = "No matching prototype place. Try Fenerive Est, Tana, or Toliara.";
    return;
  }
  await choosePlace(matches[0]);
});

elements.coordinateForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(elements.coordinateForm);
  const lat = Number(form.get("latitude"));
  const lon = Number(form.get("longitude"));
  elements.formStatus.textContent = "loading climate tile…";
  try {
    await loadCoordinate(lat, lon);
    elements.formStatus.textContent = "";
  } catch (error) {
    elements.formStatus.textContent = `${error.message} The national data layer will fill this gap.`;
  }
});

elements.locationButton.addEventListener("click", () => {
  if (!navigator.geolocation) {
    elements.formStatus.textContent = "This browser does not provide device location.";
    return;
  }
  elements.formStatus.textContent = "requesting device location…";
  navigator.geolocation.getCurrentPosition(
    async ({ coords }) => {
      document.querySelector("#latitude").value = coords.latitude.toFixed(5);
      document.querySelector("#longitude").value = coords.longitude.toFixed(5);
      try {
        await loadCoordinate(coords.latitude, coords.longitude);
        elements.formStatus.textContent = "";
      } catch (error) {
        elements.formStatus.textContent = `${error.message} The national data layer will fill this gap.`;
      }
    },
    () => { elements.formStatus.textContent = "Location was unavailable. Coordinates can still be entered manually."; },
    { enableHighAccuracy: false, timeout: 12000, maximumAge: 600000 },
  );
});

async function initialize() {
  try {
    const manifestResponse = await fetch("data/manifest.json");
    manifest = await manifestResponse.json();
    const placesResponse = await fetch(manifest.places);
    const placeData = await placesResponse.json();
    places = placeData.places;
    await choosePlace(places[0]);
  } catch (error) {
    elements.formStatus.textContent = `The prototype data could not load: ${error.message}`;
    elements.report.setAttribute("aria-busy", "false");
  }

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("sw.js")
      .then(() => { elements.offlineStatus.textContent = "offline cache ready"; })
      .catch(() => { elements.offlineStatus.textContent = "offline cache unavailable"; });
  } else {
    elements.offlineStatus.textContent = "offline cache unsupported";
  }
}

initialize();
