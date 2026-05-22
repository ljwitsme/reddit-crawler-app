from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.db.models import Submission, Comment
from backend.crawler.reddit_client import get_reddit_client
from backend.crawler.url_parser import extract_submission_id
from backend.utils.timezone import epoch_to_utc


# ---------- Real: single submission ----------

def crawl_submission_real(url: str, db: Session) -> Submission:
    """Real crawler: uses PRAW to fetch a submission and all its comments."""
    reddit = get_reddit_client()
    submission_id = extract_submission_id(url)

    submission = reddit.submission(id=submission_id)
    _ = submission.title  # force lazy load

    sub_row = _upsert_submission(db, submission)
    _upsert_comments(db, submission)

    db.commit()
    db.refresh(sub_row)
    return sub_row


def _upsert_submission(db: Session, submission) -> Submission:
    row = db.get(Submission, submission.id)
    if row is None:
        row = Submission(id=submission.id)
        db.add(row)

    row.title = submission.title
    row.author = str(submission.author) if submission.author else None
    row.subreddit = str(submission.subreddit)
    row.selftext = submission.selftext or None
    row.url = f"https://www.reddit.com{submission.permalink}"
    row.score = submission.score
    row.num_comments = submission.num_comments
    row.created_utc = epoch_to_utc(submission.created_utc)
    row.crawled_at = datetime.utcnow()
    return row


def _upsert_comments(db: Session, submission) -> None:
    submission.comments.replace_more(limit=None)

    for c in submission.comments.list():
        row = db.get(Comment, c.id)
        if row is None:
            row = Comment(id=c.id)
            db.add(row)

        row.submission_id = submission.id
        row.parent_id = _parse_parent_id(c.parent_id)
        row.author = str(c.author) if c.author else None
        row.body = c.body
        row.score = c.score
        row.created_utc = epoch_to_utc(c.created_utc)
        row.is_deleted = c.author is None or c.body in ("[deleted]", "[removed]")
        row.submission_title = str(submission.title)
        row.submission_subreddit = str(submission.subreddit)


def _parse_parent_id(parent_raw: str) -> str | None:
    if parent_raw.startswith("t1_"):
        return parent_raw[3:]
    return None


# ---------- Real: subreddit batch ----------

def crawl_subreddit_batch_real(subreddit: str, limit: int, db: Session) -> list[Submission]:
    """Fetch the most recent `limit` submissions from a subreddit and crawl each."""
    reddit = get_reddit_client()
    sub = reddit.subreddit(subreddit)

    created = []
    for submission in sub.new(limit=limit):
        _ = submission.title  # force load

        sub_row = _upsert_submission(db, submission)
        _upsert_comments(db, submission)
        created.append(sub_row)

    db.commit()
    for r in created:
        db.refresh(r)
    return created


# ---------- Real: author history ----------

def crawl_author_history_real(username: str, db: Session, limit: int = 100) -> int:
    """Fetch a user's recent comments across all of Reddit and store them.
    Returns the count of comments stored.

    Handles the case where the author commented multiple times on the same
    submission by deduplicating within the transaction.
    """
    reddit = get_reddit_client()
    redditor = reddit.redditor(username)

    # Track what we've already added in this transaction to avoid duplicate inserts.
    seen_submission_ids: set[str] = set()
    seen_comment_ids: set[str] = set()
    count = 0

    for c in redditor.comments.new(limit=limit):
        # Skip if we've already processed this exact comment in this batch
        if c.id in seen_comment_ids:
            continue
        seen_comment_ids.add(c.id)

        # ---- Upsert the comment ----
        comment_row = db.get(Comment, c.id)
        if comment_row is None:
            comment_row = Comment(id=c.id)
            db.add(comment_row)

        comment_row.submission_id = c.submission.id
        comment_row.parent_id = _parse_parent_id(c.parent_id)
        comment_row.author = username
        comment_row.body = c.body
        comment_row.score = c.score
        comment_row.created_utc = epoch_to_utc(c.created_utc)
        comment_row.is_deleted = False
        comment_row.submission_title = str(c.submission.title)
        comment_row.submission_subreddit = str(c.subreddit)

        # ---- Ensure a Submission row exists (placeholder if not yet crawled) ----
        # Only attempt this once per submission per transaction.
        if c.submission.id not in seen_submission_ids:
            seen_submission_ids.add(c.submission.id)

            sub_row = db.get(Submission, c.submission.id)
            if sub_row is None:
                sub_row = Submission(
                    id=c.submission.id,
                    title=str(c.submission.title),
                    author=str(c.submission.author) if c.submission.author else None,
                    subreddit=str(c.subreddit),
                    selftext=None,
                    url=f"https://www.reddit.com{c.submission.permalink}",
                    score=c.submission.score,
                    num_comments=c.submission.num_comments,
                    created_utc=epoch_to_utc(c.submission.created_utc),
                    crawled_at=datetime.utcnow(),
                )
                db.add(sub_row)

        count += 1

    db.commit()
    return count