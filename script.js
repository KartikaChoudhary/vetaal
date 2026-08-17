// ===== API config =====
// While backend runs locally on your machine, this is the address.
// When you eventually deploy the backend somewhere online, you'll
// change this one line to that live URL — nothing else in this file
// needs to change.
const API_BASE_URL = 'http://127.0.0.1:8000';

// ===== 1. Reveal-on-scroll =====
const revealEls = document.querySelectorAll('.reveal');
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) e.target.classList.add('in');
  });
}, { threshold: 0.15 });
revealEls.forEach(el => io.observe(el));

// ===== 2. Vetaal shadow entrance =====
const vetaalShadow = document.getElementById('vetaalShadow');
const shadowIo = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) setTimeout(() => vetaalShadow.classList.add('crept'), 600);
  });
}, { threshold: 0.3 });
shadowIo.observe(document.getElementById('s0'));

// ===== 3. Gold dust particles =====
const dustField = document.getElementById('dustField');
for (let i = 0; i < 28; i++) {
  const d = document.createElement('div');
  d.className = 'dust';
  const size = 1 + Math.random() * 2.5;
  d.style.width = size + 'px';
  d.style.height = size + 'px';
  d.style.left = Math.random() * 100 + 'vw';
  d.style.bottom = '-10px';
  d.style.animationDuration = (10 + Math.random() * 14) + 's';
  d.style.animationDelay = (Math.random() * 14) + 's';
  dustField.appendChild(d);
}

// ===== 4. Diya trail (scroll progress indicator) =====
const sections = ['s0', 's1', 's2', 's3', 's4'];
const labels = ['Palace Gate', 'The Riddle', 'The Court', 'Chapters', 'Coronation'];
const diyasWrap = document.getElementById('diyas');

sections.forEach((id, i) => {
  const pct = (i / (sections.length - 1)) * 100;
  const wrap = document.createElement('div');
  wrap.className = 'diya';
  wrap.style.top = pct + '%';
  wrap.innerHTML = '<div class="diya-flame"></div><div class="diya-base"></div>';
  const label = document.createElement('div');
  label.className = 'diya-label';
  label.style.top = pct + '%';
  label.textContent = labels[i];
  diyasWrap.appendChild(wrap);
  diyasWrap.appendChild(label);
});

const diyaEls = document.querySelectorAll('.diya');

function updateTrail() {
  const scrollTop = window.scrollY;
  const docHeight = document.body.scrollHeight - window.innerHeight;
  const progress = Math.min(scrollTop / docHeight, 1);
  diyaEls.forEach((d, i) => {
    const dotPct = i / (sections.length - 1);
    if (progress >= dotPct - 0.02) d.classList.add('lit');
    else d.classList.remove('lit');
  });
}
window.addEventListener('scroll', updateTrail);
updateTrail();

// ===== 5. Hero title parallax =====
const brand = document.querySelector('.brand');
window.addEventListener('scroll', () => {
  const y = window.scrollY;
  if (y < window.innerHeight) {
    brand.style.transform = `translateY(${y * 0.15}px)`;
    brand.style.opacity = 1 - (y / window.innerHeight) * 1.1;
  }
});

// ===================================================================
// ===== 6. Live data from the backend (chapters + characters) =====
// ===================================================================
// This replaces the hardcoded chapter/character cards in the HTML
// with real data fetched from your FastAPI + Postgres backend.

async function loadChapters() {
  const rail = document.querySelector('.chapter-rail');
  if (!rail) return;

  try {
    const res = await fetch(`${API_BASE_URL}/api/chapters`);
    if (!res.ok) throw new Error(`Server responded with ${res.status}`);
    const chapters = await res.json();
    renderChapters(chapters, rail);
  } catch (err) {
    // Server not running, CORS issue, or network error land here.
    console.error('Could not load chapters from API:', err);
    rail.innerHTML = '<p style="color:var(--ivory-dim);font-family:JetBrains Mono,monospace;font-size:12px;">Could not load chapters. Is the backend running?</p>';
  }
}

function renderChapters(chapters, rail) {
  const tierLabel = { free: 'Free', fast_pass: 'Fast Pass', new: 'New' };
  // cycles through the same cover gradients the original hardcoded cards used
  const gradients = [
    'linear-gradient(160deg,#1a130a,#100b06 70%)',
    'linear-gradient(160deg,#3a1418,#100b06 70%)',
    'linear-gradient(160deg,#2a2008,#100b06 70%)',
    'linear-gradient(160deg,#1a130a,#3a1418 130%)',
    'linear-gradient(160deg,#3a1418,#1a130a 70%)',
  ];

  rail.innerHTML = chapters.map((ch, i) => `
    <div class="chapter-card" data-chapter-id="${ch.id}">
      <div class="chapter-cover" style="background:${gradients[i % gradients.length]};">
        <div class="chapter-num">${escapeHTML(ch.riddle_label)}</div>
        <div class="chapter-cover-title">${escapeHTML(ch.title)}</div>
      </div>
      <div class="chapter-info">
        <span>${tierLabel[ch.access_tier] || escapeHTML(ch.access_tier)}</span>
        <span class="chapter-arrow">&rarr;</span>
      </div>
    </div>
  `).join('');
}

