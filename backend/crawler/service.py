from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session

from backend.config import settings
from backend.db.models import Submission, Comment, Author
from backend.crawler.url_parser import extract_submission_id


# ===========================================================
# Public API — what routes.py calls
# ===========================================================

def crawl_submission(url: str, db: Session) -> Submission:
    if settings.USE_MOCK:
        return _mock_crawl_submission(url, db)
    from backend.crawler.real_crawler import crawl_submission_real
    return crawl_submission_real(url, db)


def crawl_subreddit_batch(subreddit: str, limit: int, db: Session) -> list[Submission]:
    if settings.USE_MOCK:
        return _mock_crawl_subreddit_batch(subreddit, limit, db)
    from backend.crawler.real_crawler import crawl_subreddit_batch_real
    return crawl_subreddit_batch_real(subreddit, limit, db)


def fetch_author_history(username: str, db: Session, limit: int = 100) -> int:
    if settings.USE_MOCK:
        return _mock_fetch_author_history(username, db, limit)
    from backend.crawler.real_crawler import crawl_author_history_real
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


# ===========================================================
# Mock implementations
# ===========================================================

def _mock_crawl_submission(url: str, db: Session) -> Submission:
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

    row.title = "[MOCK] Sample post about housing policy in Singapore"
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
        row.submission_title = "[MOCK] Sample post about housing policy in Singapore"
        row.submission_subreddit = "singapore"


def _mock_crawl_subreddit_batch(subreddit: str, limit: int, db: Session) -> list[Submission]:
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

        title = f"[MOCK] {random.choice(mock_titles)} (#{i+1})"
        row.title = title
        row.author = random.choice(mock_authors_pool)
        row.subreddit = subreddit
        row.selftext = "Mock submission body for subreddit expansion testing."
        row.url = f"https://www.reddit.com/r/{subreddit}/comments/{sub_id}/mock/"
        row.score = random.randint(5, 500)
        row.num_comments = random.randint(0, 50)
        row.created_utc = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        row.crawled_at = datetime.utcnow()
        created.append(row)

        _mock_few_comments(db, sub_id, title, subreddit, mock_authors_pool)

    db.commit()
    for r in created:
        db.refresh(r)
    return created


def _mock_few_comments(db: Session, submission_id: str, title: str, subreddit: str, authors: list[str]) -> None:
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
        row.submission_title = title
        row.submission_subreddit = subreddit


def _mock_fetch_author_history(username: str, db: Session, limit: int) -> int:
    other_subreddits = [
        "AskReddit", "worldnews", "technology", "personalfinance",
        "MapPorn", "books", "movies", "AskHistorians",
    ]
    bodies = [
        "I lived through this. Here's my take...",
        "Citation needed but interesting if true.",
        "Same thing happened in 2019.",
        "Strongly disagree, here's why.",
        "TIL — never knew this.",
        "OP's analysis is spot on.",
        "Anyone got a primary source?",
    ]

    count = 0
    for i in range(min(limit, 15)):
        cid = f"ext_{username}_{i:03d}"
        sub_id = f"ext_sub_{username}_{i:03d}"
        chosen_sub = random.choice(other_subreddits)
        chosen_title = f"External submission #{i+1} on {chosen_sub}"

        sub_row = db.get(Submission, sub_id)
        if sub_row is None:
            sub_row = Submission(
                id=sub_id,
                title=chosen_title,
                author="some_other_user",
                subreddit=chosen_sub,
                selftext=None,
                url=f"https://www.reddit.com/r/{chosen_sub}/comments/{sub_id}/",
                score=random.randint(10, 5000),
                num_comments=random.randint(5, 500),
                created_utc=datetime.utcnow() - timedelta(days=random.randint(5, 90)),
                crawled_at=datetime.utcnow(),
            )
            db.add(sub_row)

        row = db.get(Comment, cid)
        if row is None:
            row = Comment(id=cid)
            db.add(row)

        row.submission_id = sub_id
        row.parent_id = None
        row.author = username
        row.body = random.choice(bodies)
        row.score = random.randint(1, 200)
        row.created_utc = datetime.utcnow() - timedelta(days=random.randint(1, 60))
        row.is_deleted = False
        row.submission_title = chosen_title
        row.submission_subreddit = chosen_sub
        count += 1

    _update_author_record(db, username, count)
    return count