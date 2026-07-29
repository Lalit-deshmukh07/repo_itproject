// Fetch and display user profile data
async function loadProfile() {
  try {
    const authResponse = await fetch('/api/auth/status');
    const authData = await authResponse.json();

    if (!authData.authenticated) {
      window.location.href = '/login';
      return;
    }

    const user = authData.user || {};
    const name = user.name || 'there';
    document.getElementById('userName').textContent = `Welcome, ${name}!`;
    document.getElementById('userEmail').textContent = user.email || 'No email available';

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
        const modelImage = rec.modelImage || rec.image || 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&auto=format&fit=crop';
        card.innerHTML = `
          <div class="rec-img-wrap">
            <img src="${modelImage}"
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

        const occasionValue = outfit.occasion || 'Saved Outfit';
        const icon = occasionIcons[occasionValue] || occasionIcons['default'];
        const outfitItems = outfit.items || {};
        const outerwearItem = outfitItems.outerwear || null;
        const topItem = outfitItems.top || null;
        const bottomItem = outfitItems.bottom || null;
        const shoesItem = outfitItems.shoes || null;

        const outerwearLabel = typeof outerwearItem === 'object' ? (outerwearItem.name || outerwearItem.title || outerwearItem.label || '—') : (outerwearItem || '—');
        const topLabel = typeof topItem === 'object' ? (topItem.name || topItem.title || topItem.label || '—') : (topItem || '—');
        const bottomLabel = typeof bottomItem === 'object' ? (bottomItem.name || bottomItem.title || bottomItem.label || '—') : (bottomItem || '—');
        const shoesLabel = typeof shoesItem === 'object' ? (shoesItem.name || shoesItem.title || shoesItem.label || '—') : (shoesItem || '—');

        const outerwearImage = typeof outerwearItem === 'object' ? (outerwearItem.url || outerwearItem.image || null) : null;
        const topImage = typeof topItem === 'object' ? (topItem.url || topItem.image || null) : null;
        const bottomImage = typeof bottomItem === 'object' ? (bottomItem.url || bottomItem.image || null) : null;
        const shoesImage = typeof shoesItem === 'object' ? (shoesItem.url || shoesItem.image || null) : null;

        let itemImages = '';
        if (outerwearImage) {
          itemImages += `
            <div class="outfit-thumb">
              <img src="${outerwearImage}" alt="Outerwear image" onerror="this.src='https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=320&auto=format&fit=crop'">
              <span>Outerwear</span>
            </div>`;
        }
        if (topImage) {
          itemImages += `
            <div class="outfit-thumb">
              <img src="${topImage}" alt="Top image" onerror="this.src='https://images.unsplash.com/photo-1483985988355-763728e1935b?w=320&auto=format&fit=crop'">
              <span>Top</span>
            </div>`;
        }
        if (bottomImage) {
          itemImages += `
            <div class="outfit-thumb">
              <img src="${bottomImage}" alt="Bottom image" onerror="this.src='https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=320&auto=format&fit=crop'">
              <span>Bottom</span>
            </div>`;
        }
        if (shoesImage) {
          itemImages += `
            <div class="outfit-thumb">
              <img src="${shoesImage}" alt="Shoes image" onerror="this.src='https://images.unsplash.com/photo-1517849845537-4d257902454a?w=320&auto=format&fit=crop'">
              <span>Shoes</span>
            </div>`;
        }

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
            <h3 class="outfit-occasion">${occasionValue}</h3>
            <span class="weather-tag">🌤️ ${outfit.weather || 'Any weather'}</span>
          </div>
          <div class="outfit-images-row">
            ${itemImages}
          </div>
          <div class="outfit-items-list">
            ${itemsRows}
          </div>
          <div class="outfit-card-footer">
            <p class="outfit-note">${outfit.aiNote || 'Saved outfit'}</p>
            <div class="outfit-footer-actions">
              <span class="outfit-date">📅 ${date}</span>
              <button class="delete-btn" onclick="deleteOutfit(${outfit.id})">Delete</button>
            </div>
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
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🧥</div>
        <h3>We could not load your wardrobe yet</h3>
        <p>Please refresh the page or try saving an outfit again.</p>
      </div>
    `;
  }
}

async function deleteOutfit(outfitId) {
  if (!confirm('Delete this saved outfit?')) {
    return;
  }

  try {
    const response = await fetch(`/api/outfit/delete/${outfitId}`, {
      method: 'DELETE'
    });
    const data = await response.json();

    if (response.ok) {
      await loadWardrobe();
    } else {
      alert(data.message || 'Failed to delete outfit.');
    }
  } catch (error) {
    console.error('Error deleting outfit:', error);
    alert('Unable to delete outfit right now. Please try again later.');
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