async function loadCharacters() {
  const grid = document.querySelector('.char-grid');
  if (!grid) return;

  try {
    const res = await fetch(`${API_BASE_URL}/api/characters`);
    if (!res.ok) throw new Error(`Server responded with ${res.status}`);
    const characters = await res.json();
    renderCharacters(characters, grid);
  } catch (err) {
    console.error('Could not load characters from API:', err);
    grid.innerHTML = '<p style="color:var(--ivory-dim);font-family:JetBrains Mono,monospace;font-size:12px;">Could not load characters. Is the backend running?</p>';
  }
}

function renderCharacters(characters, grid) {
  grid.innerHTML = characters.map((c, i) => `
    <div class="char-card reveal in d${(i % 4) + 1}">
      <div class="char-portrait">
        <svg class="jewel-icon" viewBox="0 0 70 70">
          <path d="M35 6 44 26 65 30 49 45 53 66 35 55 17 66 21 45 5 30 26 26Z" fill="none" stroke="#e8c468" stroke-width="2"/>
          <circle cx="35" cy="35" r="6" fill="#a3182b"/>
        </svg>
      </div>
      <div class="char-body">
        <div class="char-code">${escapeHTML(c.code)}</div>
        <div class="char-name">${escapeHTML(c.name)}</div>
        <div class="char-role">${escapeHTML(c.name_devanagari || c.role || '')}</div>
        <p class="char-desc">${escapeHTML(c.description)}</p>
      </div>
    </div>
  `).join('');
}

// Basic safety: prevents any weird characters coming from the database
// from being interpreted as HTML tags when we insert them into the page.
function escapeHTML(str) {
  const div = document.createElement('div');
  div.textContent = str ?? '';
  return div.innerHTML;
}

// Kick off both fetches once the page is ready.
document.addEventListener('DOMContentLoaded', () => {
  loadChapters();
  loadCharacters();
});

// ===================================================================
// ===== 7. Auth (login / register) =====
// ===================================================================
// The JWT token is stored in localStorage so the user stays logged in
// across page reloads. (Note: this is fine here because this is a real
// deployed site running in an actual browser — not a Claude.ai artifact
// sandbox, where localStorage isn't available.)

const TOKEN_KEY = 'vetaal_token';
const EMAIL_KEY = 'vetaal_email';

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function isLoggedIn() {
  return !!getToken();
}

function logout() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(EMAIL_KEY);
  renderAccountPill();
  renderRiddleBox(); // refresh quiz area to show the "login to answer" state
}

// ----- Modal open/close + login vs register toggle -----

let authMode = 'login'; // or 'register'

function openAuthModal(mode = 'login') {
  authMode = mode;
  updateAuthModalText();
  document.getElementById('authBackdrop').classList.add('open');
  document.getElementById('authError').classList.remove('show');
}

function closeAuthModal() {
  document.getElementById('authBackdrop').classList.remove('open');
}

function updateAuthModalText() {
  const isLogin = authMode === 'login';
  document.getElementById('authTitle').textContent = isLogin ? 'Enter the Court' : 'Join the Court';
  document.getElementById('authSub').textContent = isLogin ? 'Login to answer the Vetaal' : 'Register to begin answering';
  document.getElementById('authSubmit').textContent = isLogin ? 'Login' : 'Register';
  document.getElementById('authSwitchText').textContent = isLogin ? 'New to the court?' : 'Already have an account?';
  document.getElementById('authSwitchLink').textContent = isLogin ? 'Register instead' : 'Login instead';
}

function showAuthError(msg) {
  const el = document.getElementById('authError');
  el.textContent = msg;
  el.classList.add('show');
}

async function handleAuthSubmit() {
  const email = document.getElementById('authEmail').value.trim();
  const password = document.getElementById('authPassword').value;
  const submitBtn = document.getElementById('authSubmit');

  if (!email || !password) {
    showAuthError('Enter both email and password.');
    return;
  }

  submitBtn.disabled = true;
  document.getElementById('authError').classList.remove('show');

  try {
    if (authMode === 'register') {
      const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Registration failed');
      }
      // auto-login right after registering
      await loginRequest(email, password);
    } else {
      await loginRequest(email, password);
    }
    closeAuthModal();
    renderAccountPill();
    renderRiddleBox();
  } catch (err) {
    showAuthError(err.message || 'Something went wrong.');
  } finally {
    submitBtn.disabled = false;
  }
}

