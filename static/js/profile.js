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

// Load recommendations based on style
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
          <h3>${rec.title}</h3>
          <p>${rec.description}</p>
        `;
        container.appendChild(card);
      });
    } else {
      container.innerHTML = '<p>Complete your profile to get personalized recommendations!</p>';
    }
  } catch (error) {
    console.error('Error loading recommendations:', error);
    const container = document.getElementById('recommendationsContainer');
    container.innerHTML = '<p>Could not load recommendations</p>';
  }
}

// Load saved outfits (wardrobe)
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
        
        const date = new Date(outfit.createdAt).toLocaleDateString();
        
        card.innerHTML = `
          <div class="outfit-preview">
            <div class="outfit-item">${outfit.items.top ? 'Top' : 'No Top'}</div>
            <div class="outfit-item">${outfit.items.bottom ? 'Bottom' : 'No Bottom'}</div>
            <div class="outfit-item">${outfit.items.shoes ? 'Shoes' : 'No Shoes'}</div>
            <div class="outfit-item">${outfit.weather || 'Any'}</div>
          </div>
          <div class="outfit-details">
            <h3>${outfit.occasion}</h3>
            <p>${outfit.aiNote || 'Outfit saved'}</p>
            <p class="outfit-date">Saved on ${date}</p>
          </div>
        `;
        container.appendChild(card);
      });
    } else {
      container.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
          <p>You haven't saved any outfits yet!</p>
          <a href="/">Generate Your First Outfit</a>
        </div>
      `;
    }
  } catch (error) {
    console.error('Error loading wardrobe:', error);
    const container = document.getElementById('wardrobeContainer');
    container.innerHTML = '<p>Could not load wardrobe</p>';
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
