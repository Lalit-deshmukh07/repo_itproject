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
  shoes: []
};

// The outfit the user chose to save
let chosenOutfit = null;
let userAuthenticated = false;

// Current weather data (updated by loadWeather)
let currentWeather = { temp: null, condition: 'Clear', city: '' };

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

function getOutfitForWeather(condition, temp, occ) {
  const c = condition.toLowerCase();
  const isHot = temp >= 25;
  const isCold = temp <= 10;
  const isRainy = c.includes('rain') || c.includes('drizzle') || c.includes('shower');
  const isSnowy = c.includes('snow');
  const isWarm = temp >= 15 && temp < 25;

  const base = {
    College: {
      hot: 'Light t-shirt, shorts, sneakers',
      warm: 'Casual shirt, jeans, sneakers',
      cold: 'Hoodie, jeans, sneakers & light jacket',
      rain: 'Waterproof jacket, jeans, ankle boots',
      snow: 'Thick coat, thermal jeans, boots'
    },
    Office: {
      hot: 'Breathable dress shirt, chinos, loafers',
      warm: 'Blazer, dress trousers, oxford shoes',
      cold: 'Wool suit, overcoat, leather shoes',
      rain: 'Trench coat, dark trousers, waterproof shoes',
      snow: 'Wool coat, formal trousers, insulated shoes'
    },
    Party: {
      hot: 'Stylish sundress or linen shirt, sandals',
      warm: 'Cocktail dress or fitted blazer, heels',
      cold: 'Party dress with cardigan or suit, boots',
      rain: 'Chic raincoat, party dress, ankle boots',
      snow: 'Glamorous coat, evening wear, boots'
    },
    'Casual Day Out': {
      hot: 'Tank top, shorts, flip-flops or sandals',
      warm: 'Light sweater, casual jeans, sneakers',
      cold: 'Puffer jacket, joggers, trainers',
      rain: 'Rain jacket, waterproof pants, boots',
      snow: 'Parka, thermal base, snow boots'
    }
  };

  const occOutfits = base[occ] || base['Casual Day Out'];
  if (isSnowy) return occOutfits.snow;
  if (isRainy) return occOutfits.rain;
  if (isCold) return occOutfits.cold;
  if (isHot) return occOutfits.hot;
  return occOutfits.warm;
}

async function loadWeather() {
  const card = document.getElementById('weatherCard');
  if (!card) return;

  let lat, lon, city = 'Your Location';

  // Try browser geolocation (optional — skip if denied)
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

  // Fetch real weather from Open-Meteo (free, no key)
  try {
    const wRes = await fetch(
      `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,weather_code,wind_speed_10m&wind_speed_unit=mph`
    );
    const wData = await wRes.json();
    const temp = Math.round(wData.current.temperature_2m);
    const condition = getWeatherCondition(wData.current.weather_code);
    const wind = Math.round(wData.current.wind_speed_10m);
    const icon = getWeatherIcon(condition);
    const occ = occasion ? occasion.value || 'Casual Day Out' : 'Casual Day Out';
    const outfitSuggestion = getOutfitForWeather(condition, temp, occ);

    currentWeather = { temp, condition, city };

    // Update weather badge in outfit section
    const badge = document.getElementById('weatherBadge');
    if (badge) badge.textContent = `${condition}, ${temp}°C`;

    card.innerHTML = `
      <div class="weather-main">
        <div class="weather-icon-big">${icon}</div>
        <div class="weather-info">
          <h3 id="weatherCity">${city}</h3>
          <p class="temp">${temp}°C &bull; ${condition}</p>
          <p class="weather-wind">💨 Wind: ${wind} mph</p>
        </div>
        <button class="weather-locate-btn" onclick="loadWeather()" title="Refresh location">📍 Refresh</button>
      </div>
      <div class="weather-suggestion">
        <strong>Suggested outfit:</strong> ${outfitSuggestion}
      </div>
    `;
  } catch (e) {
    card.innerHTML = `<p style="color:#ef4444;">Could not load weather data. Check your connection.</p>`;
  }
}

// Reload outfit suggestion when occasion changes
if (occasion) {
  occasion.addEventListener('change', () => {
    if (currentWeather.temp !== null) {
      const occ = occasion.value || 'Casual Day Out';
      const suggestion = getOutfitForWeather(currentWeather.condition, currentWeather.temp, occ);
      const card = document.getElementById('weatherCard');
      const suggEl = card?.querySelector('.weather-suggestion');
      if (suggEl) suggEl.innerHTML = `<strong>Suggested outfit:</strong> ${suggestion}`;
    }
  });
}

// ─── INIT ────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function() {
  checkAuthStatus();
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
  } catch (error) {
    console.log('Auth check failed:', error);
    userAuthenticated = false;
  }
}

// (Save button state handled per-card in renderOutfitOptions)

// Setup category upload handlers
function setupCategoryUploads() {
  const categories = ['tops', 'bottoms', 'dresses', 'shoes'];
  
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
  // Append new files to existing ones (don't replace)
  const newEntries = Array.from(files).map(file => ({
    url: URL.createObjectURL(file),
    name: file.name
  }));
  categoryFiles[category] = [...categoryFiles[category], ...newEntries];
  renderThumbnails(category);
  // Reset the input so the same file can be added again if needed
  document.getElementById(`${category}Upload`).value = '';
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
  URL.revokeObjectURL(categoryFiles[category][index].url);
  categoryFiles[category].splice(index, 1);
  renderThumbnails(category);
}

