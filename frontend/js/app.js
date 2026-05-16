const urlInput = document.getElementById('url');
const crawlBtn = document.getElementById('crawl-btn');
const statusEl = document.getElementById('status');

const subInput = document.getElementById('subreddit-name');
const subBtn = document.getElementById('crawl-sub-btn');
const subStatusEl = document.getElementById('sub-status');

const listEl = document.getElementById('submissions-list');
const statsEl = document.getElementById('stats');

crawlBtn.addEventListener('click', crawl);
urlInput.addEventListener('keydown', e => { if (e.key === 'Enter') crawl(); });

subBtn.addEventListener('click', crawlSubreddit);
subInput.addEventListener('keydown', e => { if (e.key === 'Enter') crawlSubreddit(); });

loadStats();
loadSubmissions();

async function crawl() {
  const url = urlInput.value.trim();
  if (!url) return;
  setStatus(statusEl, '<span class="spinner"></span>Crawling...');
  crawlBtn.disabled = true;
  try {
    const res = await fetch('/api/crawl', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || res.statusText);
    }
    const data = await res.json();
    setStatus(statusEl, `✓ Done. <a href="/submission/${data.id}">View submission →</a>`, 'success');
    loadStats();
    loadSubmissions();
  } catch (e) {
    setStatus(statusEl, '✗ ' + e.message, 'error');
  } finally {
    crawlBtn.disabled = false;
  }
}

async function crawlSubreddit() {
  const subreddit = subInput.value.trim();
  if (!subreddit) return;
  setStatus(subStatusEl, '<span class="spinner"></span>Crawling 50 posts...');
  subBtn.disabled = true;
  try {
    const res = await fetch('/api/crawl-subreddit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ subreddit, limit: 50 }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || res.statusText);
    }
    const data = await res.json();
    setStatus(subStatusEl, `✓ Done. Crawled ${data.length} posts from r/${subreddit}. <a href="/subreddit/${subreddit}">View →</a>`, 'success');
    loadStats();
    loadSubmissions();
  } catch (e) {
    setStatus(subStatusEl, '✗ ' + e.message, 'error');
  } finally {
    subBtn.disabled = false;
  }
}

function setStatus(el, html, type = '') {
  el.className = 'status-msg' + (type ? ' ' + type : '');
  el.innerHTML = html;
}

async function loadStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();
    statsEl.innerHTML = `
      <div class="stat-card"><div class="stat-label">Submissions</div><div class="stat-value">${data.submissions.toLocaleString()}</div></div>
      <div class="stat-card"><div class="stat-label">Comments</div><div class="stat-value">${data.comments.toLocaleString()}</div></div>
      <div class="stat-card"><div class="stat-label">Subreddits</div><div class="stat-value">${data.subreddits.toLocaleString()}</div></div>
      <div class="stat-card"><div class="stat-label">Unique authors</div><div class="stat-value">${data.unique_authors.toLocaleString()}</div></div>
    `;
  } catch (e) {
    // silent
  }
}

async function loadSubmissions() {
  try {
    const res = await fetch('/api/submissions');
    const data = await res.json();
    if (data.length === 0) {
      listEl.innerHTML = `
        <div class="empty-state">
          <div class="icon">○</div>
          <div class="title">No submissions yet</div>
          <div class="hint">Crawl a submission above to get started.</div>
        </div>`;
      return;
    }
    listEl.innerHTML = data.map(s => renderRow(s)).join('');
  } catch (e) {
    listEl.textContent = 'Failed to load submissions.';
  }
}

function renderRow(s) {
  const author = s.author ?? '[deleted]';
  return `
    <div class="sub-row">
      <div class="sub-score">
        <div class="sub-score-num">${s.score.toLocaleString()}</div>
        <div class="sub-score-label">votes</div>
      </div>
      <div class="sub-content">
        <a href="/submission/${s.id}" class="sub-title-link">${escapeHtml(s.title)}</a>
        <div class="sub-meta">
          <a href="/subreddit/${s.subreddit}">r/${s.subreddit}</a>
          <span class="dot">·</span>
          <a href="/author/${author}">u/${author}</a>
          <span class="dot">·</span>
          <span>${s.created_sgt.replace('T', ' ').substring(0, 16)} SGT</span>
        </div>
      </div>
      <div class="sub-comments">${s.num_comments.toLocaleString()} comments</div>
    </div>
  `;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}