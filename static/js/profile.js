// Populate profile page from localStorage
const userJson = localStorage.getItem('user');
if (!userJson) {
  // No user found, redirect to login
  window.location.href = '/login';
} else {
  try {
    const user = JSON.parse(userJson);
    const nameEl = document.getElementById('profile-name');
    const emailEl = document.getElementById('profile-email');
    const welcomeEl = document.getElementById('welcome');
    if (nameEl) nameEl.textContent = `${user.firstName || ''} ${user.lastName || ''}`.trim();
    if (emailEl) emailEl.textContent = user.email || '';
    if (welcomeEl) welcomeEl.textContent = `Welcome back, ${user.firstName || ''}!`;
  } catch (e) {
    localStorage.removeItem('user');
    window.location.href = '/login';
  }
}

// Logout
const logoutBtn = document.getElementById('logoutBtn');
if (logoutBtn) {
  logoutBtn.addEventListener('click', () => {
    localStorage.removeItem('user');
    window.location.href = '/login';
  });
}
