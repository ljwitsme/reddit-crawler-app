const urlInput = document.getElementById('url');
const crawlBtn = document.getElementById('crawl-btn');
const statusEl = document.getElementById('status');
const resultEl = document.getElementById('result');

crawlBtn.addEventListener('click', crawl);
urlInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') crawl(); });

async function crawl() {
  const url = urlInput.value.trim();
  if (!url) return;

  statusEl.textContent = 'Crawling... (this may take 10-60s for large threads)';
  resultEl.innerHTML = '';
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
    render(data);
    statusEl.textContent = `Done. ${data.comments.length} comments stored.`;
  } catch (e) {
    statusEl.textContent = 'Error: ' + e.message;
  } finally {
    crawlBtn.disabled = false;
  }
}

function render(sub) {
  resultEl.innerHTML = `
    <div class="submission">
      <h2>${escapeHtml(sub.title)}</h2>
      <div class="meta">
        r/${sub.subreddit} · by ${sub.author ?? '[deleted]'} ·
        ${sub.score} upvotes · ${sub.num_comments} comments ·
        ${sub.created_sgt} SGT
      </div>
      <p>${escapeHtml(sub.selftext || '')}</p>
    </div>
    <h3>Comments</h3>
    <div id="comments"></div>
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
    div.innerHTML = `
      <div class="meta">${c.author ?? '[deleted]'} · ${c.score} pts · ${c.created_sgt} SGT</div>
      <div>${escapeHtml(c.body || '')}</div>
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