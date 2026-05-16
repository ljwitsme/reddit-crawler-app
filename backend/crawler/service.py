from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session

from backend.db.models import Submission, Comment
from backend.crawler.url_parser import extract_submission_id


# ---------- Single submission mock crawler ----------

def crawl_submission(url: str, db: Session) -> Submission:
    """MOCK crawler: generates fake submission + comments for UI/DB testing."""
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
        "while Reddit API access is pending."
    )
    row.url = url
    row.score = 142
    row.num_comments = 8
    row.created_utc = datetime.utcnow() - timedelta(days=2)
    row.crawled_at = datetime.utcnow()
    return row


def _mock_comments(db: Session, submission_id: str) -> None:
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

    comments_to_create = [
        # (suffix, parent_suffix, author, body, score, is_deleted)
        ("c001", None, "alice_sg", mock_bodies[0], 25, False),
        ("c002", "c001", "bob_tan", mock_bodies[1], 12, False),
        ("c003", "c002", "alice_sg", mock_bodies[2], 8, False),
        ("c004", "c002", "charlie_lim", mock_bodies[3], 15, False),
        ("c005", None, "dana_wong", mock_bodies[4], 18, False),
        ("c006", "c005", None, "[deleted]", -2, True),
        ("c007", None, "bob_tan", mock_bodies[6], 7, False),
        ("c008", "c007", "alice_sg", mock_bodies[7], 3, False),
    ]

    for suffix, parent_suffix, author, body, score, is_deleted in comments_to_create:
        # Make comment IDs unique per submission by prefixing
        cid = f"{submission_id}_{suffix}"
        pid = f"{submission_id}_{parent_suffix}" if parent_suffix else None

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


# ---------- Bonus 1a: Subreddit expansion mock ----------

def crawl_subreddit_batch(subreddit: str, limit: int, db: Session) -> list[Submission]:
    """MOCK: generate `limit` fake submissions for the given subreddit."""
    mock_titles = [
        "Discussion: New transport policy effects",
        "Anyone else noticed price hikes at NTUC?",
        "Best hawker centres in CBD area",
        "Help — first time buying HDB resale",
        "Career advice for fresh grads in tech",
        "PSA: New COE bidding rules explained",
        "Weekend trip recommendations near SG",
        "MRT breakdown this morning — anyone affected?",
        "Singapore food scene is changing fast",
        "Honest review of the new shopping mall",
    ]
    mock_authors_pool = [
        "alice_sg", "bob_tan", "charlie_lim", "dana_wong", "evan_lee",
        "fiona_ng", "grace_teo", "henry_koh", "ivan_yeo", "jane_low",
    ]

    created = []
    for i in range(limit):
        sub_id = f"mock_{subreddit}_{i:03d}"
        row = db.get(Submission, sub_id)
        if row is None:
            row = Submission(id=sub_id)
            db.add(row)

        row.title = f"[MOCK] {random.choice(mock_titles)} (#{i+1})"
        row.author = random.choice(mock_authors_pool)
        row.subreddit = subreddit
        row.selftext = "Mock submission body for subreddit expansion testing."
        row.url = f"https://www.reddit.com/r/{subreddit}/comments/{sub_id}/mock/"
        row.score = random.randint(5, 500)
        row.num_comments = random.randint(0, 50)
        row.created_utc = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        row.crawled_at = datetime.utcnow()
        created.append(row)

        # Add a few mock comments per submission
        _mock_few_comments(db, sub_id, mock_authors_pool, subreddit)

    db.commit()
    for r in created:
        db.refresh(r)
    return created


def _mock_few_comments(db: Session, submission_id: str, authors: list[str], subreddit: str) -> None:
    """Add 3-5 mock comments to a submission (for subreddit expansion)."""
    bodies = [
        "Great post, thanks for sharing.",
        "I had a similar experience last month.",
        "Source needed.",
        "This needs more attention.",
        "Completely agree with OP.",
    ]
    n = random.randint(3, 5)
    for i in range(n):
        cid = f"{submission_id}_c{i:02d}"
        row = db.get(Comment, cid)
        if row is None:
            row = Comment(id=cid)
            db.add(row)
        row.submission_id = submission_id
        row.parent_id = None
        row.author = random.choice(authors)
        row.body = random.choice(bodies)
        row.score = random.randint(1, 50)
        row.created_utc = datetime.utcnow() - timedelta(hours=random.randint(1, 100))
        row.is_deleted = False