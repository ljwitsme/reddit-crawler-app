const pathParts = window.location.pathname.split('/');
const subredditName = decodeURIComponent(pathParts[pathParts.length - 1]);
const contentEl = document.getElementById('content');
const batchBtn = document.getElementById('batch-btn');
const batchStatusEl = document.getElementById('batch-status');

const PAGE_SIZE = 10;
let currentPage = 1;
let currentSort = 'newest';

document.getElementById('sub-name').textContent = `r/${subredditName}`;
document.getElementById('crumb-name').textContent = `r/${subredditName}`;

batchBtn.addEventListener('click', batchCrawl);
load(1);

async function load(page) {
  currentPage = page;
  contentEl.innerHTML = '<div class="loading"><span class="spinner"></span>Loading...</div>';
  try {
    const res = await fetch(`/api/submissions?subreddit=${encodeURIComponent(subredditName)}&page=${page}&page_size=${PAGE_SIZE}&sort=${currentSort}`);
    const data = await res.json();
    if (data.total === 0) {
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
            <h2 class="panel-title">${data.total.toLocaleString()} submissions</h2>
            <div class="panel-subtitle">All posts crawled from this subreddit</div>
          </div>
          <select id="sort-select" class="sort-select">
            <option value="newest" ${currentSort === 'newest' ? 'selected' : ''}>Newest crawled</option>
            <option value="upvotes" ${currentSort === 'upvotes' ? 'selected' : ''}>Most upvotes</option>
            <option value="comments" ${currentSort === 'comments' ? 'selected' : ''}>Most comments</option>
          </select>
        </div>
        <div class="panel-body tight">
          <div class="sub-list">${data.items.map(renderRow).join('')}</div>
          ${renderPagination(data)}
        </div>
      </div>
    `;

    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
      sortSelect.addEventListener('change', () => {
        currentSort = sortSelect.value;
        load(1);
      });
    }

    contentEl.querySelectorAll('[data-page]').forEach(btn => {
      btn.addEventListener('click', () => load(parseInt(btn.dataset.page)));
    });
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

function renderPagination(data) {
  if (data.total_pages <= 1) return '';

  const start = (data.page - 1) * data.page_size + 1;
  const end = Math.min(data.page * data.page_size, data.total);

  const pageNumbers = getPageNumbers(data.page, data.total_pages);
  const numberButtons = pageNumbers.map(p => {
    if (p === '...') return `<span class="page-ellipsis">…</span>`;
    const isActive = p === data.page;
    return `<button class="page-btn ${isActive ? 'active' : ''}" data-page="${p}">${p}</button>`;
  }).join('');

  return `
    <div class="pagination">
      <div class="pagination-info">
        Showing ${start.toLocaleString()}–${end.toLocaleString()} of ${data.total.toLocaleString()}
      </div>
      <div class="pagination-controls">
        <button class="page-btn" data-page="${data.page - 1}" ${data.page === 1 ? 'disabled' : ''}>← Prev</button>
        ${numberButtons}
        <button class="page-btn" data-page="${data.page + 1}" ${data.page === data.total_pages ? 'disabled' : ''}>Next →</button>
      </div>
    </div>
  `;
}

function getPageNumbers(current, total) {
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }
  const pages = [1];
  if (current > 3) pages.push('...');
  for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) {
    pages.push(i);
  }
  if (current < total - 2) pages.push('...');
  pages.push(total);
  return pages;
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
    load(1);
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