async function loginRequest(email, password) {
  const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Login failed');
  }
  const data = await res.json();
  localStorage.setItem(TOKEN_KEY, data.access_token);
  localStorage.setItem(EMAIL_KEY, email);
}

function renderAccountPill() {
  const pill = document.getElementById('accountPill');
  if (!pill) return;

  if (isLoggedIn()) {
    const email = localStorage.getItem(EMAIL_KEY) || 'account';
    pill.innerHTML = `<span>${escapeHTML(email)}</span><button id="logoutBtn">Logout</button>`;
    document.getElementById('logoutBtn').addEventListener('click', logout);
  } else {
    pill.innerHTML = `<button id="loginBtn">Login</button>`;
    document.getElementById('loginBtn').addEventListener('click', () => openAuthModal('login'));
  }
}

// ===================================================================
// ===== 8. Riddle quiz =====
// ===================================================================

let currentRiddle = null; // { id, chapter_id, question, hint }

async function renderRiddleBox() {
  const container = document.getElementById('riddleContainer');
  if (!container) return;

  if (!isLoggedIn()) {
    container.innerHTML = `
      <p class="riddle-locked">Only those who enter the court may answer.
        <a id="loginToAnswerLink">Login to answer the Vetaal</a>
      </p>`;
    document.getElementById('loginToAnswerLink').addEventListener('click', () => openAuthModal('login'));
    return;
  }

  if (!currentRiddle) {
    try {
      // fetch chapter 1's riddle by default (adjust the number if you want a different chapter's riddle featured)
      const chaptersRes = await fetch(`${API_BASE_URL}/api/chapters`);
      const chapters = await chaptersRes.json();
      const firstChapter = chapters.find(c => c.number === 1);
      if (!firstChapter) throw new Error('No chapter found');

      const riddleRes = await fetch(`${API_BASE_URL}/api/chapters/${firstChapter.id}/riddle`);
      if (!riddleRes.ok) throw new Error('No riddle available yet');
      currentRiddle = await riddleRes.json();
    } catch (err) {
      container.innerHTML = `<p class="riddle-locked">The Vetaal has no question tonight.</p>`;
      return;
    }
  }

  container.innerHTML = `
    <div class="riddle-box">
      <div class="riddle-question">${escapeHTML(currentRiddle.question)}</div>
      <div class="riddle-input-row">
        <input type="text" id="riddleAnswerInput" placeholder="Your answer..." />
        <button class="riddle-submit" id="riddleSubmitBtn">Answer</button>
      </div>
      ${currentRiddle.hint ? `<span class="riddle-hint" id="riddleHintToggle">Need a hint?</span>
      <div id="riddleHintText" style="display:none;margin-top:8px;font-size:12px;color:var(--ivory-dim);">${escapeHTML(currentRiddle.hint)}</div>` : ''}
      <div class="riddle-result" id="riddleResult"></div>
    </div>
  `;

  document.getElementById('riddleSubmitBtn').addEventListener('click', submitRiddleAnswer);
  document.getElementById('riddleAnswerInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') submitRiddleAnswer();
  });
  const hintToggle = document.getElementById('riddleHintToggle');
  if (hintToggle) {
    hintToggle.addEventListener('click', () => {
      document.getElementById('riddleHintText').style.display = 'block';
    });
  }
}

async function submitRiddleAnswer() {
  const input = document.getElementById('riddleAnswerInput');
  const resultBox = document.getElementById('riddleResult');
  const answer = input.value.trim();
  if (!answer || !currentRiddle) return;

  try {
    const res = await fetch(`${API_BASE_URL}/api/riddles/${currentRiddle.id}/answer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`,
      },
      body: JSON.stringify({ answer }),
    });

    if (res.status === 401) {
      // token expired or invalid — force re-login
      logout();
      openAuthModal('login');
      return;
    }

    const data = await res.json();
    resultBox.textContent = data.message;
    resultBox.className = `riddle-result show ${data.is_correct ? 'correct' : 'wrong'}`;
  } catch (err) {
    resultBox.textContent = 'Could not reach the Vetaal. Try again.';
    resultBox.className = 'riddle-result show wrong';
  }
}

// ===== Wire up modal buttons + initial render =====
document.addEventListener('DOMContentLoaded', () => {
  renderAccountPill();
  renderRiddleBox();

  document.getElementById('authClose').addEventListener('click', closeAuthModal);
  document.getElementById('authSubmit').addEventListener('click', handleAuthSubmit);
  document.getElementById('authSwitchLink').addEventListener('click', () => {
    openAuthModal(authMode === 'login' ? 'register' : 'login');
  });
  document.getElementById('authBackdrop').addEventListener('click', (e) => {
    if (e.target.id === 'authBackdrop') closeAuthModal();
  });
});
