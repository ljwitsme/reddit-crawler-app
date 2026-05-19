"""Crawler service — thin dispatcher to PRAW-backed implementations."""
from datetime import datetime
from sqlalchemy.orm import Session

from backend.db.models import Submission, Author
from backend.crawler.real_crawler import (
    crawl_submission_real,
    crawl_subreddit_batch_real,
    crawl_author_history_real,
)


def crawl_submission(url: str, db: Session) -> Submission:
    # 1. Crawl the specific submission (with its full comment tree)
    submission = crawl_submission_real(url, db)

    # 2. Auto-batch 50 more posts from the same subreddit
    #    (Bonus Objective 1a — subreddit expansion)
    try:
        crawl_subreddit_batch_real(submission.subreddit, limit=50, db=db)
    except Exception as e:
        # Don't fail the entire request if the batch errors;
        # the user still gets their requested submission.
        print(f"[crawl_submission] Auto-batch failed for r/{submission.subreddit}: {e}")

    return submission


def crawl_subreddit_batch(subreddit: str, limit: int, db: Session) -> list[Submission]:
    return crawl_subreddit_batch_real(subreddit, limit, db)


def fetch_author_history(username: str, db: Session, limit: int = 100) -> int:
    count = crawl_author_history_real(username, db, limit)
    _update_author_record(db, username, count)
    return count


def _update_author_record(db: Session, username: str, count: int) -> None:
    author = db.get(Author, username)
    if author is None:
        author = Author(username=username)
        db.add(author)
    author.last_fetched_at = datetime.utcnow()
    author.total_comments_fetched = count
    db.commit()