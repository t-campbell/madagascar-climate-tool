const STORAGE_KEY = "mg-climate-language";

const MONTHS = {
  en: ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"],
  mg: ["jan", "feb", "mar", "apr", "mey", "jon", "jol", "aog", "sep", "okt", "nov", "des"],
};

const COPY = {
  en: {
    recentEyebrow: "recent rainfall · CHIRPS Final",
    recentTitle: "what fell recently",
    recentActual: "actual rainfall",
    recentTypical: "1991–2020 mean",
    recentDifference: "difference",
    recentNote: "twelve complete months of Final rainfall estimates. day-count pairs show actual / historical average. these are past observations, not a forecast.",
    recentCaption: "recent monthly rainfall compared with the matching historical calendar month",
    recentThrough: "observations through {date}",
    recentLoading: "loading recent rainfall…",
    recentUnavailable: "recent rainfall could not load here. the historical baseline is still available.",
    recentPending: "recent monthly observations have not been published yet.",
    recentStale: "the latest included month is older than the usual Final release schedule. the date above shows the last verified data.",
    recentAxis: "rainfall scale: 0–{max} mm, fixed across locations for this release.",
    recentChartAria: "recent monthly rainfall bars with the matching 1991–2020 monthly mean as a line; values are in the table below",
    recentTooltip: "{month}: {actual} mm actual; {normal} mm historical mean",
    methodRecentLabel: "recent rainfall:",
    methodRecent: "complete months of CHIRPS v3 Final RNL, using the same grid and thresholds as the baseline. Final normally arrives in the third week of the following month. differences compare each month with its 1991–2020 mean; percentage differences are omitted when the baseline is below 1 mm. daily rainfall is disaggregated from pentad totals, so day counts are estimates. the displayed observation date remains visible offline.",
    title: "Madagascar climate field guide",
    description: "Low-bandwidth historical rainfall and temperature patterns for locations across Madagascar.",
    homeLabel: "Madagascar climate field guide home",
    brand: "climate field guide",
    methods: "methods",
    historicalRainfall: "historical rainfall · 1991–2020",
    historicalClimate: "historical climate · 1991–2020",
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
    climateBaseline: "climate baseline",
    demoNote: "1991–2020 historical CHIRPS rainfall and ERA5-Land temperature. this is not a forecast.",
    loadingLocation: "loading location",
    rainfallReport: "rainfall report",
    climateReport: "climate report",
    baseline: "historical baseline",
    annualRain: "typical annual rain",
    dryRisk: "highest 10-day dry-spell risk",
    warmestHigh: "warmest typical daytime high",
    coolestLow: "coolest typical nighttime low",
    historicalPattern: "historical pattern",
    yearRain: "rain through the year",
    chooseSeries: "choose chart series",
    rainfall: "rainfall",
    rainyDays: "rainy days",
    heavyDays: "heavy days",
    chartAria: "monthly rainfall totals in blue bars on a fixed left axis from zero to 1,000 millimeters, and average rainy days in orange on the right axis from zero to 31 days; rounded values are in the table below",
    chartNote: "rainfall uses the fixed left axis (0–1,000 mm); rainy and heavy-rain days use the right axis (0–31 days). heavy means ≥20 mm in one day.",
    tableCaption: "monthly rainfall totals and historical range, rainy-day frequency, heavy-rain-day frequency, and wet-day intensity",
    historicalTemperature: "historical temperature",
    yearTemperature: "heat through the year",
    dailyMinimum: "daily minimum",
    dailyMaximum: "daily maximum",
    temperatureChartAria: "monthly mean daily minimum and maximum temperature on a fixed zero to 40 degree Celsius axis",
    temperatureChartNote: "the fixed 0–40 °C axis makes heat directly comparable between locations. the shaded band spans the mean daily minimum to maximum.",
    temperatureTableCaption: "monthly mean daily minimum and maximum temperature",
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
    methodTemperatureLabel: "temperature:",
    methodTemperature: "ERA5-Land at 0.1° resolution, using 1991–2020 data. each monthly low is the mean of daily minimum temperatures; each high is the mean of daily maximum temperatures.",
    methodRoundingLabel: "rounding:",
    methodRounding: "displayed rainfall totals, ranges, and wet-day intensity are rounded to the nearest whole millimetre. mean rainy-day and heavy-rain-day counts are rounded to the nearest whole day, and temperatures to the nearest whole degree Celsius. calculations and chart positions still use the unrounded values.",
    methodPlacesLabel: "place names:",
    methodPlacesBefore: "settlement search uses",
    methodPlacesAfter: "data (CC BY). enter coordinates if the local name is missing or ambiguous.",
    lowBandwidth: "built for low-bandwidth field use",
    checkingOffline: "checking offline support",
    switchLanguage: "switch to Malagasy",
    noCell: "No CHIRPS land cell is available near those coordinates.",
    outsideCoverage: "Those coordinates fall outside the Madagascar coverage box.",
    noCell12: "No CHIRPS land cell is within 12 km. Check the coordinates or try a nearby inland point.",
    noTemperatureCell: "No ERA5-Land temperature cell is available near those coordinates.",
    noTemperatureCell20: "No ERA5-Land temperature cell is within 20 km. Check the coordinates or try a nearby inland point.",
    placeUnavailable: "Place search is temporarily unavailable.",
    typeThree: "type at least three letters",
    keepTyping: "keep typing to narrow the place search",
    noMatch: "no matching place; coordinates still work",
    loadingRainfall: "loading rainfall tile…",
    loadingClimate: "loading climate tile…",
    deviceUnsupported: "This browser does not provide device location.",
    requestingLocation: "requesting device location…",
    locationUnavailable: "Location was unavailable. Coordinates can still be entered manually.",
    manifestUnavailable: "climate manifest unavailable",
    unexpectedData: "unexpected climate data version",
    dataLoadFailed: "Climate data could not load: {message}",
    offlineReady: "visited places available offline",
    offlineUnavailable: "offline cache unavailable",
    offlineUnsupported: "offline cache unsupported",
    coordinateLookup: "coordinate lookup · Madagascar",
    coordinateRainfall: "rainfall at coordinates",
    coordinateClimate: "climate at coordinates",
    requested: "requested: {lat}, {lon}",
    seasonSummary: "wettest: {wettest} · most ≥20 mm days: {heavy}",
    highestIn: "highest in {month}",
    lowestIn: "lowest in {month}",
    cellDetails: "nearest cells: CHIRPS 0.05° at {rainLat}, {rainLon} ({rainDistance} km); ERA5-Land 0.1° at {temperatureLat}, {temperatureLon} ({temperatureDistance} km). 1991–2020 normal.",
    rainTooltip: "{month}: {value} mm rainfall",
    heavyTooltip: "{month}: {value} days with ≥20 mm rain",
    rainyTooltip: "{month}: {value} days with ≥1 mm rain",
    temperatureHighTooltip: "{month}: {value} °C mean daily maximum",
    temperatureLowTooltip: "{month}: {value} °C mean daily minimum",
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
    recentEyebrow: "rotsak’orana vao haingana · CHIRPS Final",
    recentTitle: "orana nilatsaka vao haingana",
    recentActual: "orana nilatsaka",
    recentTypical: "salan’isa 1991–2020",
    recentDifference: "fahasamihafana",
    recentNote: "volana roa ambin’ny folo feno amin’ny tomban’ny orana Final. ny isa miaraka dia andro tamin’ilay volana / salan’isa ara-tantara. angona tamin’ny lasa ireo, fa tsy vinavinan’ny andro.",
    recentCaption: "rotsak’orana isam-bolana vao haingana ampitahaina amin’ny volana mitovy tamin’ny angona ara-tantara",
    recentThrough: "angona hatramin’ny {date}",
    recentLoading: "maka angon’ny orana vao haingana…",
    recentUnavailable: "tsy azo nalaina eto ny angon’ny orana vao haingana. mbola azo jerena ny angona ara-tantara.",
    recentPending: "mbola tsy navoaka ny angon’ny orana vao haingana isam-bolana.",
    recentStale: "antitra noho ny fandaharam-pamoahana Final mahazatra ny volana farany tafiditra. ny daty etsy ambony no faran’ny angona voamarina.",
    recentAxis: "maridrefin’ny orana: 0–{max} mm, mitovy amin’ny toerana rehetra amin’ity famoahana ity.",
    recentChartAria: "tsanganana mampiseho ny orana isam-bolana vao haingana, miaraka amin’ny tsipika mampiseho ny salan’isa 1991–2020; ao amin’ny tabilao ambany ny isa",
    recentTooltip: "{month}: {actual} mm nilatsaka; {normal} mm salan’isa ara-tantara",
    methodRecentLabel: "orana vao haingana:",
    methodRecent: "volana feno amin’ny CHIRPS v3 Final RNL, mampiasa sela sy fetra mitovy amin’ny angona fototra. matetika mivoaka amin’ny herinandro fahatelo amin’ny volana manaraka ny Final. ampitahaina amin’ny salan’isa 1991–2020 amin’ny volana mitovy ny orana; tsy aseho ny isan-jato raha latsaky ny 1 mm ny salan’isa. zaraina ho andro ny fitambaran’ny orana mandritra ny dimy andro, ka tombana ny isan’ny andro. mbola hita ny datin’ny angona rehefa tsy misy aterineto.",
    title: "Torolalana momba ny toetrandro eto Madagasikara",
    description: "Endriky ny rotsak’orana sy maripana ara-tantara amin’ny toerana manerana an’i Madagasikara, natao ho an’ny aterineto miadana.",
    homeLabel: "Fandraisana amin’ny torolalana momba ny toetrandro eto Madagasikara",
    brand: "torolalana momba ny toetrandro",
    methods: "fomba",
    historicalRainfall: "rotsak’orana ara-tantara · 1991–2020",
    historicalClimate: "toetrandro ara-tantara · 1991–2020",
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
    climateBaseline: "angona fototry ny toetrandro",
    demoNote: "Rotsak’orana CHIRPS sy maripana ERA5-Land ara-tantara 1991–2020. Tsy vinavinan’ny andro ity.",
    loadingLocation: "maka ny toerana",
    rainfallReport: "tatitra momba ny rotsak’orana",
    climateReport: "tatitra momba ny toetrandro",
    baseline: "salan’isa ara-tantara",
    annualRain: "rotsak’orana isan-taona mahazatra",
    dryRisk: "risika avo indrindra amin’ny haintany 10 andro",
    warmestHigh: "maripana antoandro mahazatra avo indrindra",
    coolestLow: "maripana alina mahazatra ambany indrindra",
    historicalPattern: "endrika ara-tantara",
    yearRain: "rotsak’orana mandritra ny taona",
    chooseSeries: "safidio ny angona amin’ny sary",
    rainfall: "rotsak’orana",
    rainyDays: "andro misy orana",
    heavyDays: "andro be orana",
    chartAria: "fitambaran’ny rotsak’orana isam-bolana amin’ny tsanganana manga eo amin’ny maridrefy havia 0 hatramin’ny 1 000 milimetatra, ary salan’ny andro misy orana amin’ny tsipika volomboasary eo amin’ny maridrefy havanana 0 hatramin’ny 31 andro; ao amin’ny tabilao ambany ny isa voahodina",
    chartNote: "Ny rotsak’orana dia mampiasa ny maridrefy havia raikitra (0–1 000 mm); ny andro misy orana sy ny andro be orana dia mampiasa ny maridrefy havanana (0–31 andro). Ny hoe be orana dia ≥20 mm ao anatin’ny iray andro.",
    tableCaption: "fitambaran’ny rotsak’orana isam-bolana sy elanelana ara-tantara, fahabetsahan’ny andro misy orana sy andro be orana, ary herin’ny orana amin’ny andro mando",
    historicalTemperature: "maripana ara-tantara",
    yearTemperature: "hafanana mandritra ny taona",
    dailyMinimum: "maripana ambany isan’andro",
    dailyMaximum: "maripana avo isan’andro",
    temperatureChartAria: "salan’ny maripana ambany sy avo isan’andro isam-bolana amin’ny maridrefy raikitra 0 ka hatramin’ny 40 degre Celsius",
    temperatureChartNote: "Ny maridrefy raikitra 0–40 °C dia ahafahana mampitaha mivantana ny hafanana amin’ny toerana samihafa. Ny faritra miloko dia manomboka amin’ny salan’ny maripana ambany ka hatramin’ny avo isan’andro.",
    temperatureTableCaption: "salan’ny maripana ambany sy avo isan’andro isam-bolana",
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
    methodTemperatureLabel: "maripana:",
    methodTemperature: "ERA5-Land amin’ny resolution 0,1°, mampiasa angona 1991–2020. Ny maripana ambany isam-bolana dia salan’ny maripana ambany isan’andro; ny avo kosa dia salan’ny maripana avo isan’andro.",
    methodRoundingLabel: "fanodinana isa:",
    methodRounding: "ny fitambaran’ny rotsak’orana, ny elanelana ary ny herin’ny orana amin’ny andro mando aseho dia voahodina ho mm manontolo akaiky indrindra. Ny isan’ny andro dia voahodina ho andro manontolo, ary ny maripana ho degre Celsius manontolo akaiky indrindra. Ny kajy sy ny toeran’ny sary kosa mbola mampiasa ny isa tsy voahodina.",
    methodPlacesLabel: "anaran-toerana:",
    methodPlacesBefore: "ny fikarohana anaran-toerana dia mampiasa ny angon’i",
    methodPlacesAfter: "(CC BY). Ampidiro ny koordinaty raha tsy hita na mety manondro toerana maro ny anarana eo an-toerana.",
    lowBandwidth: "natao ho an’ny fampiasana eny an-tsaha amin’ny aterineto miadana",
    checkingOffline: "manamarina ny fampiasana tsy misy aterineto",
    switchLanguage: "ovay ho teny anglisy",
    noCell: "Tsy misy sela an-tanety CHIRPS akaikin’ireo koordinaty ireo.",
    outsideCoverage: "Any ivelan’ny faritra rakofan’ny angona eto Madagasikara ireo koordinaty ireo.",
    noCell12: "Tsy misy sela an-tanety CHIRPS ao anatin’ny 12 km. Hamarino ny koordinaty na manandrama teboka akaiky kokoa mankany an-tanety.",
    noTemperatureCell: "Tsy misy sela maripana ERA5-Land akaikin’ireo koordinaty ireo.",
    noTemperatureCell20: "Tsy misy sela maripana ERA5-Land ao anatin’ny 20 km. Hamarino ny koordinaty na manandrama teboka akaiky kokoa mankany an-tanety.",
    placeUnavailable: "Tsy azo ampiasaina vetivety ny fikarohana toerana.",
    typeThree: "manorata litera telo farafahakeliny",
    keepTyping: "tohizo ny fanoratana mba hahitsy kokoa ny fikarohana",
    noMatch: "tsy misy toerana mifanaraka; mbola azo ampiasaina ny koordinaty",
    loadingRainfall: "maka ny angona momba ny rotsak’orana…",
    loadingClimate: "maka ny angona momba ny rotsak’orana…",
    deviceUnsupported: "Tsy afaka maka ny toerana misy ilay fitaovana ity navigateur ity.",
    requestingLocation: "maka ny toerana misy ilay fitaovana…",
    locationUnavailable: "Tsy azo ny toerana. Mbola azo ampidirina mivantana ny koordinaty.",
    manifestUnavailable: "tsy azo ny lisitry ny angona momba ny toetrandro",
    unexpectedData: "tsy araka ny nampoizina ny kinovan’ny angona momba ny toetrandro",
    dataLoadFailed: "Tsy voasokatra ny angona momba ny toetrandro: {message}",
    offlineReady: "azo ampiasaina tsy misy aterineto ireo toerana efa nojerena",
    offlineUnavailable: "tsy azo ampiasaina ny fitahirizana ho an’ny fotoana tsy misy aterineto",
    offlineUnsupported: "tsy tohanan’ity navigateur ity ny fampiasana tsy misy aterineto",
    coordinateLookup: "fikarohana amin’ny koordinaty · Madagasikara",
    coordinateRainfall: "rotsak’orana amin’ireo koordinaty",
    coordinateClimate: "toetrandro amin’ireo koordinaty",
    requested: "koordinaty nangatahana: {lat}, {lon}",
    seasonSummary: "be orana indrindra: {wettest} · be indrindra ny andro ≥20 mm: {heavy}",
    highestIn: "avo indrindra amin’ny {month}",
    lowestIn: "ambany indrindra amin’ny {month}",
    cellDetails: "sela akaiky indrindra: CHIRPS 0,05° amin’ny {rainLat}, {rainLon} ({rainDistance} km); ERA5-Land 0,1° amin’ny {temperatureLat}, {temperatureLon} ({temperatureDistance} km). Salan’isa 1991–2020.",
    rainTooltip: "{month}: rotsak’orana {value} mm",
    heavyTooltip: "{month}: {value} andro misy orana ≥20 mm",
    rainyTooltip: "{month}: {value} andro misy orana ≥1 mm",
    temperatureHighTooltip: "{month}: {value} °C salan’ny maripana avo isan’andro",
    temperatureLowTooltip: "{month}: {value} °C salan’ny maripana ambany isan’andro",
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
