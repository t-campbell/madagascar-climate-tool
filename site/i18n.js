const STORAGE_KEY = "mg-climate-language";

const MONTHS = {
  en: ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"],
  mg: ["jan", "feb", "mar", "apr", "mey", "jon", "jol", "aog", "sep", "okt", "nov", "des"],
};

const COPY = {
  en: {
    title: "Madagascar climate field guide",
    description: "Low-bandwidth historical rainfall patterns for locations across Madagascar.",
    homeLabel: "Madagascar climate field guide home",
    brand: "climate field guide",
    methods: "methods",
    historicalRainfall: "historical rainfall · 1991–2020",
    searchTitle: "check a location in Madagascar",
    town: "town or settlement",
    placePlaceholder: "try Fenerive Est or Tana",
    search: "search",
    searchHelp: "start typing a place name; for an unlisted settlement, use coordinates",
    matchingPlaces: "matching places",
    useCoordinates: "use coordinates instead",
    latitude: "latitude",
    longitude: "longitude",
    checkCoordinates: "check coordinates",
    useLocation: "use my location",
    rainfallDemo: "rainfall demo",
    demoNote: "1991–2020 historical CHIRPS rainfall. temperature and current-season comparisons are coming later; this is not a forecast.",
    loadingLocation: "loading location",
    rainfallReport: "rainfall report",
    baseline: "historical baseline",
    annualRain: "typical annual rain",
    dryRisk: "highest 10-day dry-spell risk",
    historicalPattern: "historical pattern",
    yearRain: "rain through the year",
    chooseSeries: "choose chart series",
    rainfall: "rainfall",
    rainyDays: "rainy days",
    heavyDays: "heavy days",
    chartAria: "monthly rainfall totals in blue bars on a fixed left axis from zero to 1,000 millimeters, and average rainy days in orange on the right axis from zero to 31 days; rounded values are in the table below",
    chartNote: "rainfall uses the fixed left axis (0–1,000 mm); rainy and heavy-rain days use the right axis (0–31 days). heavy means ≥20 mm in one day.",
    tableCaption: "monthly rainfall totals and historical range, rainy-day frequency, heavy-rain-day frequency, and wet-day intensity",
    month: "month",
    meanRain: "mean rain",
    typicalRange: "typical range",
    days20: "days ≥20 mm",
    meanWetDay: "mean wet day",
    fieldInterpretation: "field interpretation",
    patternSuggests: "what the pattern suggests",
    caution: "this describes historical climate, not a forecast or a planting recommendation for this season.",
    spatialBasis: "spatial basis",
    numbersMean: "what these numbers mean",
    methodRainLabel: "rainfall:",
    methodRain: "CHIRPS Final at 0.05° resolution, using 1991–2020 data. coordinate lookups use the nearest land cell within 12 km. small areas and complex terrain may differ from the cell average.",
    methodRangeLabel: "typical range:",
    methodRange: "the 10th to 90th percentile of that calendar month's rainfall totals across 1991–2020. it describes past variation, not a forecast interval.",
    methodFrequencyLabel: "rain frequency:",
    methodFrequency: "a rainy day has at least 1 mm. a heavy-rain day has at least 20 mm. both columns show the mean number of days per month across the baseline years.",
    methodRoundingLabel: "rounding:",
    methodRounding: "displayed rainfall totals, ranges, and wet-day intensity are rounded to the nearest whole millimetre. mean rainy-day and heavy-rain-day counts are rounded to the nearest whole day. calculations and chart positions still use the unrounded values.",
    methodPlacesLabel: "place names:",
    methodPlacesBefore: "settlement search uses",
    methodPlacesAfter: "data (CC BY). enter coordinates if the local name is missing or ambiguous.",
    lowBandwidth: "built for low-bandwidth field use",
    checkingOffline: "checking offline support",
    switchLanguage: "switch to Malagasy",
    noCell: "No CHIRPS land cell is available near those coordinates.",
    outsideCoverage: "Those coordinates fall outside the Madagascar coverage box.",
    noCell12: "No CHIRPS land cell is within 12 km. Check the coordinates or try a nearby inland point.",
    placeUnavailable: "Place search is temporarily unavailable.",
    typeThree: "type at least three letters",
    keepTyping: "keep typing to narrow the place search",
    noMatch: "no matching place; coordinates still work",
    loadingRainfall: "loading rainfall tile…",
    loadingClimate: "loading climate tile…",
    deviceUnsupported: "This browser does not provide device location.",
    requestingLocation: "requesting device location…",
    locationUnavailable: "Location was unavailable. Coordinates can still be entered manually.",
    manifestUnavailable: "rainfall manifest unavailable",
    unexpectedData: "unexpected rainfall data version",
    dataLoadFailed: "Rainfall data could not load: {message}",
    offlineReady: "visited places available offline",
    offlineUnavailable: "offline cache unavailable",
    offlineUnsupported: "offline cache unsupported",
    coordinateLookup: "coordinate lookup · Madagascar",
    coordinateRainfall: "rainfall at coordinates",
    requested: "requested: {lat}, {lon}",
    seasonSummary: "wettest: {wettest} · most ≥20 mm days: {heavy}",
    highestIn: "highest in {month}",
    cellDetails: "nearest CHIRPS 0.05° cell: {lat}, {lon} ({distance} km from requested point). 1991–2020 normal.",
    rainTooltip: "{month}: {value} mm rainfall",
    heavyTooltip: "{month}: {value} days with ≥20 mm rain",
    rainyTooltip: "{month}: {value} days with ≥1 mm rain",
    daysUnit: "days",
    visibleRainfall: "rainfall",
    visibleRainy: "rainy days",
    visibleHeavy: "heavy-rain days",
    chartVisible: "monthly {series}; rounded values are in the table below",
    chartNone: "no chart series selected; rounded values are in the table below",
    interpretationHeavy: "Days with at least 20 mm are most frequent in {months} (about {days} per month in the historical record).",
    interpretationWet: "Rain is spread across much of the year. Drainage and workable rain-free days may be important.",
    interpretationSeason: "Rainfall has a sustained wetter period. Compare rainy-day frequency and dry-spell risk before choosing a planting window.",
    interpretationShort: "Rain is concentrated in fewer months. Consider water access and dry-spell risk when planning establishment.",
    interpretationDry: "Ten-day dry spells are historically common for part of the year. Monthly totals alone can overstate water reliability.",
    interpretationHighRain: "High annual rainfall can also bring leaching and saturated soil.",
  },
  mg: {
    title: "Torolalana momba ny toetrandro eto Madagasikara",
    description: "Endriky ny rotsak’orana ara-tantara amin’ny toerana manerana an’i Madagasikara, natao ho an’ny aterineto miadana.",
    homeLabel: "Fandraisana amin’ny torolalana momba ny toetrandro eto Madagasikara",
    brand: "torolalana momba ny toetrandro",
    methods: "fomba",
    historicalRainfall: "rotsak’orana ara-tantara · 1991–2020",
    searchTitle: "jereo ny toerana iray eto Madagasikara",
    town: "tanàna na vohitra",
    placePlaceholder: "ohatra: Fenerive Est na Tana",
    search: "karohy",
    searchHelp: "manomboha manoratra anaran-toerana; ampiasao ny koordinaty raha tsy hita ilay toerana",
    matchingPlaces: "toerana mifanaraka",
    useCoordinates: "ampiasao kosa ny koordinaty",
    latitude: "latitude",
    longitude: "longitude",
    checkCoordinates: "jereo ny koordinaty",
    useLocation: "ampiasao ny toerana misy ahy",
    rainfallDemo: "santionan’ny rotsak’orana",
    demoNote: "Rotsak’orana ara-tantara CHIRPS 1991–2020. Hampiana any aoriana ny maripana sy ny fampitahana amin’ny vanim-potoana ankehitriny; tsy vinavinan’ny andro ity.",
    loadingLocation: "maka ny toerana",
    rainfallReport: "tatitra momba ny rotsak’orana",
    baseline: "salan’isa ara-tantara",
    annualRain: "rotsak’orana isan-taona mahazatra",
    dryRisk: "risika avo indrindra amin’ny haintany 10 andro",
    historicalPattern: "endrika ara-tantara",
    yearRain: "rotsak’orana mandritra ny taona",
    chooseSeries: "safidio ny angona amin’ny sary",
    rainfall: "rotsak’orana",
    rainyDays: "andro misy orana",
    heavyDays: "andro be orana",
    chartAria: "fitambaran’ny rotsak’orana isam-bolana amin’ny tsanganana manga eo amin’ny maridrefy havia 0 hatramin’ny 1 000 milimetatra, ary salan’ny andro misy orana amin’ny tsipika volomboasary eo amin’ny maridrefy havanana 0 hatramin’ny 31 andro; ao amin’ny tabilao ambany ny isa voahodina",
    chartNote: "Ny rotsak’orana dia mampiasa ny maridrefy havia raikitra (0–1 000 mm); ny andro misy orana sy ny andro be orana dia mampiasa ny maridrefy havanana (0–31 andro). Ny hoe be orana dia ≥20 mm ao anatin’ny iray andro.",
    tableCaption: "fitambaran’ny rotsak’orana isam-bolana sy elanelana ara-tantara, fahabetsahan’ny andro misy orana sy andro be orana, ary herin’ny orana amin’ny andro mando",
    month: "volana",
    meanRain: "salan’ny orana",
    typicalRange: "elanelana mahazatra",
    days20: "andro ≥20 mm",
    meanWetDay: "salan’ny orana/andro mando",
    fieldInterpretation: "fanazavana ho an’ny asa eny an-tsaha",
    patternSuggests: "inona no asehon’ity endrika ity",
    caution: "Toetrandro ara-tantara no asehon’ity, fa tsy vinavinan’ny andro na torohevitra hambolena amin’ity vanim-potoana ity.",
    spatialBasis: "fototra ara-toerana",
    numbersMean: "inona no dikan’ireo isa",
    methodRainLabel: "rotsak’orana:",
    methodRain: "CHIRPS Final amin’ny resolution 0,05°, mampiasa angona 1991–2020. Ho an’ny koordinaty dia ny sela an-tanety akaiky indrindra ao anatin’ny 12 km no ampiasaina. Mety tsy hitovy amin’ny salan’ilay sela ny faritra madinika sy ny toerana be tendrombohitra.",
    methodRangeLabel: "elanelana mahazatra:",
    methodRange: "ny percentile faha-10 ka hatramin’ny faha-90 amin’ny fitambaran’ny rotsak’orana tamin’io volana io nandritra ny 1991–2020. Fiovaovana tamin’ny lasa no asehony, fa tsy elanelan’ny vinavina.",
    methodFrequencyLabel: "fahabetsahan’ny orana:",
    methodFrequency: "ny andro misy orana dia manana orana 1 mm farafahakeliny. Ny andro be orana dia manana 20 mm farafahakeliny. Ireo tsanganana roa ireo dia mampiseho ny salan’isan’ny andro isam-bolana nandritra ireo taona fototra.",
    methodRoundingLabel: "fanodinana isa:",
    methodRounding: "ny fitambaran’ny rotsak’orana, ny elanelana ary ny herin’ny orana amin’ny andro mando aseho dia voahodina ho mm manontolo akaiky indrindra. Ny salan’isan’ny andro misy orana sy andro be orana dia voahodina ho andro manontolo akaiky indrindra. Ny kajy sy ny toeran’ny sary kosa mbola mampiasa ny isa tsy voahodina.",
    methodPlacesLabel: "anaran-toerana:",
    methodPlacesBefore: "ny fikarohana anaran-toerana dia mampiasa ny angon’i",
    methodPlacesAfter: "(CC BY). Ampidiro ny koordinaty raha tsy hita na mety manondro toerana maro ny anarana eo an-toerana.",
    lowBandwidth: "natao ho an’ny fampiasana eny an-tsaha amin’ny aterineto miadana",
    checkingOffline: "manamarina ny fampiasana tsy misy aterineto",
    switchLanguage: "ovay ho teny anglisy",
    noCell: "Tsy misy sela an-tanety CHIRPS akaikin’ireo koordinaty ireo.",
    outsideCoverage: "Any ivelan’ny faritra rakofan’ny angona eto Madagasikara ireo koordinaty ireo.",
    noCell12: "Tsy misy sela an-tanety CHIRPS ao anatin’ny 12 km. Hamarino ny koordinaty na manandrama teboka akaiky kokoa mankany an-tanety.",
    placeUnavailable: "Tsy azo ampiasaina vetivety ny fikarohana toerana.",
    typeThree: "manorata litera telo farafahakeliny",
    keepTyping: "tohizo ny fanoratana mba hahitsy kokoa ny fikarohana",
    noMatch: "tsy misy toerana mifanaraka; mbola azo ampiasaina ny koordinaty",
    loadingRainfall: "maka ny angona momba ny rotsak’orana…",
    loadingClimate: "maka ny angona momba ny rotsak’orana…",
    deviceUnsupported: "Tsy afaka maka ny toerana misy ilay fitaovana ity navigateur ity.",
    requestingLocation: "maka ny toerana misy ilay fitaovana…",
    locationUnavailable: "Tsy azo ny toerana. Mbola azo ampidirina mivantana ny koordinaty.",
    manifestUnavailable: "tsy azo ny lisitry ny angona momba ny rotsak’orana",
    unexpectedData: "tsy araka ny nampoizina ny kinovan’ny angona momba ny rotsak’orana",
    dataLoadFailed: "Tsy voasokatra ny angona momba ny rotsak’orana: {message}",
    offlineReady: "azo ampiasaina tsy misy aterineto ireo toerana efa nojerena",
    offlineUnavailable: "tsy azo ampiasaina ny fitahirizana ho an’ny fotoana tsy misy aterineto",
    offlineUnsupported: "tsy tohanan’ity navigateur ity ny fampiasana tsy misy aterineto",
    coordinateLookup: "fikarohana amin’ny koordinaty · Madagasikara",
    coordinateRainfall: "rotsak’orana amin’ireo koordinaty",
    requested: "koordinaty nangatahana: {lat}, {lon}",
    seasonSummary: "be orana indrindra: {wettest} · be indrindra ny andro ≥20 mm: {heavy}",
    highestIn: "avo indrindra amin’ny {month}",
    cellDetails: "sela CHIRPS 0,05° akaiky indrindra: {lat}, {lon} ({distance} km miala amin’ny teboka nangatahana). Salan’isa 1991–2020.",
    rainTooltip: "{month}: rotsak’orana {value} mm",
    heavyTooltip: "{month}: {value} andro misy orana ≥20 mm",
    rainyTooltip: "{month}: {value} andro misy orana ≥1 mm",
    daysUnit: "andro",
    visibleRainfall: "rotsak’orana",
    visibleRainy: "andro misy orana",
    visibleHeavy: "andro be orana",
    chartVisible: "{series} isam-bolana; ao amin’ny tabilao ambany ny isa voahodina",
    chartNone: "tsy misy angona voafantina amin’ny sary; ao amin’ny tabilao ambany ny isa voahodina",
    interpretationHeavy: "Ny andro misy orana 20 mm farafahakeliny dia matetika indrindra amin’ny {months} (eo amin’ny {days} isam-bolana ao amin’ny angona ara-tantara).",
    interpretationWet: "Miparitaka amin’ny ankamaroan’ny taona ny orana. Mety ho zava-dehibe ny lalan-drano sy ny fahitana andro tsy misy orana ahafahana miasa.",
    interpretationSeason: "Misy vanim-potoana mando maharitra. Ampitahao ny isan’ny andro misy orana sy ny risika amin’ny haintany alohan’ny hisafidianana fotoana hambolena.",
    interpretationShort: "Mivangongo amin’ny volana vitsivitsy ny orana. Diniho ny fahazoana rano sy ny risika amin’ny haintany rehefa manomana ny fanorenan’ny voly.",
    interpretationDry: "Fahita ara-tantara mandritra ny ampahany amin’ny taona ny haintany 10 andro. Mety hampiseho rano azo antoka mihoatra ny tena izy ny fitambaran’ny orana isam-bolana fotsiny.",
    interpretationHighRain: "Mety hiteraka fahaverezan-tsakafo ao anaty tany sy tany tototry ny rano koa ny rotsak’orana be isan-taona.",
  },
};

