// INTERACTIVE OUTFIT RECOMMENDATION DEMO
// Displays uploaded clothing images as a suggested outfit combination by category.

const occasion = document.getElementById("occasion");
const generateBtn = document.getElementById("generateBtn");
const recommendationSection = document.getElementById("recommendations");
const selectedOccasion = document.getElementById("selectedOccasion");
const outfitOptionsGrid = document.getElementById("outfitOptionsGrid");

// Track uploaded files by category — each entry is { url, name }
let categoryFiles = {
  tops: [],
  bottoms: [],
  dresses: [],
  shoes: [],
  outerwear: []
};

// The outfit the user chose to save
let chosenOutfit = null;
let userAuthenticated = false;
let currentUserStorageKey = null;

// Current weather data (updated by loadWeather)
let currentWeather = { temp: null, feelsLike: null, condition: 'Clear', city: '', shortTerm: null };
let selectedLocationQuery = null;
let manualLocationCandidates = [];
let selectedForecastDate = null;

// ─── WEATHER API ─────────────────────────────────────────
const WMO_CONDITIONS = {
  0: 'Clear', 1: 'Mostly Clear', 2: 'Partly Cloudy', 3: 'Overcast',
  45: 'Foggy', 48: 'Icy Fog',
  51: 'Light Drizzle', 53: 'Drizzle', 55: 'Heavy Drizzle',
  61: 'Light Rain', 63: 'Rain', 65: 'Heavy Rain',
  71: 'Light Snow', 73: 'Snow', 75: 'Heavy Snow', 77: 'Snow Grains',
  80: 'Light Showers', 81: 'Showers', 82: 'Heavy Showers',
  85: 'Snow Showers', 86: 'Heavy Snow Showers',
  95: 'Thunderstorm', 96: 'Thunderstorm', 99: 'Thunderstorm'
};

function getWeatherCondition(code) {
  return WMO_CONDITIONS[code] || 'Cloudy';
}

function getWeatherIcon(condition) {
  const c = condition.toLowerCase();
  if (c.includes('clear') || c.includes('sunny')) return '☀️';
  if (c.includes('partly')) return '⛅';
  if (c.includes('cloud') || c.includes('overcast')) return '☁️';
  if (c.includes('fog')) return '🌫️';
  if (c.includes('drizzle') || c.includes('shower')) return '🌦️';
  if (c.includes('rain')) return '🌧️';
  if (c.includes('snow')) return '❄️';
  if (c.includes('thunder') || c.includes('storm')) return '⛈️';
  return '🌤️';
}

