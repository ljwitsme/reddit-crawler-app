const pathParts = window.location.pathname.split('/');
const subredditName = decodeURIComponent(pathParts[pathParts.length - 1]);
const contentEl = document.getElementById('content');
const batchBtn = document.getElementById('batch-btn');
const batchStatusEl = document.getElementById('batch-status');

document.getElementById('sub-name').textContent = `r/${subredditName}`;
document.getElementById('crumb-name').textContent = `r/${subredditName}`;

batchBtn.addEventListener('click', batchCrawl);
load();

async function load() {
  try {
    const res = await fetch(`/api/submissions?subreddit=${encodeURIComponent(subredditName)}`);
    const data = await res.json();
    if (data.length === 0) {
      contentEl.innerHTML = `
        <div class="empty-state">
          <div class="icon">○</div>
          <div class="title">No submissions for r/${subredditName}</div>
          <div class="hint">Click "Crawl 50 more posts" above to seed the database.</div>
        </div>`;
      return;
    }
    contentEl.innerHTML = `
      <div class="panel">
        <div class="panel-header">
          <div>
            <h2 class="panel-title">${data.length} submissions</h2>
            <div class="panel-subtitle">All posts crawled from this subreddit</div>
          </div>
        </div>
        <div class="panel-body tight">
          <div class="sub-list">${data.map(renderRow).join('')}</div>
        </div>
      </div>
    `;
  } catch (e) {
    contentEl.textContent = 'Error: ' + e.message;
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
          <a href="/author/${author}">u/${author}</a>
          <span class="dot">·</span>
          <span>${s.created_sgt.replace('T', ' ').substring(0, 16)} SGT</span>
        </div>
      </div>
      <div class="sub-comments">${s.num_comments.toLocaleString()} comments</div>
    </div>
  `;
}

async function batchCrawl() {
  batchBtn.disabled = true;
  batchStatusEl.className = 'status-msg';
  batchStatusEl.innerHTML = '<span class="spinner"></span>Crawling 50 posts...';
  try {
    const res = await fetch('/api/crawl-subreddit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ subreddit: subredditName, limit: 50 }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || res.statusText);
    }
    const data = await res.json();
    batchStatusEl.className = 'status-msg success';
    batchStatusEl.textContent = `✓ Added ${data.length} posts.`;
    load();
  } catch (e) {
    batchStatusEl.className = 'status-msg error';
    batchStatusEl.textContent = '✗ ' + e.message;
  } finally {
    batchBtn.disabled = false;
  }
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}