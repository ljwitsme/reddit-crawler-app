const pathParts = window.location.pathname.split('/');
const username = decodeURIComponent(pathParts[pathParts.length - 1]);
const contentEl = document.getElementById('content');
document.getElementById('author-name').textContent = `u/${username}`;
document.getElementById('crumb-name').textContent = `u/${username}`;

load();

async function load() {
  try {
    const res = await fetch(`/api/authors/${username}`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || res.statusText);
    }
    const data = await res.json();
    render(data);
  } catch (e) {
    contentEl.innerHTML = `<div class="empty-state"><div class="icon">⚠</div><div class="title">${escapeHtml(e.message)}</div><div class="hint">This author may not have been crawled yet.</div></div>`;
  }
}

function render(data) {
  const chips = data.subreddits.map(s =>
    `<a href="/subreddit/${s}" class="chip">r/${s}</a>`
  ).join('');

  contentEl.innerHTML = `
    <section class="stats-grid">
      <div class="stat-card"><div class="stat-label">Total comments</div><div class="stat-value">${data.total_comments.toLocaleString()}</div></div>
      <div class="stat-card"><div class="stat-label">Active subreddits</div><div class="stat-value">${data.subreddits.length}</div></div>
    </section>
    <div class="panel">
      <div class="panel-header">
        <div><h2 class="panel-title">Active in subreddits</h2></div>
      </div>
      <div class="panel-body">${chips}</div>
    </div>
    <div class="panel">
      <div class="panel-header">
        <div>
          <h2 class="panel-title">Comment history</h2>
          <div class="panel-subtitle">All comments by this author, newest first</div>
        </div>
      </div>
      <div class="panel-body">
        <div id="comments-list"></div>
      </div>
    </div>
  `;

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

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}