function toLocalDateString(dateObj) {
  const y = dateObj.getFullYear();
  const m = String(dateObj.getMonth() + 1).padStart(2, '0');
  const d = String(dateObj.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

function getTodayLocalDateString() {
  return toLocalDateString(new Date());
}

function formatShortDate(dateStr) {
  if (!dateStr) return 'today';
  const dt = new Date(`${dateStr}T00:00:00`);
  if (Number.isNaN(dt.getTime())) return dateStr;
  return dt.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
}

function findForecastSnapshotForDate(hourly, targetDateStr) {
  if (!hourly || !Array.isArray(hourly.time) || !targetDateStr) return null;

  const targetRows = [];
  for (let i = 0; i < hourly.time.length; i++) {
    const timeStr = hourly.time[i];
    if (!timeStr || typeof timeStr !== 'string') continue;
    if (!timeStr.startsWith(targetDateStr)) continue;

    const hour = Number(timeStr.slice(11, 13));
    targetRows.push({
      idx: i,
      hour,
      timeStr,
      temperature: Number(hourly.temperature_2m?.[i]),
      feelsLike: Number(hourly.apparent_temperature?.[i]),
      code: hourly.weather_code?.[i],
      wind: Number(hourly.wind_speed_10m?.[i]),
      gust: Number(hourly.wind_gusts_10m?.[i]),
      precipProb: Number(hourly.precipitation_probability?.[i] || 0)
    });
  }

  if (targetRows.length === 0) return null;

  // Pick the row closest to midday for outfit planning.
  let best = targetRows[0];
  let bestDist = Math.abs(best.hour - 12);
  for (const row of targetRows) {
    const dist = Math.abs(row.hour - 12);
    if (dist < bestDist) {
      best = row;
      bestDist = dist;
    }
  }

  return best;
}

function isRainLikelyCode(code) {
  return [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99].includes(code);
}

function getWindSeverity(speedMph, gustMph) {
  const speed = Number(speedMph || 0);
  const gust = Number(gustMph || 0);

  if (gust >= 30 || speed >= 24) {
    return {
      label: 'Very windy',
      note: 'Wind is strong. Prefer secure outerwear and avoid loose accessories.'
    };
  }

  if (gust >= 22 || speed >= 16) {
    return {
      label: 'Moderately windy',
      note: 'A light jacket is recommended, especially for outdoor travel.'
    };
  }

  return {
    label: 'Light wind',
    note: 'Comfortable wind conditions right now.'
  };
}

function analyzeShortTermRainOutlook(hourly, currentIsoTime, targetDateStr) {
  if (!hourly || !Array.isArray(hourly.time)) {
    return {
      futureNote: 'No short-term forecast detail available right now.',
        protectionAdvice: '',
        rainExpected: false
    };
  }

  const now = currentIsoTime ? new Date(currentIsoTime) : new Date();
  if (Number.isNaN(now.getTime())) {
    return {
      futureNote: 'No short-term forecast detail available right now.',
        protectionAdvice: '',
        rainExpected: false
    };
  }

  const sixHours = 6 * 60 * 60 * 1000;
  const todayY = now.getFullYear();
  const todayM = now.getMonth();
  const todayD = now.getDate();
  const targetDay = targetDateStr || getTodayLocalDateString();
  const todayStr = getTodayLocalDateString();
  const isTodayTarget = targetDay === todayStr;
  let rainSoon = null;
  let rainLaterToday = null;

  for (let i = 0; i < hourly.time.length; i++) {
    const t = new Date(hourly.time[i]);
    if (Number.isNaN(t.getTime()) || t <= now) continue;

    // Only evaluate rain for the remainder of the current day.
    if (isTodayTarget) {
      const isSameDay = t.getFullYear() === todayY && t.getMonth() === todayM && t.getDate() === todayD;
      if (!isSameDay) continue;
    } else {
      const rowDate = toLocalDateString(t);
      if (rowDate !== targetDay) continue;
    }

    const delta = t.getTime() - now.getTime();
    const precipProb = Number(hourly.precipitation_probability?.[i] || 0);
    const precipMm = Number(hourly.precipitation?.[i] || 0);
    const hourlyWind = Number(hourly.wind_speed_10m?.[i] || 0);
    const isRainySlot = precipMm > 0;

    if (!isRainySlot) continue;

    const rainPoint = {
      hoursAhead: Math.max(1, Math.round(delta / (60 * 60 * 1000))),
      precipProb,
      wind: hourlyWind
    };

    if (isTodayTarget && delta <= sixHours) {
      rainSoon = rainPoint;
      break;
    }

    if (!rainLaterToday) {
      rainLaterToday = rainPoint;
    }
  }

  if (rainSoon) {
    let protectionAdvice = '';
    if (rainSoon.wind >= 18) {
      protectionAdvice = `Rain may start in about ${rainSoon.hoursAhead} hour(s) and wind may be around ${Math.round(rainSoon.wind)} mph. Prefer a hooded raincoat over an umbrella.`;
    } else {
      protectionAdvice = `Rain may start in about ${rainSoon.hoursAhead} hour(s) with lighter wind (~${Math.round(rainSoon.wind)} mph). Carry an umbrella.`;
    }

    return {
      futureNote: `It looks dry now, but rain is likely within the next ${rainSoon.hoursAhead} hour(s) (${Math.round(rainSoon.precipProb)}% chance).`,
        protectionAdvice,
        rainExpected: true
    };
  }

  if (rainLaterToday) {
    if (!isTodayTarget) {
      return {
        futureNote: `Rain is forecast on ${formatShortDate(targetDay)} (around ${rainLaterToday.hoursAhead}h from now view).`,
        protectionAdvice: 'Carry rain protection for that day. Use a raincoat if winds are strong.',
        rainExpected: true
      };
    }

    return {
      futureNote: `No immediate rain signal, but rain may develop in around ${rainLaterToday.hoursAhead} hour(s) (${Math.round(rainLaterToday.precipProb)}% chance).`,
        protectionAdvice: 'Consider carrying foldable rain protection if you will be out for long.',
        rainExpected: true
    };
  }

  return {
    futureNote: 'No rain forecast for the rest of today.',
      protectionAdvice: '',
      rainExpected: false
  };
}

function getWeatherScene(condition, temp, shortTerm) {
  const c = (condition || '').toLowerCase();
    const rainSoon = !!shortTerm?.rainExpected;

  if (c.includes('thunder')) {
    return {
      themeClass: 'storm',
      title: 'Storm Alert Look',
      subtitle: 'Keep waterproof layers and avoid flimsy umbrellas.',
      mainEmoji: '⛈️',
      sideEmoji: '🧥'
    };
  }

  if (c.includes('rain') || c.includes('drizzle') || c.includes('shower')) {
    return {
      themeClass: 'rain',
      title: 'Rainy Street Scene',
      subtitle: 'Umbrella if winds are light, raincoat if it is gusty.',
      mainEmoji: '🌧️',
      sideEmoji: '☂️'
    };
  }

  if (temp >= 29) {
    return {
      themeClass: 'hot',
      title: 'Beach Weather Vibe',
      subtitle: 'Keep fabrics breathable and stay hydrated.',
      mainEmoji: '🏖️',
      sideEmoji: '🕶️'
    };
  }

  if (c.includes('snow') || temp <= 8) {
    return {
      themeClass: 'cold',
      title: 'Cold Weather Mode',
      subtitle: 'Layer up and prefer insulated outerwear.',
      mainEmoji: '❄️',
      sideEmoji: '🧤'
    };
  }

  if (c.includes('wind') || c.includes('overcast')) {
    return {
      themeClass: 'windy',
      title: 'Breezy City Mood',
      subtitle: 'A light jacket can keep you comfortable outdoors.',
      mainEmoji: '🌬️',
      sideEmoji: '🧥'
    };
  }

  if (rainSoon) {
    return {
      themeClass: 'sunny-rain-later',
      title: 'Sunny Now, Rain Later',
      subtitle: 'Carry foldable rain protection just in case.',
      mainEmoji: '🌤️',
      sideEmoji: '☔'
    };
  }

  return {
    themeClass: 'clear',
    title: 'Clear Day Style',
    subtitle: 'Great conditions for lightweight outfits.',
    mainEmoji: '☀️',
    sideEmoji: '👟'
  };
}

function getOutfitForWeather(condition, temp, occ) {
  const c = condition.toLowerCase();
  const isHot = temp >= 25;
  const isCold = temp <= 10;
  const isRainy = c.includes('rain') || c.includes('drizzle') || c.includes('shower');
  const isSnowy = c.includes('snow');
  const isWarm = temp >= 15 && temp < 25;

  const base = {
    College: {
      hot: 'Breathable tee or shirt + shorts/chinos, or a light dress, with sneakers/sandals',
      warm: 'Casual shirt or top + jeans/chinos, or a midi dress, with sneakers',
      cold: 'Hoodie/sweater + jeans/trousers, or a knit dress + jacket, with sneakers/boots',
      rain: 'Waterproof jacket + jeans/trousers, or a weather-safe dress + layer, with water-resistant shoes',
      snow: 'Thick coat + thermal layers + trousers, or warm knit dress + tights, with insulated boots'
    },
    Office: {
      hot: 'Breathable shirt/blouse + chinos/trousers, or a structured dress, with loafers/flats',
      warm: 'Blazer + tailored trousers, or a midi dress + blazer, with loafers/heels',
      cold: 'Wool layers + formal trousers, or long-sleeve dress + coat, with leather shoes/boots',
      rain: 'Trench/raincoat + dark trousers, or dress + water-safe layer, with waterproof shoes',
      snow: 'Wool coat + insulated formal layers, or warm dress + tights + coat, with insulated footwear'
    },
    Party: {
      hot: 'Linen shirt + tailored bottoms, or a breezy dress, with sandals/loafers',
      warm: 'Fitted blazer + smart pants, or cocktail dress/jumpsuit, with heels/derbies',
      cold: 'Layered party look: blazer/suit or dress + cardigan, with boots',
      rain: 'Chic rain layer over party wear (suit or dress), with water-friendly boots',
      snow: 'Warm statement coat over evening wear (suit or dress), with insulated boots'
    },
    'Casual Day Out': {
      hot: 'Tank/tee + shorts or relaxed pants, or a light dress, with sandals/sneakers',
      warm: 'Light sweater or shirt + jeans/joggers, or a casual dress + light layer, with sneakers',
      cold: 'Puffer/jacket + joggers/jeans, or knit dress + tights + layer, with trainers/boots',
      rain: 'Rain jacket + quick-dry bottoms, or dress + raincoat, with waterproof boots/sneakers',
      snow: 'Parka + thermal base + warm bottoms, or warm dress + leggings, with snow boots'
    }
  };

  const occOutfits = base[occ] || base['Casual Day Out'];
  if (isSnowy) return occOutfits.snow;
  if (isRainy) return occOutfits.rain;
  if (isCold) return occOutfits.cold;
  if (isHot) return occOutfits.hot;
  return occOutfits.warm;
}

async function searchLocationsByName(query) {
  const url = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(query)}&count=8&language=en&format=json`;
  const res = await fetch(url);
  const data = await res.json();
  if (!data || !data.results || data.results.length === 0) {
    return [];
  }

  return data.results.map((item) => {
    const cityLabelParts = [item.name, item.admin1, item.country].filter(Boolean);
    return {
      lat: item.latitude,
      lon: item.longitude,
      city: cityLabelParts.join(', ')
    };
  });
}

async function loadWeather(locationQuery) {
  const card = document.getElementById('weatherCard');
  if (!card) return;

  let lat, lon, city = 'Your Location';
  let forcedManualCoordinates = null;

  if (typeof locationQuery === 'string') {
    selectedLocationQuery = locationQuery.trim() || null;
  } else if (locationQuery === null) {
    selectedLocationQuery = null;
  } else if (locationQuery && typeof locationQuery === 'object' && Number.isFinite(locationQuery.lat) && Number.isFinite(locationQuery.lon)) {
    selectedLocationQuery = locationQuery.city || selectedLocationQuery;
    forcedManualCoordinates = locationQuery;
  }

  if (!selectedForecastDate) {
    selectedForecastDate = getTodayLocalDateString();
  }

  const usingManualLocation = !!selectedLocationQuery || !!forcedManualCoordinates;

  if (forcedManualCoordinates) {
    lat = forcedManualCoordinates.lat;
    lon = forcedManualCoordinates.lon;
    city = forcedManualCoordinates.city || selectedLocationQuery || 'Selected Location';
  } else if (usingManualLocation) {
    try {
      const candidates = await searchLocationsByName(selectedLocationQuery);
      if (candidates.length === 0) {
        throw new Error('Location not found');
      }

      const manual = candidates[0];
      lat = manual.lat;
      lon = manual.lon;
      city = manual.city;
    } catch (_) {
      card.innerHTML = `<p style="color:#ef4444;">Could not find that location. Try a city name like "Hyderabad" or "London".</p>`;
      return;
    }
  }

  // Try browser geolocation (optional — skip if denied)
  if (!usingManualLocation) {
    try {
      const pos = await new Promise((resolve, reject) => {
        if (!navigator.geolocation) return reject(new Error('no geo'));
        navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 6000 });
      });
      lat = pos.coords.latitude;
      lon = pos.coords.longitude;
      // Reverse geocode for city name
      try {
        const geoRes = await fetch(
          `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`,
          { headers: { 'Accept-Language': 'en' } }
        );
        const geoData = await geoRes.json();
        city = geoData.address?.city || geoData.address?.town || geoData.address?.village || 'Your Location';
      } catch (_) {}
    } catch (_) {
      // Fallback: IP-based location
      try {
        const ipRes = await fetch('https://ipapi.co/json/');
        const ipData = await ipRes.json();
        lat = ipData.latitude; lon = ipData.longitude;
        city = ipData.city || 'Your Location';
      } catch (_) {
        // Last resort defaults
        lat = 52.52; lon = 13.41; city = 'Berlin';
      }
    }
  }

  // Fetch real weather from Open-Meteo (free, no key)
  try {
    const wRes = await fetch(
      `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m,wind_gusts_10m&hourly=temperature_2m,apparent_temperature,weather_code,precipitation_probability,precipitation,wind_speed_10m,wind_gusts_10m&forecast_days=7&timezone=auto&wind_speed_unit=mph`
    );
    const wData = await wRes.json();
    const forecastDate = selectedForecastDate || getTodayLocalDateString();
    const todayStr = getTodayLocalDateString();
    const useCurrent = forecastDate === todayStr;

    const forecastRow = useCurrent ? null : findForecastSnapshotForDate(wData.hourly, forecastDate);

    const baseTemp = useCurrent ? wData.current.temperature_2m : forecastRow?.temperature;
    const baseFeels = useCurrent ? wData.current.apparent_temperature : forecastRow?.feelsLike;
    const baseCode = useCurrent ? wData.current.weather_code : forecastRow?.code;
    const baseWind = useCurrent ? wData.current.wind_speed_10m : forecastRow?.wind;
    const baseGust = useCurrent ? (wData.current.wind_gusts_10m || wData.current.wind_speed_10m) : (forecastRow?.gust || forecastRow?.wind);

    if (!Number.isFinite(baseTemp) || !Number.isFinite(baseFeels) || !Number.isFinite(baseWind) || !Number.isFinite(baseGust) || baseCode === undefined || baseCode === null) {
      card.innerHTML = `<p style="color:#ef4444;">Forecast not available for the selected date. Choose another date.</p>`;
      return;
    }

    const temp = Math.round(baseTemp);
    const feelsLike = Math.round(baseFeels);
    const condition = getWeatherCondition(baseCode);
    const wind = Math.round(baseWind);
    const gust = Math.round(baseGust);
    const icon = getWeatherIcon(condition);
    const occ = occasion ? occasion.value || 'Casual Day Out' : 'Casual Day Out';
    const outfitSuggestion = getOutfitForWeather(condition, temp, occ);
    const windSeverity = getWindSeverity(wind, gust);
    const shortTerm = analyzeShortTermRainOutlook(wData.hourly, wData.current.time, forecastDate);
    const scene = getWeatherScene(condition, temp, shortTerm);

    currentWeather = { temp, feelsLike, condition, city, shortTerm };

    // Update weather badge in outfit section
    const badge = document.getElementById('weatherBadge');
    if (badge) badge.textContent = `${condition}, ${temp}°C (${formatShortDate(forecastDate)})`;

    const inputValue = (selectedLocationQuery || city || '').replace(/"/g, '&quot;');

    card.innerHTML = `
      <div class="weather-main">
        <div class="weather-icon-big">${icon}</div>
        <div class="weather-info">
          <h3 id="weatherCity">${city}</h3>
          <p class="temp">${temp}°C &bull; ${condition}</p>
            <p class="weather-feels-like">Feels like ${feelsLike}°C</p>
            <p class="weather-wind">💨 Wind: ${wind} mph &bull; Gusts: ${gust} mph</p>
            <p class="weather-wind-status">${windSeverity.label} &mdash; ${windSeverity.note}</p>
        </div>
        <button class="weather-locate-btn" onclick="loadWeather()" title="Refresh location">📍 Refresh</button>
      </div>
      <div class="weather-location-tools">
        <input id="manualLocationInput" class="weather-location-input" type="text" value="${inputValue}" placeholder="Enter city/location (e.g., Hyderabad)">
        <input id="forecastDateInput" class="weather-date-input" type="date" value="${forecastDate}" min="${todayStr}">
        <button class="weather-locate-btn" onclick="applyManualLocation()" title="Use typed location">Use Location</button>
        <button class="weather-locate-btn" onclick="applyForecastDate()" title="Use selected date">Use Date</button>
        <button class="weather-locate-btn" onclick="clearManualLocation()" title="Switch back to automatic location">Use My Location</button>
      </div>
      <div id="locationDisambiguation" class="weather-location-choices" hidden></div>
      <div class="weather-scene ${scene.themeClass}">
        <div class="weather-scene-main" aria-hidden="true">${scene.mainEmoji}</div>
        <div class="weather-scene-content">
          <h4>${scene.title}</h4>
          <p>${scene.subtitle}</p>
        </div>
        <div class="weather-scene-side" aria-hidden="true">${scene.sideEmoji}</div>
      </div>
      <div class="weather-suggestion">
        <strong>Suggested outfit:</strong> ${outfitSuggestion}
          <p class="weather-future-note">🔎 ${shortTerm.futureNote}</p>
          ${shortTerm.protectionAdvice ? `<p class="weather-protection-note">🛡️ ${shortTerm.protectionAdvice}</p>` : ''}
      </div>
    `;
  } catch (e) {
    card.innerHTML = `<p style="color:#ef4444;">Could not load weather data. Check your connection.</p>`;
  }
}

function applyForecastDate() {
  const input = document.getElementById('forecastDateInput');
  if (!input || !input.value) {
    alert('Please choose a date.');
    return;
  }

  selectedForecastDate = input.value;
  loadWeather();
}

function renderLocationDisambiguation(candidates) {
  const wrapper = document.getElementById('locationDisambiguation');
  if (!wrapper) return;

  if (!candidates || candidates.length <= 1) {
    wrapper.hidden = true;
    wrapper.innerHTML = '';
    return;
  }

  const options = candidates
    .map((c, i) => `<option value="${i}">${c.city}</option>`)
    .join('');

  wrapper.hidden = false;
  wrapper.innerHTML = `
    <p class="weather-location-hint">Multiple matches found. Choose one:</p>
    <div class="weather-location-choice-row">
      <select id="manualLocationSelect" class="weather-location-select">${options}</select>
      <button class="weather-locate-btn" onclick="chooseManualLocationFromList()">Use Selected</button>
    </div>
  `;
}

async function applyManualLocation() {
  const input = document.getElementById('manualLocationInput');
  const query = input ? input.value.trim() : '';
  if (!query) {
    alert('Please enter a city or location.');
    return;
  }

  const candidates = await searchLocationsByName(query);
  if (candidates.length === 0) {
    alert('Location not found. Try a different city or add country name.');
    return;
  }

  manualLocationCandidates = candidates;

  if (candidates.length === 1) {
    const chosen = candidates[0];
    loadWeather({ lat: chosen.lat, lon: chosen.lon, city: chosen.city });
    return;
  }

  renderLocationDisambiguation(candidates);
}

function chooseManualLocationFromList() {
  const select = document.getElementById('manualLocationSelect');
  if (!select) return;

  const idx = Number(select.value);
  const chosen = manualLocationCandidates[idx];
  if (!chosen) return;

  loadWeather({ lat: chosen.lat, lon: chosen.lon, city: chosen.city });
}

function clearManualLocation() {
  manualLocationCandidates = [];
  loadWeather(null);
}

// Reload outfit suggestion when occasion changes
if (occasion) {
  occasion.addEventListener('change', () => {
    if (currentWeather.temp !== null) {
      const occ = occasion.value || 'Casual Day Out';
      const suggestion = getOutfitForWeather(currentWeather.condition, currentWeather.temp, occ);
      const card = document.getElementById('weatherCard');
      const suggEl = card?.querySelector('.weather-suggestion');
      if (suggEl) {
        const futureNote = currentWeather.shortTerm?.futureNote
          ? `<p class="weather-future-note">🔎 ${currentWeather.shortTerm.futureNote}</p>`
          : '';
        const protectionNote = currentWeather.shortTerm?.protectionAdvice
          ? `<p class="weather-protection-note">🛡️ ${currentWeather.shortTerm.protectionAdvice}</p>`
          : '';

        suggEl.innerHTML = `<strong>Suggested outfit:</strong> ${suggestion}${futureNote}${protectionNote}`;
      }
    }
  });
}

// ─── INIT ────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async function() {
  await checkAuthStatus();
  restoreFromStorage();      // load saved photos for the current authenticated user
  setupCategoryUploads();
  setupGenerateMoreBtn();
  loadWeather();
});

// Check if user is logged in
async function checkAuthStatus() {
  try {
    const response = await fetch('/api/auth/status');
    const data = await response.json();
    userAuthenticated = data.authenticated;

    if (userAuthenticated && data.user && data.user.id) {
      currentUserStorageKey = `${STORAGE_KEY_PREFIX}_${data.user.id}`;
    } else {
      currentUserStorageKey = null;
    }
  } catch (error) {
    console.log('Auth check failed:', error);
    userAuthenticated = false;
    currentUserStorageKey = null;
  }
}

// (Save button state handled per-card in renderOutfitOptions)

// Setup category upload handlers
function setupCategoryUploads() {
  const categories = ['tops', 'bottoms', 'dresses', 'shoes', 'outerwear'];
  
  categories.forEach(category => {
    const uploadInput = document.getElementById(`${category}Upload`);
    if (uploadInput) {
      uploadInput.addEventListener('change', function(e) {
        handleCategoryUpload(category, e.target.files);
      });
    }
  });
}

// Handle file uploads for each category — ADDITIVE (appends to existing)
function handleCategoryUpload(category, files) {
  if (!files || files.length === 0) return;
  
  let processed = 0;
  const fileCount = files.length;

  Array.from(files).forEach(file => {
    const reader = new FileReader();
    reader.onload = function(e) {
      try {
        resizeImage(e.target.result, 400, (dataUrl) => {
          try {
            categoryFiles[category].push({ url: dataUrl, name: file.name });
            processed++;
            
            // Render and save immediately after each file
            renderThumbnails(category);
            saveToStorage();
          } catch (err) {
            console.error('Error processing image:', err);
          }
        });
      } catch (err) {
        console.error('Error in FileReader callback:', err);
      }
    };
    reader.onerror = function() {
      console.error(`Failed to read file: ${file.name}`);
    };
    reader.readAsDataURL(file);
  });

  // Clear the file input
  const uploadInput = document.getElementById(`${category}Upload`);
  if (uploadInput) uploadInput.value = '';
}

// Resize an image dataUrl to max px on longest side
function resizeImage(dataUrl, maxPx, callback) {
  const img = new Image();
  img.onload = function() {
    const ratio = Math.min(maxPx / img.width, maxPx / img.height, 1);
    const w = Math.round(img.width * ratio);
    const h = Math.round(img.height * ratio);
    const canvas = document.createElement('canvas');
    canvas.width = w; canvas.height = h;
    canvas.getContext('2d').drawImage(img, 0, 0, w, h);
    callback(canvas.toDataURL('image/jpeg', 0.75));
  };
  img.src = dataUrl;
}

// Render thumbnails grid for a category
function renderThumbnails(category) {
  const listContainer = document.getElementById(`${category}List`);
  listContainer.innerHTML = '';

  if (categoryFiles[category].length === 0) return;

  const grid = document.createElement('div');
  grid.className = 'thumb-grid';

  categoryFiles[category].forEach((entry, index) => {
    const wrapper = document.createElement('div');
    wrapper.className = 'thumb-wrapper';
    wrapper.innerHTML = `
      <img src="${entry.url}" alt="${entry.name}" class="thumb-img">
      <button class="thumb-remove" title="Remove" onclick="removeUploadedItem('${category}', ${index})">×</button>
    `;
    grid.appendChild(wrapper);
  });

  // Add count badge
  const badge = document.createElement('div');
  badge.className = 'upload-count';
  badge.textContent = `${categoryFiles[category].length} item${categoryFiles[category].length !== 1 ? 's' : ''} added`;
  listContainer.appendChild(grid);
  listContainer.appendChild(badge);
}

// Remove a single uploaded item
function removeUploadedItem(category, index) {
  categoryFiles[category].splice(index, 1);
  renderThumbnails(category);
  saveToStorage();            // ← update storage after removal
}

// ─── LOCALSTORAGE PERSISTENCE ────────────────────────────
const STORAGE_KEY_PREFIX = 'wearitright_wardrobe_v4_user';

function saveToStorage() {
  try {
    if (!currentUserStorageKey) return;

    const data = {};
    ['tops', 'bottoms', 'dresses', 'shoes', 'outerwear'].forEach(cat => {
      data[cat] = categoryFiles[cat].map(f => ({ url: f.url, name: f.name }));
    });
    localStorage.setItem(currentUserStorageKey, JSON.stringify(data));
  } catch (e) {
    console.warn('Storage full — not all images saved:', e);
  }
}

function restoreFromStorage() {
  try {
    if (!currentUserStorageKey) return;

    const raw = localStorage.getItem(currentUserStorageKey);
    if (!raw) return;

    const data = JSON.parse(raw);
    ['tops', 'bottoms', 'dresses', 'shoes', 'outerwear'].forEach(cat => {
      if (data[cat] && data[cat].length > 0) {
        categoryFiles[cat] = data[cat];
        renderThumbnails(cat);
      }
    });
  } catch (e) {
    console.warn('Could not restore from storage:', e);
  }
}

// Validate that we have required categories
// Dresses don't need a separate bottom — dress + shoes is valid
// Bottoms are optional — you can wear just tops/dresses with shoes
function validateCategories() {
  const hasDresses = categoryFiles.dresses.length > 0;
  const hasTops    = categoryFiles.tops.length > 0;
  const hasBottoms = categoryFiles.bottoms.length > 0;
  const hasShoes   = categoryFiles.shoes.length > 0;

  const missing = [];
  if (!hasDresses && !hasTops) missing.push('Tops or Dresses');
  if (!hasShoes) missing.push('Shoes');

  // Valid if: (dresses OR tops) AND shoes
  // Bottoms and Outerwear are optional
  const valid = (hasDresses || hasTops) && hasShoes;
  return { valid, missing };
}

// Pick a random entry from a category array
function pickRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

// Build ai notes by occasion + style vibe + actual weather
function buildAiNote(occ, vibe) {
  const weatherStr = currentWeather.temp !== null
    ? `${currentWeather.condition} at ${currentWeather.temp}°C`
    : 'current weather';
  const vibeStr = vibe ? `with a ${vibe} edge` : '';
  const notes = {
    'College': `A laid-back ${vibe || 'student'} look ${vibeStr} curated for ${weatherStr}.`,
    'Office': `A polished, ${vibe || 'professional'} combination ${vibeStr} suited to ${weatherStr}.`,
    'Party': `A ${vibe || 'bold'}, eye-catching outfit ${vibeStr} ready to turn heads — styled for ${weatherStr}.`,
    'Casual Day Out': `Easy, ${vibe || 'breezy'} vibes ${vibeStr} perfect for a relaxed day out in ${weatherStr}.`
  };
  return notes[occ] || `A ${vibe || 'stylish'} combination ${vibeStr} curated for ${weatherStr}.`;
}

// Generate 3 distinct outfit combinations and display them
// Fixes: dress never paired with a separate bottom; style vibe applied; optional outerwear
function generateOutfitCombination() {
  const validation = validateCategories();
  if (!validation.valid) {
    alert(`❌ Missing items: ${validation.missing.join(', ')}\n\nPlease upload at least one item from each required category.`);
    return;
  }

  const occ = occasion.value;
  const styleVibeEl = document.getElementById('styleVibe');
  const vibe = styleVibeEl ? styleVibeEl.value : '';
  const aiNote = buildAiNote(occ, vibe);
  const outfits = [];

  const hasDresses = categoryFiles.dresses.length > 0;
  const hasTops    = categoryFiles.tops.length > 0;
  const hasBottoms = categoryFiles.bottoms.length > 0;
  const hasOuterwear = categoryFiles.outerwear.length > 0;

  // Style vibe preference: elegant/bohemian/romantic prefer dresses;
  // sporty/preppy prefer tops+bottoms
  const dressPreferVibes = ['elegant', 'bohemian', 'romantic', 'vintage'];
  const topPreferVibes   = ['sporty', 'preppy', 'funky', 'edgy'];
  let dressWeight = 0.5; // default: 50% chance
  if (dressPreferVibes.includes(vibe) && hasDresses) dressWeight = 0.8;
  if (topPreferVibes.includes(vibe) && hasTops)      dressWeight = 0.2;
  if (!hasDresses) dressWeight = 0;
  if (!hasTops || !hasBottoms) dressWeight = 1;

  const usedCombos = new Set();
  let attempts = 0;
  while (outfits.length < 3 && attempts < 40) {
    attempts++;
    const useDress = Math.random() < dressWeight;

    let top, bottom = null, isDress = false;
    if (useDress && hasDresses) {
      top = pickRandom(categoryFiles.dresses);
      isDress = true;        // ← NO separate bottom for dresses
    } else if (hasTops && hasBottoms) {
      top    = pickRandom(categoryFiles.tops);
      bottom = pickRandom(categoryFiles.bottoms);
    } else if (hasTops) {
      // Tops only (bottoms optional)
      top = pickRandom(categoryFiles.tops);
    } else if (hasDresses) {
      top = pickRandom(categoryFiles.dresses);
      isDress = true;
    } else {
      continue;  // can't build a valid combo
    }

    const shoe = pickRandom(categoryFiles.shoes);
    
    // Optionally add outerwear (40% chance if available)
    const outerwear = (hasOuterwear && Math.random() < 0.4) ? pickRandom(categoryFiles.outerwear) : null;
    
    const key = `${top.url}|${bottom ? bottom.url : 'nobottom'}|${shoe.url}|${outerwear ? outerwear.url : 'noouterwear'}`;
    if (!usedCombos.has(key)) {
      usedCombos.add(key);
      outfits.push({ top, bottom, shoe, isDress, outerwear });
    }
  }

  selectedOccasion.textContent = occ;
  const weatherBadge = document.getElementById('weatherBadge');
  const weatherDisplay = currentWeather.temp !== null
    ? `${currentWeather.condition}, ${currentWeather.temp}°C`
    : 'Cloudy, 18°C';
  if (weatherBadge) weatherBadge.textContent = weatherDisplay;

  chosenOutfit = null;
  renderOutfitOptions(outfits, occ, aiNote, vibe);

  recommendationSection.hidden = false;
  recommendationSection.scrollIntoView({ behavior: 'smooth' });
}

// Render outfit option cards — respects dress/top compatibility and optional outerwear
function renderOutfitOptions(outfits, occ, aiNote, vibe) {
  outfitOptionsGrid.innerHTML = '';
  const matchScores = [94, 88, 91];

  outfits.forEach((outfit, i) => {
    const card = document.createElement('div');
    card.className = 'outfit-option-card';
    card.dataset.index = i;

    const vibeBadge = vibe ? ` · <span style="color:#7c3aed">${vibe}</span>` : '';
    const weatherDisplay = currentWeather.temp !== null
      ? `${currentWeather.condition}, ${currentWeather.temp}°C` : 'Cloudy, 18°C';

    // Build items HTML: outerwear on top, then core items, then shoes
    let itemsHtml = '';
    
    // Add outerwear first (if present)
    if (outfit.outerwear) {
      itemsHtml += `
        <div class="option-item option-wide">
          <img src="${outfit.outerwear.url}" alt="Outerwear">
          <span>🧥 Outerwear</span>
        </div>`;
    }
    
    // Add core items
    if (outfit.isDress) {
      itemsHtml += `
        <div class="option-item option-wide">
          <img src="${outfit.top.url}" alt="Dress">
          <span>👗 Dress</span>
        </div>`;
    } else {
      itemsHtml += `
        <div class="option-item">
          <img src="${outfit.top.url}" alt="Top">
          <span>👕 Top</span>
        </div>`;
      if (outfit.bottom) {
        itemsHtml += `
        <div class="option-item">
          <img src="${outfit.bottom.url}" alt="Bottom">
          <span>👖 Bottom</span>
        </div>`;
      }
    }
    
    // Add shoes
    itemsHtml += `
        <div class="option-item">
          <img src="${outfit.shoe.url}" alt="Shoes">
          <span>👞 Shoes</span>
        </div>`;

    const safeNote = aiNote.replace(/'/g, '&apos;').replace(/"/g, '&quot;');
    card.innerHTML = `
      <div class="option-badge">Option ${i + 1} · ${matchScores[i]}%${vibeBadge}</div>
      <div class="option-items">${itemsHtml}</div>
      <div class="option-meta">
        <p><strong>Occasion:</strong> ${occ}${vibe ? ` &bull; <em>${vibe} vibe</em>` : ''}</p>
        <p><strong>Weather:</strong> ${weatherDisplay}</p>
        <p class="option-note">${aiNote}</p>
      </div>
      <div class="option-actions">
        <button class="choose-btn" onclick="chooseOutfit(${i}, '${occ}', '${safeNote}', '${vibe || ''}')">
          💾 Save This Outfit
        </button>
      </div>
    `;
    outfitOptionsGrid.appendChild(card);
  });

  outfitOptionsGrid._outfits = outfits;
}

// User chose a specific outfit to save
async function chooseOutfit(index, occ, aiNote, vibe) {
  if (!userAuthenticated) {
    alert('Please login to save outfits.');
    window.location.href = '/login';
    return;
  }

  const outfits = outfitOptionsGrid._outfits;
  const outfit = outfits[index];

  const outfitData = {
    occasion: occ,
    items: {
      outerwear: outfit.outerwear ? `Outerwear: ${outfit.outerwear.name}` : null,
      top: outfit.isDress ? `Dress: ${outfit.top.name}` : `Top: ${outfit.top.name}`,
      bottom: outfit.isDress ? null : (outfit.bottom ? `Bottom: ${outfit.bottom.name}` : null),
      shoes: `Shoes: ${outfit.shoe.name}`
    },
    weather: currentWeather.temp !== null
      ? `${currentWeather.condition}, ${currentWeather.temp}°C` : 'Cloudy, 18°C',
    aiNote: aiNote + (vibe ? ` (${vibe} style)` : '')
  };

  // Highlight selected card
  document.querySelectorAll('.outfit-option-card').forEach(c => c.classList.remove('selected'));
  const selectedCard = outfitOptionsGrid.querySelector(`[data-index="${index}"]`);
  if (selectedCard) selectedCard.classList.add('selected');

  const btn = selectedCard.querySelector('.choose-btn');
  btn.disabled = true;
  btn.textContent = 'Saving…';

  try {
    const response = await fetch('/api/outfit/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(outfitData)
    });
    const data = await response.json();
    if (response.ok) {
      btn.textContent = '✓ Saved!';
      btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
      alert('✓ Outfit saved to your wardrobe!');
    } else {
      btn.textContent = '💾 Save This Outfit';
      btn.disabled = false;
      alert('Error: ' + data.message);
    }
  } catch (err) {
    console.error('Error saving outfit:', err);
    btn.textContent = '💾 Save This Outfit';
    btn.disabled = false;
    alert('Failed to save outfit. Please try again.');
  }
}

// Generate Outfit button
if (generateBtn) {
  generateBtn.addEventListener('click', function () {
    if (occasion.value === '') {
      alert('Please select an occasion.');
      return;
    }
    generateOutfitCombination();
  });
}

// Generate More Options button
function setupGenerateMoreBtn() {
  const moreBtn = document.getElementById('generateMoreBtn');
  if (moreBtn) {
    moreBtn.addEventListener('click', function () {
      if (occasion.value === '') {
        alert('Please select an occasion first.');
        return;
      }
      generateOutfitCombination();
    });
  }
}

// Trending outfit cards — clicking fills the occasion and scrolls to upload
const outfitButtons = document.querySelectorAll('.outfit-card button');
outfitButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const card = button.closest('.outfit-card');
    const heading = card?.querySelector('h3');
    const title = heading?.textContent || '';

    // Map trending card headings to occasion options
    const map = {
      'College Casual': 'College',
      'Office Ready': 'Office',
      'Winter Street Style': 'Casual Day Out'
    };
    const occ = map[title] || '';
    if (occ && occasion) {
      occasion.value = occ;
    }

    const uploadSection = document.getElementById('wardrobe');
    if (uploadSection) uploadSection.scrollIntoView({ behavior: 'smooth' });
  });
});