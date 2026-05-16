# from datetime import datetime
# from sqlalchemy.orm import Session

# from backend.db.models import Submission, Comment
# from backend.crawler.reddit_client import get_reddit_client
# from backend.crawler.url_parser import extract_submission_id
# from backend.utils.timezone import epoch_to_utc


# def crawl_submission(url: str, db: Session) -> Submission:
#     """Crawl a Reddit submission and all its comments, then upsert into the DB."""
#     reddit = get_reddit_client()
#     submission_id = extract_submission_id(url)

#     submission = reddit.submission(id=submission_id)
#     _ = submission.title  # force lazy load, surfaces NotFound/Forbidden errors

#     sub_row = _upsert_submission(db, submission)
#     _upsert_comments(db, submission)

#     db.commit()
#     db.refresh(sub_row)
#     return sub_row


# def _upsert_submission(db: Session, submission) -> Submission:
#     row = db.get(Submission, submission.id)
#     if row is None:
#         row = Submission(id=submission.id)
#         db.add(row)

#     row.title = submission.title
#     row.author = str(submission.author) if submission.author else None
#     row.subreddit = str(submission.subreddit)
#     row.selftext = submission.selftext or None
#     row.url = f"https://www.reddit.com{submission.permalink}"
#     row.score = submission.score
#     row.num_comments = submission.num_comments
#     row.created_utc = epoch_to_utc(submission.created_utc)
#     row.crawled_at = datetime.utcnow()
#     return row


# def _upsert_comments(db: Session, submission) -> None:
#     # Expand all "load more comments" stubs so nothing is missed
#     submission.comments.replace_more(limit=None)

#     for c in submission.comments.list():
#         row = db.get(Comment, c.id)
#         if row is None:
#             row = Comment(id=c.id)
#             db.add(row)

#         row.submission_id = submission.id
#         row.parent_id = _parse_parent_id(c.parent_id)
#         row.author = str(c.author) if c.author else None
#         row.body = c.body
#         row.score = c.score
#         row.created_utc = epoch_to_utc(c.created_utc)
#         row.is_deleted = c.author is None or c.body in ("[deleted]", "[removed]")


# def _parse_parent_id(parent_raw: str) -> str | None:
#     """PRAW parent_id is prefixed: t1_ for comment, t3_ for submission.
#     Top-level comments have a t3_ parent — we store None for those."""
#     if parent_raw.startswith("t1_"):
#         return parent_raw[3:]
#     return None

from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session

from backend.db.models import Submission, Comment
from backend.crawler.url_parser import extract_submission_id


def crawl_submission(url: str, db: Session) -> Submission:
    """MOCK crawler: generates fake submission + comments for UI/DB testing.
    Replace with real PRAW logic once Reddit API access is sorted."""
    submission_id = extract_submission_id(url)
    sub_row = _mock_submission(db, submission_id, url)
    _mock_comments(db, submission_id)
    db.commit()
    db.refresh(sub_row)
    return sub_row


def _mock_submission(db: Session, submission_id: str, url: str) -> Submission:
    row = db.get(Submission, submission_id)
    if row is None:
        row = Submission(id=submission_id)
        db.add(row)

    row.title = f"[MOCK] Sample post about housing policy in Singapore"
    row.author = "mock_user_alice"
    row.subreddit = "singapore"
    row.selftext = (
        "This is fake selftext for testing the UI and database layer "
        "while Reddit API access is pending. Lorem ipsum dolor sit amet, "
        "consectetur adipiscing elit."
    )
    row.url = url
    row.score = 142
    row.num_comments = 8
    row.created_utc = datetime.utcnow() - timedelta(days=2)
    row.crawled_at = datetime.utcnow()
    return row


def _mock_comments(db: Session, submission_id: str) -> None:
    """Generates a tree of fake comments to test nested rendering."""
    mock_authors = ["alice_sg", "bob_tan", "charlie_lim", "dana_wong", "[deleted]"]
    mock_bodies = [
        "This is a really interesting point about MOP rules.",
        "I disagree — the policy hasn't been updated since 2018.",
        "Source? Last I checked it was 5 years not 10.",
        "Agreed. Here's the HDB link with the official timeline.",
        "Lol classic Reddit comment debating semantics.",
        "[deleted]",
        "Thanks for sharing this, I had no idea.",
        "Same here, learned something new today.",
    ]

    # Build a small tree: 3 top-level comments, some with replies
    comments_to_create = [
        # (comment_id, parent_id, author, body, score, is_deleted)
        ("c001", None, "alice_sg", mock_bodies[0], 25, False),
        ("c002", "c001", "bob_tan", mock_bodies[1], 12, False),
        ("c003", "c002", "alice_sg", mock_bodies[2], 8, False),
        ("c004", "c002", "charlie_lim", mock_bodies[3], 15, False),
        ("c005", None, "dana_wong", mock_bodies[4], 18, False),
        ("c006", "c005", None, "[deleted]", -2, True),
        ("c007", None, "bob_tan", mock_bodies[6], 7, False),
        ("c008", "c007", "alice_sg", mock_bodies[7], 3, False),
    ]

    for cid, pid, author, body, score, is_deleted in comments_to_create:
        row = db.get(Comment, cid)
        if row is None:
            row = Comment(id=cid)
            db.add(row)

        row.submission_id = submission_id
        row.parent_id = pid
        row.author = author
        row.body = body
        row.score = score
        row.created_utc = datetime.utcnow() - timedelta(hours=random.randint(1, 48))
        row.is_deleted = is_deleted