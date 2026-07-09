// Login form
const loginForm = document.getElementById('loginForm');
if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
      email: loginForm.email.value,
      password: loginForm.password.value
    };
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await res.json();
    if (res.ok) window.location.href = '/';
    else alert(result.message || 'Login failed');
  });
}

// Register form
const registerForm = document.getElementById('registerForm');
if (registerForm) {
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (registerForm.password.value !== registerForm.confirmPassword.value) {
      alert('Passwords do not match'); return;
    }
    const data = {
      firstName: registerForm.firstName.value,
      lastName: registerForm.lastName.value,
      email: registerForm.email.value,
      password: registerForm.password.value
    };
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await res.json();
    if (res.ok) window.location.href = '/login';
    else alert(result.message || 'Registration failed');
  });
}

// Reset form
const resetForm = document.getElementById('resetForm');
if (resetForm) {
  resetForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = { email: resetForm.email.value };
    const res = await fetch('/api/auth/reset-request', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (res.ok) alert('Reset link sent! Check your email.');
    else alert('Something went wrong.');
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