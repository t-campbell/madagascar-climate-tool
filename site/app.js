const MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"];
// The 1991–2020 national CHIRPS land-cell baseline peaks at 800.1 mm/month.
const RAIN_AXIS_MAX_MM = 1000;
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
  annualRain: document.querySelector("#annual-rain"),
  rainSeason: document.querySelector("#rain-season"),
  dryRisk: document.querySelector("#dry-risk"),
  drySeason: document.querySelector("#dry-season"),
  rainChart: document.querySelector("#rain-chart"),
  rainTableBody: document.querySelector("#rain-table tbody"),
  interpretationList: document.querySelector("#interpretation-list"),
  cellDetails: document.querySelector("#cell-details"),
  offlineStatus: document.querySelector("#offline-status"),
};

let manifest;
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

async function loadTile(tileId) {
  const path = manifest.tileTemplate.replace("{tileId}", tileId);
  const response = await fetch(path);
  if (!response.ok) throw new Error("No CHIRPS land cell is available near those coordinates.");
  return response.json();
}

async function loadCoordinate(lat, lon, place = null) {
  if (!withinMadagascar(lat, lon)) {
    throw new Error("Those coordinates fall outside the Madagascar coverage box.");
  }
  const tileId = tileIdFor(lat, lon);
  const tile = await loadTile(tileId);
  let nearest = null;
  for (const cell of tile.cells) {
    const cellLat = tile.lat[cell[0]];
    const cellLon = tile.lon[cell[1]];
    const distance = distanceKm(lat, lon, cellLat, cellLon);
    if (!nearest || distance < nearest.distance) nearest = { cell, lat: cellLat, lon: cellLon, distance };
  }
  if (!nearest || nearest.distance > manifest.maxCellDistanceKm) {
    throw new Error("No CHIRPS land cell is within 12 km. Check the coordinates or try a nearby inland point.");
  }
  renderReport(nearest, { requestedLat: lat, requestedLon: lon, tileId, place });
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
        if (!response.ok) throw new Error("Place search is temporarily unavailable.");
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
    elements.formStatus.textContent = query ? "type at least three letters" : "";
    return [];
  }
  if (!shardFor(normalized)) {
    renderSuggestions([]);
    elements.formStatus.textContent = manifest.searchPrefixes.some((prefix) => prefix.startsWith(normalized))
      ? "keep typing to narrow the place search" : "no matching place; coordinates still work";
    return [];
  }
  try {
    const matches = await matchingPlaces(query);
    if (elements.placeInput.value !== query) return [];
    renderSuggestions(matches);
    elements.formStatus.textContent = matches.length ? ""
      : manifest.searchPrefixes.some((prefix) => prefix.startsWith(normalized))
        ? "keep typing to narrow the place search" : "no matching place; coordinates still work";
    return matches;
  } catch (error) {
    if (elements.placeInput.value === query) elements.formStatus.textContent = error.message;
    return [];
  }
}

async function choosePlace(place) {
  elements.suggestions.hidden = true;
  elements.placeInput.value = place.name;
  elements.formStatus.textContent = "loading rainfall tile…";
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

function buildInterpretation(rain, heavyRainDays, risk) {
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
    notes.push("Rain is spread across much of the year. Drainage and workable rain-free days may be important.");
  } else if (wetMonths >= 4) {
    notes.push("Rainfall has a sustained wetter period. Compare rainy-day frequency and dry-spell risk before choosing a planting window.");
  } else {
    notes.push("Rain is concentrated in fewer months. Consider water access and dry-spell risk when planning establishment.");
  }
  if (riskyMonths >= 5) {
    notes.push("Ten-day dry spells are historically common for part of the year. Monthly totals alone can overstate water reliability.");
  }
  if (annual > 2000) {
    notes.push("High annual rainfall can also bring leaching and saturated soil.");
  }
  return notes;
}

function renderReport(nearest, request) {
  const [,, rain, p10, p90, rainyDays, heavyRainDays, wetIntensity, dryRisk] = nearest.cell;
  const wettestIndex = rain.indexOf(Math.max(...rain));
  const highestRiskIndex = dryRisk.indexOf(Math.max(...dryRisk));
  const highestHeavyIndex = heavyRainDays.indexOf(Math.max(...heavyRainDays));
  const annual = rain.reduce((sum, value) => sum + value, 0);

  elements.reportRegion.textContent = request.place
    ? [request.place.district, request.place.region].filter(Boolean).join(", ") || "Madagascar"
    : "coordinate lookup · Madagascar";
  elements.reportTitle.textContent = request.place ? request.place.name : "rainfall at coordinates";
  elements.reportCoordinates.textContent = `requested: ${request.requestedLat.toFixed(4)}, ${request.requestedLon.toFixed(4)}`;
  elements.annualRain.textContent = `${Math.round(annual).toLocaleString()} mm`;
  elements.rainSeason.textContent = `wettest: ${MONTHS[wettestIndex]} · most ≥20 mm days: ${MONTHS[highestHeavyIndex]}`;
  elements.dryRisk.textContent = `${Math.round(dryRisk[highestRiskIndex] * 100)}%`;
  elements.drySeason.textContent = `highest in ${MONTHS[highestRiskIndex]}`;
  elements.cellDetails.textContent = `nearest CHIRPS 0.05° cell: ${nearest.lat.toFixed(4)}, ${nearest.lon.toFixed(4)} (${nearest.distance.toFixed(1)} km from requested point). 1991–2020 normal.`;

  renderRainChart(rain, rainyDays, heavyRainDays);
  elements.rainTableBody.replaceChildren(...MONTHS.map((month, index) => {
    const row = document.createElement("tr");
    for (const value of [month, `${rain[index]} mm`, `${p10[index]}–${p90[index]} mm`, rainyDays[index], heavyRainDays[index], `${wetIntensity[index]} mm`]) {
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

elements.placeInput.addEventListener("input", updateSuggestions);
elements.placeForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const matches = await updateSuggestions();
  if (!matches.length) {
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
    elements.formStatus.textContent = error.message;
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
        elements.formStatus.textContent = error.message;
      }
    },
    () => { elements.formStatus.textContent = "Location was unavailable. Coordinates can still be entered manually."; },
    { enableHighAccuracy: false, timeout: 12000, maximumAge: 600000 },
  );
});

async function initialize() {
  try {
    const manifestResponse = await fetch("data/manifest.json");
    if (!manifestResponse.ok) throw new Error("rainfall manifest unavailable");
    manifest = await manifestResponse.json();
    if (manifest.status !== "rainfall-baseline") throw new Error("unexpected rainfall data version");
    manifest.searchPrefixesSet = new Set(manifest.searchPrefixes);
    await loadCoordinate(manifest.defaultLocation.lat, manifest.defaultLocation.lon, manifest.defaultLocation);
  } catch (error) {
    elements.formStatus.textContent = `Rainfall data could not load: ${error.message}`;
    elements.report.setAttribute("aria-busy", "false");
  }

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("sw.js")
      .then(() => { elements.offlineStatus.textContent = "visited places available offline"; })
      .catch(() => { elements.offlineStatus.textContent = "offline cache unavailable"; });
  } else {
    elements.offlineStatus.textContent = "offline cache unsupported";
  }
}

initialize();
