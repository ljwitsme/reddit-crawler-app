const urlInput = document.getElementById('url');
const crawlBtn = document.getElementById('crawl-btn');
const statusEl = document.getElementById('status');

const listEl = document.getElementById('submissions-list');
const statsEl = document.getElementById('stats');
const sortSelect = document.getElementById('sort-select');

const PAGE_SIZE = 10;
let currentPage = 1;
let currentSort = 'newest';

crawlBtn.addEventListener('click', crawl);
urlInput.addEventListener('keydown', e => { if (e.key === 'Enter') crawl(); });

sortSelect.addEventListener('change', () => {
  currentSort = sortSelect.value;
  loadSubmissions(1);
});

loadStats();
loadSubmissions(1);

async function crawl() {
  const url = urlInput.value.trim();
  if (!url) return;
  setStatus(statusEl, '<span class="spinner"></span>Crawling the post and 50 more from the same subreddit. This takes 1–3 minutes...');
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
    const subInfo = data.batch_count !== undefined
      ? ` Also crawled ${data.batch_count} additional posts from r/${data.subreddit}.`
      : '';
    setStatus(
      statusEl,
      `✓ Done.${subInfo} <a href="/submission/${data.submission.id}">View submission →</a>`,
      'success'
    );
    loadStats();
    loadSubmissions(1);
  } catch (e) {
    setStatus(statusEl, '✗ ' + e.message, 'error');
  } finally {
    crawlBtn.disabled = false;
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

async function loadSubmissions(page) {
  currentPage = page;
  listEl.innerHTML = '<div class="loading"><span class="spinner"></span>Loading...</div>';
  try {
    const res = await fetch(`/api/submissions?page=${page}&page_size=${PAGE_SIZE}&sort=${currentSort}`);
    const data = await res.json();

    if (data.total === 0) {
      listEl.innerHTML = `
        <div class="empty-state">
          <div class="icon">○</div>
          <div class="title">No submissions yet</div>
          <div class="hint">Crawl a submission above to get started.</div>
        </div>`;
      return;
    }

    listEl.innerHTML = `
      ${data.items.map(renderRow).join('')}
      ${renderPagination(data)}
    `;

    listEl.querySelectorAll('[data-page]').forEach(btn => {
      btn.addEventListener('click', () => {
        loadSubmissions(parseInt(btn.dataset.page));
      });
    });
  } catch (e) {
    listEl.textContent = 'Failed to load submissions.';
  }
}

function renderRow(s) {
  const author = s.author ?? '[deleted]';

  // When sorting by "newest crawled", show the crawl time.
  // Otherwise, show the Reddit post creation time.
  const timeToShow = currentSort === 'newest' ? s.crawled_at_sgt : s.created_sgt;
  const timeLabel = currentSort === 'newest' ? 'crawled' : 'posted';

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
          <span>${timeLabel} ${timeToShow.replace('T', ' ').substring(0, 16)} SGT</span>
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

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}