let currentLanguage = "en";
try {
  currentLanguage = localStorage.getItem(STORAGE_KEY) === "mg" ? "mg" : "en";
} catch {
  currentLanguage = "en";
}

const listeners = new Set();

export function language() {
  return currentLanguage;
}

export function t(key, values = {}) {
  const template = COPY[currentLanguage][key] ?? COPY.en[key] ?? key;
  return Object.entries(values).reduce(
    (result, [name, value]) => result.replaceAll(`{${name}}`, String(value)),
    template,
  );
}

export function displayMonth(index) {
  return MONTHS[currentLanguage][index];
}

export function subscribeLanguageChange(listener) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function applyLanguage() {
  document.documentElement.lang = currentLanguage;
  document.title = t("title");
  document.querySelector('meta[name="description"]')?.setAttribute("content", t("description"));
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    element.setAttribute("placeholder", t(element.dataset.i18nPlaceholder));
  });
  document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => {
    element.setAttribute("aria-label", t(element.dataset.i18nAriaLabel));
  });
  const toggle = document.querySelector("#language-toggle");
  if (toggle) {
    toggle.textContent = currentLanguage === "en" ? "MG" : "EN";
    toggle.setAttribute("aria-label", t("switchLanguage"));
    toggle.setAttribute("title", t("switchLanguage"));
  }
}

function setLanguage(nextLanguage) {
  currentLanguage = nextLanguage;
  try {
    localStorage.setItem(STORAGE_KEY, currentLanguage);
  } catch {
    // The language still changes for this page view if storage is unavailable.
  }
  applyLanguage();
  listeners.forEach((listener) => listener(currentLanguage));
}

document.querySelector("#language-toggle")?.addEventListener("click", () => {
  setLanguage(currentLanguage === "en" ? "mg" : "en");
});

applyLanguage();