// Validate that we have required categories
function validateCategories() {
  const hasContent = (categoryFiles.tops.length > 0 || categoryFiles.dresses.length > 0) &&
                     categoryFiles.bottoms.length > 0 &&
                     categoryFiles.shoes.length > 0;
  
  const missing = [];
  if (categoryFiles.tops.length === 0 && categoryFiles.dresses.length === 0) {
    missing.push('Tops or Dresses');
  }
  if (categoryFiles.bottoms.length === 0) {
    missing.push('Bottoms');
  }
  if (categoryFiles.shoes.length === 0) {
    missing.push('Shoes');
  }
  
  return { valid: hasContent, missing };
}

// Pick a random entry from a category array
function pickRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

// Build ai notes by occasion + actual weather
function buildAiNote(occ) {
  const weatherStr = currentWeather.temp !== null
    ? `${currentWeather.condition} at ${currentWeather.temp}°C`
    : 'current weather';
  const notes = {
    'College': `A laid-back student look curated for ${weatherStr} — comfortable yet stylish for campus life.`,
    'Office': `A polished, professional combination suited to ${weatherStr} that means business.`,
    'Party': `A bold, eye-catching outfit ready to turn heads tonight — styled for ${weatherStr}.`,
    'Casual Day Out': `Easy, breezy vibes perfect for a relaxed day out in ${weatherStr}.`
  };
  return notes[occ] || `A stylish combination curated for ${weatherStr}.`;
}

// Generate 3 distinct outfit combinations and display them
function generateOutfitCombination() {
  const validation = validateCategories();

  if (!validation.valid) {
    alert(`❌ Missing items: ${validation.missing.join(', ')}\n\nPlease upload at least one item from each required category.`);
    return;
  }

  const occ = occasion.value;
  const aiNote = buildAiNote(occ);
  const outfits = [];

  // Generate up to 3 distinct combinations
  const usedCombos = new Set();
  let attempts = 0;
  while (outfits.length < 3 && attempts < 30) {
    attempts++;
    const topPool = categoryFiles.dresses.length > 0 && Math.random() > 0.5
      ? categoryFiles.dresses
      : categoryFiles.tops;
    const top = pickRandom(topPool);
    const bottom = pickRandom(categoryFiles.bottoms);
    const shoe = pickRandom(categoryFiles.shoes);
    const key = `${top.url}|${bottom.url}|${shoe.url}`;
    if (!usedCombos.has(key)) {
      usedCombos.add(key);
      outfits.push({ top, bottom, shoe });
    }
  }

  selectedOccasion.textContent = occ;
  const weatherBadge = document.getElementById('weatherBadge');
  const weatherDisplay = currentWeather.temp !== null
    ? `${currentWeather.condition}, ${currentWeather.temp}°C`
    : 'Cloudy, 18°C';
  if (weatherBadge) weatherBadge.textContent = weatherDisplay;

  chosenOutfit = null;
  renderOutfitOptions(outfits, occ, aiNote);

  recommendationSection.hidden = false;
  recommendationSection.scrollIntoView({ behavior: 'smooth' });
}

// Render 3 outfit option cards
function renderOutfitOptions(outfits, occ, aiNote) {
  outfitOptionsGrid.innerHTML = '';

  outfits.forEach((outfit, i) => {
    const card = document.createElement('div');
    card.className = 'outfit-option-card';
    card.dataset.index = i;

    const matchScores = [94, 88, 91];

    card.innerHTML = `
      <div class="option-badge">Option ${i + 1} &nbsp;·&nbsp; ${matchScores[i]}% match</div>
      <div class="option-items">
        <div class="option-item">
          <img src="${outfit.top.url}" alt="Top">
          <span>Top / Dress</span>
        </div>
        <div class="option-item">
          <img src="${outfit.bottom.url}" alt="Bottom">
          <span>Bottom</span>
        </div>
        <div class="option-item">
          <img src="${outfit.shoe.url}" alt="Shoes">
          <span>Shoes</span>
        </div>
      </div>
      <div class="option-meta">
        <p><strong>Occasion:</strong> ${occ}</p>
        <p><strong>Weather:</strong> Cloudy, 18°C</p>
        <p class="option-note">${aiNote}</p>
      </div>
      <div class="option-actions">
        <button class="choose-btn" onclick="chooseOutfit(${i}, '${occ}', '${aiNote.replace(/'/g, "&apos;")}')">
          💾 Save This Outfit
        </button>
      </div>
    `;
    outfitOptionsGrid.appendChild(card);
  });

  // Store outfits for save handler
  outfitOptionsGrid._outfits = outfits;
}

// User chose a specific outfit to save
async function chooseOutfit(index, occ, aiNote) {
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
      top: outfit.top.name || 'Top/Dress',
      bottom: outfit.bottom.name || 'Bottom',
      shoes: outfit.shoe.name || 'Shoes'
    },
    weather: currentWeather.temp !== null
      ? `${currentWeather.condition}, ${currentWeather.temp}°C`
      : 'Cloudy, 18°C',
    aiNote: aiNote
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