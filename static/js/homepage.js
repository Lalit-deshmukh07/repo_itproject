// INTERACTIVE OUTFIT RECOMMENDATION DEMO
// Displays uploaded clothing images as a suggested outfit combination by category.

const occasion = document.getElementById("occasion");
const generateBtn = document.getElementById("generateBtn");
const recommendationSection = document.getElementById("recommendations");
const selectedOccasion = document.getElementById("selectedOccasion");

const topImage = document.getElementById("topImage");
const bottomImage = document.getElementById("bottomImage");
const shoesImage = document.getElementById("shoesImage");

// Track uploaded files by category
let categoryFiles = {
  tops: [],
  bottoms: [],
  dresses: [],
  shoes: []
};

let userAuthenticated = false;

// Check authentication status on page load
document.addEventListener('DOMContentLoaded', function() {
  checkAuthStatus();
  setupCategoryUploads();
});

// Check if user is logged in
async function checkAuthStatus() {
  try {
    const response = await fetch('/api/auth/status');
    const data = await response.json();
    userAuthenticated = data.authenticated;
    updateSaveButtonState();
  } catch (error) {
    console.log('Auth check failed:', error);
    userAuthenticated = false;
  }
}

// Update save button state
function updateSaveButtonState() {
  const saveBtn = document.querySelector('.result-buttons button:first-child');
  if (saveBtn) {
    if (userAuthenticated) {
      saveBtn.disabled = false;
      saveBtn.style.opacity = '1';
      saveBtn.title = 'Click to save this outfit';
    } else {
      saveBtn.disabled = true;
      saveBtn.style.opacity = '0.5';
      saveBtn.title = 'Please login to save outfits';
    }
  }
}

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

// Handle file uploads for each category
function handleCategoryUpload(category, files) {
  categoryFiles[category] = Array.from(files).map(file => URL.createObjectURL(file));
  
  // Display uploaded files
  const listContainer = document.getElementById(`${category}List`);
  listContainer.innerHTML = '';
  
  Array.from(files).forEach(file => {
    const item = document.createElement('div');
    item.className = 'file-item';
    item.textContent = `✓ ${file.name}`;
    listContainer.appendChild(item);
  });
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

// Generate outfit combination
function generateOutfitCombination() {
  const validation = validateCategories();
  
  if (!validation.valid) {
    const missingText = validation.missing.join(', ');
    alert(`❌ Missing items: ${missingText}\n\nPlease upload at least one item from each required category.`);
    
    recommendationSection.hidden = false;
    topImage.src = '';
    bottomImage.src = '';
    shoesImage.src = '';
    
    document.getElementById("topImage").parentElement.innerHTML = `<div style="width:100%; height:100%; display:flex; align-items:center; justify-content:center; color:#999; text-align:center;"><p>No Top/Dress Selected</p></div>`;
    document.getElementById("bottomImage").parentElement.innerHTML = `<div style="width:100%; height:100%; display:flex; align-items:center; justify-content:center; color:#999; text-align:center;"><p>No Bottoms Selected</p></div>`;
    document.getElementById("shoesImage").parentElement.innerHTML = `<div style="width:100%; height:100%; display:flex; align-items:center; justify-content:center; color:#999; text-align:center;"><p>No Shoes Selected</p></div>`;
    
    recommendationSection.scrollIntoView({ behavior: "smooth" });
    return;
  }

  // Select random items from each category
  const topOrDress = categoryFiles.dresses.length > 0 && Math.random() > 0.5 
    ? categoryFiles.dresses[Math.floor(Math.random() * categoryFiles.dresses.length)]
    : categoryFiles.tops[Math.floor(Math.random() * categoryFiles.tops.length)];
    
  const bottom = categoryFiles.bottoms[Math.floor(Math.random() * categoryFiles.bottoms.length)];
  const shoe = categoryFiles.shoes[Math.floor(Math.random() * categoryFiles.shoes.length)];

  // Set images
  topImage.src = topOrDress;
  bottomImage.src = bottom;
  shoesImage.src = shoe;
  
  // Restore proper image display
  topImage.parentElement.innerHTML = `<img id="topImage" src="${topOrDress}" alt="Top/Dress" style="width:100%; height:100%; object-fit:cover; border-radius:15px;">`;
  bottomImage.parentElement.innerHTML = `<img id="bottomImage" src="${bottom}" alt="Bottom" style="width:100%; height:100%; object-fit:cover; border-radius:15px;">`;
  shoesImage.parentElement.innerHTML = `<img id="shoesImage" src="${shoe}" alt="Shoes" style="width:100%; height:100%; object-fit:cover; border-radius:15px;">`;

  selectedOccasion.textContent = occasion.value;
  recommendationSection.hidden = false;
  recommendationSection.scrollIntoView({ behavior: "smooth" });

  updateSaveButtonState();
}

if (generateBtn) {
  generateBtn.addEventListener("click", function () {
    if (occasion.value === "") {
      alert("Please select an occasion.");
      return;
    }

    generateOutfitCombination();
  });
}

// Handle Save Outfit button
document.addEventListener('DOMContentLoaded', function() {
  const saveBtn = document.querySelector('.result-buttons button:first-child');
  if (saveBtn) {
    saveBtn.addEventListener('click', async function() {
      if (!userAuthenticated) {
        alert('Please login to save outfits.');
        window.location.href = '/login';
        return;
      }

      const topImageSrc = document.getElementById('topImage')?.src || '';
      const bottomImageSrc = document.getElementById('bottomImage')?.src || '';
      const shoesImageSrc = document.getElementById('shoesImage')?.src || '';

      const outfitData = {
        occasion: selectedOccasion.textContent,
        items: {
          top: topImageSrc ? 'Top/Dress item' : '',
          bottom: bottomImageSrc ? 'Bottom item' : '',
          shoes: shoesImageSrc ? 'Shoes' : ''
        },
        weather: 'Cloudy, 18°C',
        aiNote: 'A comfortable casual combination with light layers suitable for the weather.'
      };

      try {
        const response = await fetch('/api/outfit/save', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(outfitData)
        });

        const data = await response.json();

        if (response.ok) {
          alert('✓ Outfit saved successfully!');
          saveBtn.textContent = 'Outfit Saved!';
          setTimeout(() => {
            saveBtn.textContent = 'Save Outfit';
          }, 2000);
        } else {
          alert('Error: ' + data.message);
        }
      } catch (error) {
        console.error('Error saving outfit:', error);
        alert('Failed to save outfit. Please try again.');
      }
    });
  }
});

// Handle Generate Another button
document.addEventListener('DOMContentLoaded', function() {
  const generateAnotherBtn = document.querySelector('.result-buttons .secondary-btn');
  if (generateAnotherBtn) {
    generateAnotherBtn.addEventListener('click', function() {
      const validation = validateCategories();
      if (validation.valid && occasion.value !== "") {
        generateOutfitCombination();
      } else {
        alert('Please upload items and select an occasion first.');
      }
    });
  }
});

const outfitButtons = document.querySelectorAll('.outfit-card button');
outfitButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const card = button.closest('.outfit-card');
    const heading = card?.querySelector('h3');
    const title = heading?.textContent || 'Selected outfit';

    if (selectedOccasion) {
      selectedOccasion.textContent = title;
    }

    if (recommendationSection) {
      recommendationSection.hidden = false;
      recommendationSection.scrollIntoView({ behavior: 'smooth' });
    }
  });
});