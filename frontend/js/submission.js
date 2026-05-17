const COMMENTS_PER_PAGE = 20;

const resultEl = document.getElementById('result');
const submissionId = window.location.pathname.split('/').pop();

let submissionData = null;
let topLevelComments = [];
let commentsByParent = {};
let currentPage = 1;
let collapsedSet = new Set();

loadSubmission();

async function loadSubmission() {
  try {
    const res = await fetch(`/api/submissions/${submissionId}`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || res.statusText);
    }
    submissionData = await res.json();
    organizeComments();
    render();
  } catch (e) {
    resultEl.innerHTML = `
      <div class="empty-state">
        <div class="icon">⚠</div>
        <div class="title">Failed to load</div>
        <div class="hint">${escapeHtml(e.message)}</div>
      </div>`;
  }
}

function organizeComments() {
  commentsByParent = {};
  for (const c of submissionData.comments) {
    const key = c.parent_id || 'ROOT';
    if (!commentsByParent[key]) commentsByParent[key] = [];
    commentsByParent[key].push(c);
  }
  for (const key in commentsByParent) {
    commentsByParent[key].sort((a, b) => b.score - a.score);
  }
  topLevelComments = commentsByParent['ROOT'] || [];
}

function render() {
  const s = submissionData;
  const totalTopLevel = topLevelComments.length;
  const totalComments = submissionData.comments.length;
  const totalPages = Math.max(1, Math.ceil(totalTopLevel / COMMENTS_PER_PAGE));
  if (currentPage > totalPages) currentPage = totalPages;
  const startIdx = (currentPage - 1) * COMMENTS_PER_PAGE;
  const endIdx = Math.min(startIdx + COMMENTS_PER_PAGE, totalTopLevel);
  const pageComments = topLevelComments.slice(startIdx, endIdx);

  resultEl.innerHTML = `
    <div class="submission-card">
      <h2>${escapeHtml(s.title)}</h2>
      <div class="meta">
        <a href="/subreddit/${s.subreddit}">r/${s.subreddit}</a>
        <span class="dot">·</span>
        Posted by <a href="/author/${s.author ?? '[deleted]'}">u/${s.author ?? '[deleted]'}</a>
        <span class="dot">·</span>
        ${s.created_sgt.replace('T', ' ').substring(0, 16)} SGT
        <span class="dot">·</span>
        ${s.score.toLocaleString()} points
        <span class="dot">·</span>
        ${s.num_comments.toLocaleString()} comments on Reddit
        <span class="dot">·</span>
        <a href="${s.url}" target="_blank" rel="noopener">View on Reddit ↗</a>
      </div>
      ${s.selftext ? `<div class="selftext">${escapeHtml(s.selftext)}</div>` : ''}
    </div>

    <div class="comments-section">
      <h3>Comments (${totalComments.toLocaleString()})</h3>
      ${totalTopLevel === 0 ? `
        <div class="empty-state">
          <div class="icon">○</div>
          <div class="hint">No comments on this submission.</div>
        </div>
      ` : `
        <div class="comment-controls">
          <button class="text-btn" id="expand-all">Expand all</button>
          <button class="text-btn" id="collapse-all">Collapse all</button>
        </div>
        <div id="comments-tree">${pageComments.map(c => renderComment(c)).join('')}</div>
        ${renderPagination(currentPage, totalPages, startIdx, endIdx, totalTopLevel)}
      `}
    </div>
  `;

  attachHandlers();
}

function renderComment(c) {
  const author = c.author ?? '[deleted]';
  const deletedClass = c.is_deleted ? ' deleted' : '';
  const children = commentsByParent[c.id] || [];
  const hasChildren = children.length > 0;
  const isCollapsed = collapsedSet.has(c.id);
  const collapsedClass = isCollapsed && hasChildren ? ' collapsed-row' : '';

  const toggle = hasChildren
    ? `<button class="collapse-toggle" data-id="${c.id}">${isCollapsed ? '+' : '−'}</button>`
    : `<span class="collapse-spacer"></span>`;

  const childrenCountLabel = isCollapsed && hasChildren
    ? ` <span class="hidden-count">(${countDescendants(c.id)} hidden)</span>`
    : '';

  const childrenHtml = (hasChildren && !isCollapsed)
    ? `<div class="comment-children">${children.map(child => renderComment(child)).join('')}</div>`
    : '';

  return `
    <div class="comment${deletedClass}${collapsedClass}">
      <div class="comment-header">
        ${toggle}
        <div class="comment-content">
          <div class="meta">
            <a href="/author/${author}"><strong>u/${author}</strong></a>
            <span class="dot">·</span>
            ${c.score.toLocaleString()} points
            <span class="dot">·</span>
            ${c.created_sgt.replace('T', ' ').substring(0, 16)} SGT
            ${childrenCountLabel}
          </div>
          ${!isCollapsed ? `<div class="comment-body">${escapeHtml(c.body)}</div>` : ''}
        </div>
      </div>
      ${childrenHtml}
    </div>
  `;
}

function countDescendants(commentId) {
  const children = commentsByParent[commentId] || [];
  let count = children.length;
  for (const c of children) count += countDescendants(c.id);
  return count;
}

function renderPagination(page, totalPages, startIdx, endIdx, total) {
  if (totalPages <= 1) return '';
  const pageNumbers = getPageNumbers(page, totalPages);
  const numberButtons = pageNumbers.map(p => {
    if (p === '...') return `<span class="page-ellipsis">…</span>`;
    return `<button class="page-btn ${p === page ? 'active' : ''}" data-page="${p}">${p}</button>`;
  }).join('');
  return `
    <div class="pagination">
      <div class="pagination-info">
        Showing ${(startIdx + 1).toLocaleString()}–${endIdx.toLocaleString()} of ${total.toLocaleString()} top-level comments
      </div>
      <div class="pagination-controls">
        <button class="page-btn" data-page="${page - 1}" ${page === 1 ? 'disabled' : ''}>← Prev</button>
        ${numberButtons}
        <button class="page-btn" data-page="${page + 1}" ${page === totalPages ? 'disabled' : ''}>Next →</button>
      </div>
    </div>
  `;
}

function getPageNumbers(current, total) {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
  const pages = [1];
  if (current > 3) pages.push('...');
  for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) {
    pages.push(i);
  }
  if (current < total - 2) pages.push('...');
  pages.push(total);
  return pages;
}

function attachHandlers() {
  document.querySelectorAll('[data-page]').forEach(btn => {
    btn.addEventListener('click', () => {
      currentPage = parseInt(btn.dataset.page);
      render();
      const target = document.querySelector('.comments-section');
      if (target) {
        window.scrollTo({ top: target.offsetTop - 20, behavior: 'smooth' });
      }
    });
  });

  document.querySelectorAll('.collapse-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.id;
      if (collapsedSet.has(id)) collapsedSet.delete(id);
      else collapsedSet.add(id);
      render();
    });
  });

  const expandAllBtn = document.getElementById('expand-all');
  const collapseAllBtn = document.getElementById('collapse-all');
  if (expandAllBtn) {
    expandAllBtn.addEventListener('click', () => {
      collapsedSet.clear();
      render();
    });
  }
  if (collapseAllBtn) {
    collapseAllBtn.addEventListener('click', () => {
      collapsedSet.clear();
      for (const c of submissionData.comments) {
        if ((commentsByParent[c.id] || []).length > 0) collapsedSet.add(c.id);
      }
      render();
    });
  }
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}