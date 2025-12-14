const form = document.getElementById('loginForm');
const errorEl = document.getElementById('error');
const btn = document.getElementById('loginBtn');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  errorEl.hidden = true;

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  if (!email || !password) {
    return showError('Please enter email and password.');
  }

  if (password.length < 8) {
    return showError('Password must be at least 8 characters.');
  }

  btn.disabled = true;

  // simulate server delay
  await new Promise(r => setTimeout(r, 600));

  // Save fake user data
  localStorage.setItem('user', JSON.stringify({
    name: "Avery Parker",
    major: "Computer Science",
    birthday: "08/21/2003",
    workplace: "Student Worker at IT Helpdesk",
    bio: "I love building apps, studying CS, and hanging out on campus.",
    clubs: ["Programming Club", "Rodeo Club", "Game Dev Society"],
    friends: [
      "img/friend1.jpg",
      "img/friend2.jpg",
      "img/friend3.jpg"
    ],
    profilePic: "img/avery.jpg"
  }));

  window.location.href = "home.html";
  btn.disabled = false;
});

function showError(msg) {
  errorEl.textContent = msg;
  errorEl.hidden = false;
}
