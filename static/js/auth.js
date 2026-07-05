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
      body: JSON.stringify(data)
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
      body: JSON.stringify(data)
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

// Exclusion tags (profile setup)
const exclusionInput = document.getElementById('exclusions');
const tagContainer = document.getElementById('exclusion-tags');
if (exclusionInput) {
  exclusionInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      const val = exclusionInput.value.trim();
      if (!val) return;
      const tag = document.createElement('div');
      tag.className = 'tag';
      tag.innerHTML = `${val}<button onclick="this.parentElement.remove()">×</button>`;
      tagContainer.appendChild(tag);
      exclusionInput.value = '';
    }
  });
}