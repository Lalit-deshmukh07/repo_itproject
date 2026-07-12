// Fetch and display user profile data
async function loadProfile() {
  try {
    const authResponse = await fetch('/api/auth/status');
    const authData = await authResponse.json();

    if (!authData.authenticated) {
      window.location.href = '/login';
      return;
    }

    const user = authData.user;
    document.getElementById('userName').textContent = `Welcome, ${user.name}!`;
    document.getElementById('userEmail').textContent = user.email;

    // Load preferences
    await loadPreferences();

    // Load recommendations
    await loadRecommendations();

    // Load wardrobe (saved outfits)
    await loadWardrobe();
  } catch (error) {
    console.error('Error loading profile:', error);
  }
}

// Load user preferences
async function loadPreferences() {
  try {
    const response = await fetch('/api/user/preferences');
    const data = await response.json();

    if (data.preferences) {
      const prefs = data.preferences;
      document.getElementById('userGender').textContent = prefs.gender || 'Not set';
      document.getElementById('userTopSize').textContent = prefs.topSize || 'Not set';
      document.getElementById('userBottomSize').textContent = prefs.bottomSize || 'Not set';

      // Display style preferences
      const stylesList = document.getElementById('stylesList');
      stylesList.innerHTML = '';
      if (prefs.styles && prefs.styles.length > 0) {
        prefs.styles.forEach(style => {
          const tag = document.createElement('span');
          tag.className = 'style-tag';
          tag.textContent = style;
          stylesList.appendChild(tag);
        });
      } else {
        stylesList.innerHTML = '<p style="color: #999;">No style preferences set yet</p>';
      }
    }
  } catch (error) {
    console.error('Error loading preferences:', error);
  }
}

// Load recommendations based on style — with fashion images
async function loadRecommendations() {
  try {
    const response = await fetch('/api/recommendations');
    const data = await response.json();

    const container = document.getElementById('recommendationsContainer');
    container.innerHTML = '';

    if (data.recommendations && data.recommendations.length > 0) {
      data.recommendations.forEach(rec => {
        const card = document.createElement('div');
        card.className = 'recommendation-card';
        card.innerHTML = `
          <div class="rec-img-wrap">
            <img src="${rec.image || 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&auto=format&fit=crop'}"
                 alt="${rec.title}" class="rec-img"
                 onerror="this.src='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&auto=format&fit=crop'">
          </div>
          <div class="rec-body">
            <h3>${rec.title}</h3>
            <p>${rec.description}</p>
          </div>
        `;
        container.appendChild(card);
      });
    } else {
      container.innerHTML = '<p class="no-recs">Complete your profile to get personalised recommendations!</p>';
    }
  } catch (error) {
    console.error('Error loading recommendations:', error);
    document.getElementById('recommendationsContainer').innerHTML =
      '<p style="color:#ef4444;">Could not load recommendations.</p>';
  }
}

// Occasion icons for wardrobe cards
const occasionIcons = {
  'College': '🎓',
  'Office': '💼',
  'Party': '🎉',
  'Casual Day Out': '🌿',
  'default': '👗'
};

// Load saved outfits (wardrobe) — shows exact items saved, no stock photos
async function loadWardrobe() {
  try {
    const response = await fetch('/api/outfit/get-all');
    const data = await response.json();

    const container = document.getElementById('wardrobeContainer');
    container.innerHTML = '';

    if (data.outfits && data.outfits.length > 0) {
      data.outfits.forEach(outfit => {
        const card = document.createElement('div');
        card.className = 'outfit-card';

        const date = new Date(outfit.createdAt).toLocaleDateString('en-GB', {
          day: '2-digit', month: 'short', year: 'numeric'
        });

        const icon = occasionIcons[outfit.occasion] || occasionIcons['default'];
        const outerwearLabel = outfit.items?.outerwear || '—';
        const topLabel = outfit.items?.top || '—';
        const bottomLabel = outfit.items?.bottom || '—';
        const shoesLabel = outfit.items?.shoes || '—';

        // Build item rows dynamically
        let itemsRows = '';
        if (outerwearLabel !== '—') {
          itemsRows += `
            <div class="outfit-item-row">
              <span class="item-icon">🧥</span>
              <div class="item-detail">
                <span class="item-label">Outerwear</span>
                <span class="item-name">${outerwearLabel}</span>
              </div>
            </div>`;
        }
        itemsRows += `
            <div class="outfit-item-row">
              <span class="item-icon">👕</span>
              <div class="item-detail">
                <span class="item-label">Top / Dress</span>
                <span class="item-name">${topLabel}</span>
              </div>
            </div>`;
        if (bottomLabel !== '—') {
          itemsRows += `
            <div class="outfit-item-row">
              <span class="item-icon">👖</span>
              <div class="item-detail">
                <span class="item-label">Bottom</span>
                <span class="item-name">${bottomLabel}</span>
              </div>
            </div>`;
        }
        itemsRows += `
            <div class="outfit-item-row">
              <span class="item-icon">👞</span>
              <div class="item-detail">
                <span class="item-label">Shoes</span>
                <span class="item-name">${shoesLabel}</span>
              </div>
            </div>`;

        card.innerHTML = `
          <div class="outfit-card-header">
            <span class="occasion-icon">${icon}</span>
            <h3 class="outfit-occasion">${outfit.occasion}</h3>
            <span class="weather-tag">🌤️ ${outfit.weather || 'Any weather'}</span>
          </div>
          <div class="outfit-items-list">
            ${itemsRows}
          </div>
          <div class="outfit-card-footer">
            <p class="outfit-note">${outfit.aiNote || 'Saved outfit'}</p>
            <span class="outfit-date">📅 ${date}</span>
          </div>
        `;
        container.appendChild(card);
      });
    } else {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">👗</div>
          <h3>Your wardrobe is empty</h3>
          <p>Generate and save outfits to build your wardrobe.</p>
          <a href="/" class="btn-primary">Generate Your First Outfit</a>
        </div>
      `;
    }
  } catch (error) {
    console.error('Error loading wardrobe:', error);
    const container = document.getElementById('wardrobeContainer');
    container.innerHTML = '<p style="color:#ef4444;">Could not load wardrobe. Please refresh.</p>';
  }
}

// Logout handler
document.getElementById('logoutBtn').addEventListener('click', async () => {
  try {
    const response = await fetch('/api/auth/logout', {
      method: 'POST'
    });

    if (response.ok) {
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
  } catch (error) {
    console.error('Error logging out:', error);
  }
});

// Load profile on page load
document.addEventListener('DOMContentLoaded', loadProfile);
