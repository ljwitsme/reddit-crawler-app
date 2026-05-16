const pathParts = window.location.pathname.split('/');
const submissionId = pathParts[pathParts.length - 1];
const resultEl = document.getElementById('result');

load();

async function load() {
  try {
    const res = await fetch(`/api/submissions/${submissionId}`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || res.statusText);
    }
    const sub = await res.json();
    render(sub);
  } catch (e) {
    resultEl.innerHTML = `<div class="empty-state"><div class="icon">⚠</div><div class="title">Could not load submission</div><div class="hint">${escapeHtml(e.message)}</div></div>`;
  }
}

function render(sub) {
  const author = sub.author ?? '[deleted]';
  resultEl.innerHTML = `
    <div class="submission-card">
      <h2>${escapeHtml(sub.title)}</h2>
      <div class="meta">
        <a href="/subreddit/${sub.subreddit}">r/${sub.subreddit}</a>
        · <a href="/author/${author}">u/${author}</a>
        · ${sub.score.toLocaleString()} upvotes
        · ${sub.num_comments.toLocaleString()} comments
        · ${sub.created_sgt.replace('T', ' ').substring(0, 16)} SGT
        · <a href="${sub.url}" target="_blank">View on Reddit ↗</a>
      </div>
      ${sub.selftext ? `<div class="selftext">${escapeHtml(sub.selftext)}</div>` : ''}
    </div>
    <div class="comments-section">
      <h3>Comments (${sub.comments.length})</h3>
      <div id="comments"></div>
    </div>
  `;

  const byParent = {};
  sub.comments.forEach(c => {
    const key = c.parent_id || 'ROOT';
    (byParent[key] ||= []).push(c);
  });
  renderLevel(document.getElementById('comments'), byParent, 'ROOT');
}

function renderLevel(container, byParent, parentKey) {
  const children = byParent[parentKey] || [];
  children.sort((a, b) => b.score - a.score);
  children.forEach(c => {
    const div = document.createElement('div');
    div.className = 'comment' + (c.is_deleted ? ' deleted' : '');
    const authorLink = c.author && !c.is_deleted
      ? `<a href="/author/${c.author}"><strong>u/${c.author}</strong></a>`
      : `<strong>${c.author ?? '[deleted]'}</strong>`;
    div.innerHTML = `
      <div class="meta">${authorLink} · ${c.score} points · ${c.created_sgt.replace('T', ' ').substring(0, 16)} SGT</div>
      <div class="comment-body">${escapeHtml(c.body || '')}</div>
    `;
    container.appendChild(div);
    renderLevel(div, byParent, c.id);
  });
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}