const pathParts = window.location.pathname.split('/');
const username = decodeURIComponent(pathParts[pathParts.length - 1]);
const contentEl = document.getElementById('content');
document.getElementById('author-name').textContent = `u/${username}`;
document.getElementById('crumb-name').textContent = `u/${username}`;

load();

async function load() {
  contentEl.innerHTML = '<div class="loading"><span class="spinner"></span>Loading...</div>';
  try {
    const res = await fetch(`/api/authors/${username}`);
    if (res.status === 404) {
      // No comments yet — offer to fetch
      contentEl.innerHTML = `
        <div class="empty-state">
          <div class="icon">○</div>
          <div class="title">No data for u/${username} yet</div>
          <div class="hint" style="margin-top: 0.8em;">
            <button id="fetch-btn">Fetch this user's history from Reddit</button>
          </div>
        </div>`;
      document.getElementById('fetch-btn').addEventListener('click', fetchAuthor);
      return;
    }
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || res.statusText);
    }
    const data = await res.json();
    render(data);
  } catch (e) {
    contentEl.innerHTML = `<div class="empty-state"><div class="icon">⚠</div><div class="title">${escapeHtml(e.message)}</div></div>`;
  }
}

async function fetchAuthor() {
  const btn = document.getElementById('fetch-btn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span>Fetching from Reddit...';
  try {
    const res = await fetch(`/api/authors/${username}/fetch`, { method: 'POST' });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || res.statusText);
    }
    const data = await res.json();
    // After fetch, reload the page data
    load();
  } catch (e) {
    btn.disabled = false;
    btn.textContent = 'Fetch failed: ' + e.message;
  }
}

function render(data) {
  const chips = data.subreddits.map(s =>
    `<a href="/subreddit/${s}" class="chip">r/${s}</a>`
  ).join('');

  const lastFetched = data.last_fetched_at
    ? `<div class="panel-subtitle">Last fetched from Reddit: ${data.last_fetched_at.replace('T', ' ').substring(0, 16)} SGT</div>`
    : '';

  contentEl.innerHTML = `
    <section class="stats-grid">
      <div class="stat-card"><div class="stat-label">Total comments</div><div class="stat-value">${data.total_comments.toLocaleString()}</div></div>
      <div class="stat-card"><div class="stat-label">Active subreddits</div><div class="stat-value">${data.subreddits.length}</div></div>
    </section>
    <div class="panel">
      <div class="panel-header">
        <div>
          <h2 class="panel-title">Active in subreddits</h2>
        </div>
        <button id="refresh-btn">Refresh from Reddit</button>
        <p class="hint">Adds up to 100 recent comments from any subreddit on Reddit</p>
      </div>
      <div class="panel-body">${chips}</div>
    </div>
    <div class="panel">
      <div class="panel-header">
        <div>
          <h2 class="panel-title">Comment history</h2>
          ${lastFetched}
        </div>
      </div>
      <div class="panel-body">
        <div id="comments-list"></div>
      </div>
    </div>
  `;

  document.getElementById('refresh-btn').addEventListener('click', refreshAuthor);

  document.getElementById('comments-list').innerHTML = data.comments.map(c => `
    <div class="author-comment ${c.is_deleted ? 'deleted' : ''}">
      <div class="context">
        On <a href="/submission/${c.submission_id}">${escapeHtml(c.submission_title)}</a>
        in <a href="/subreddit/${c.subreddit}">r/${c.subreddit}</a>
        · ${c.score} points · ${c.created_sgt.replace('T', ' ').substring(0, 16)} SGT
      </div>
      <div class="body">${escapeHtml(c.body || '')}</div>
    </div>
  `).join('');
}

async function refreshAuthor() {
  const btn = document.getElementById('refresh-btn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span>Fetching...';
  try {
    const res = await fetch(`/api/authors/${username}/fetch`, { method: 'POST' });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || res.statusText);
    }
    load();
  } catch (e) {
    btn.disabled = false;
    btn.textContent = 'Error: ' + e.message;
  }
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}