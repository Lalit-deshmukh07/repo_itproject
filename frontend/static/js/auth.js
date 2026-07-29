const showError = (element, message) => {
  if (!element) return;
  element.textContent = message;
  element.style.display = 'block';
};

const clearError = (element) => {
  if (!element) return;
  element.textContent = '';
  element.style.display = 'none';
};

// Login form
const loginForm = document.getElementById('loginForm');
if (loginForm) {
  const loginError = document.getElementById('loginError');
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearError(loginError);

    const email = loginForm.email.value.trim();
    const password = loginForm.password.value;

    if (!email || !password) {
      showError(loginError, 'Please enter both email and password.');
      return;
    }

    const data = { email, password };
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      credentials: 'same-origin'
    });
    const result = await res.json();
    if (res.ok) {
      if (result.user) {
        localStorage.setItem('user', JSON.stringify(result.user));
      }
      window.location.href = '/profile';
    } else {
      showError(loginError, result.message || 'Login failed');
    }
  });
}

// Register form
const registerForm = document.getElementById('registerForm');
if (registerForm) {
  const registerError = document.getElementById('registerError');
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearError(registerError);

    const firstName = registerForm.firstName.value.trim();
    const lastName = registerForm.lastName.value.trim();
    const email = registerForm.email.value.trim();
    const password = registerForm.password.value;
    const confirmPassword = registerForm.confirmPassword.value;
    const consentChecked = registerForm.consent.checked;

    if (!firstName || !lastName) {
      showError(registerError, 'Please enter your first and last name.');
      return;
    }
    if (!email || !email.includes('@') || email.length < 5) {
      showError(registerError, 'Please enter a valid email address.');
      return;
    }
    if (password.length < 8) {
      showError(registerError, 'Password must be at least 8 characters long.');
      return;
    }
    if (password !== confirmPassword) {
      showError(registerError, 'Passwords do not match.');
      return;
    }
    if (!consentChecked) {
      showError(registerError, 'You must accept the terms and privacy policy.');
      return;
    }

    const data = {
      firstName,
      lastName,
      email,
      password,
      consent: consentChecked
    };
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      credentials: 'same-origin'
    });
    const result = await res.json();
    if (res.ok) {
      if (result.user) {
        localStorage.setItem('user', JSON.stringify(result.user));
      }
      // New users go to profile setup first
      window.location.href = '/profile-setup';
    } else {
      showError(registerError, result.message || 'Registration failed');
    }
  });
}

// Reset form
const resetForm = document.getElementById('resetForm');
if (resetForm) {
  const resetError = document.getElementById('resetError');
  resetForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearError(resetError);

    const email = resetForm.email.value.trim();
    if (!email || !email.includes('@')) {
      showError(resetError, 'Please enter a valid email address.');
      return;
    }

    const data = { email };
    const res = await fetch('/api/auth/reset-request', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await res.json();
    if (res.ok) {
      alert('Reset link sent! Check your email.');
    } else {
      showError(resetError, result.message || 'Something went wrong.');
    }
  });
}

function updateStyleOptionState() {
  document.querySelectorAll('.style-option input[type="checkbox"]').forEach((checkbox) => {
    const option = checkbox.closest('.style-option');
    if (option) {
      option.classList.toggle('checked', checkbox.checked);
    }
  });
}

function addExclusionTag(value) {
  const exclusionInput = document.getElementById('exclusions');
  const tagContainer = document.getElementById('exclusion-tags');
  if (!tagContainer || !value) return;

  const tag = document.createElement('div');
  tag.className = 'tag';
  tag.innerHTML = `${value}<button type="button" onclick="this.parentElement.remove()">×</button>`;
  tagContainer.appendChild(tag);
  if (exclusionInput) exclusionInput.value = '';
}

async function loadExistingProfilePreferences() {
  try {
    const response = await fetch('/api/user/preferences');
    if (!response.ok) return;

    const data = await response.json();
    const prefs = data.preferences || {};

    const genderField = document.getElementById('gender');
    if (genderField && prefs.gender) {
      genderField.value = prefs.gender;
    }

    const topSizeField = document.getElementById('topSize');
    if (topSizeField && prefs.topSize) {
      topSizeField.value = prefs.topSize;
    }

    const bottomSizeField = document.getElementById('bottomSize');
    if (bottomSizeField && prefs.bottomSize) {
      bottomSizeField.value = prefs.bottomSize;
    }

    document.querySelectorAll('input[name="style"]').forEach((checkbox) => {
      checkbox.checked = Array.isArray(prefs.styles) && prefs.styles.includes(checkbox.value);
    });
    updateStyleOptionState();

    const tagContainer = document.getElementById('exclusion-tags');
    if (tagContainer && Array.isArray(prefs.exclusions)) {
      tagContainer.innerHTML = '';
      prefs.exclusions.forEach((item) => addExclusionTag(item));
    }
  } catch (error) {
    console.error('Error loading profile preferences:', error);
  }
}

// Exclusion tags (profile setup)
const exclusionInput = document.getElementById('exclusions');
const tagContainer = document.getElementById('exclusion-tags');
if (exclusionInput) {
  exclusionInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addExclusionTag(exclusionInput.value.trim());
    }
  });
}

document.querySelectorAll('.style-option input[type="checkbox"]').forEach((checkbox) => {
  checkbox.addEventListener('change', updateStyleOptionState);
});

if (document.getElementById('profileForm')) {
  loadExistingProfilePreferences();
}

// Profile setup form
const profileForm = document.getElementById('profileForm');
if (profileForm) {
  profileForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const gender = document.getElementById('gender').value;
    const topSize = document.getElementById('topSize').value;
    const bottomSize = document.getElementById('bottomSize').value;
    
    // Get selected styles
    const styleCheckboxes = document.querySelectorAll('input[name="style"]:checked');
    const styles = Array.from(styleCheckboxes).map(cb => cb.value);
    
    // Get exclusions from tags
    const exclusionTags = document.querySelectorAll('#exclusion-tags .tag');
    const exclusions = Array.from(exclusionTags).map(tag => tag.textContent.replace('×', '').trim()).filter(e => e);

    if (!gender || !topSize || !bottomSize || styles.length === 0) {
      alert('Please fill in all fields and select at least one style preference.');
      return;
    }

    const data = {
      gender,
      topSize,
      bottomSize,
      styles,
      exclusions
    };

    try {
      const res = await fetch('/api/user/preferences', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      
      const result = await res.json();
      
      if (res.ok) {
        alert('✓ Profile setup saved successfully!');
        window.location.href = '/profile';
      } else {
        alert('Error: ' + (result.message || 'Failed to save profile'));
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to save profile. Please try again.');
    }
  });
}