const form = document.getElementById('loginForm');
const errorEl = document.getElementById('error');
const btn = document.getElementById('loginBtn');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  errorEl.hidden = true;

  const email = form.email.value.trim();
  const password = form.password.value;

  // simple validation
  if (!email || !password) {
    return showError('Please enter email and password.');
  }
  if (password.length < 8) {
    return showError('Password must be at least 8 characters.');
  }

  btn.disabled = true;

  // TEMPORARY: fake successful login
  await new Promise(r => setTimeout(r, 600));
  alert('It Works!');
  btn.disabled = false;
});

function showError(msg) {
  errorEl.textContent = msg;
  errorEl.hidden = false;
}
