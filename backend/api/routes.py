from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from prawcore.exceptions import NotFound, Forbidden, ResponseException

from backend.database import engine, Base, get_db
from backend.db.models import Submission, Comment, Author
from backend.crawler.service import (
    crawl_submission,
    crawl_subreddit_batch,
    fetch_author_history,
)
from backend.utils.timezone import utc_to_sgt_iso
from backend.api.schemas import (
    CrawlRequest,
    SubredditCrawlRequest,
    SubmissionOut,
    CommentOut,
    SubmissionSummary,
    AuthorOut,
    CommentWithContext,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Reddit Crawler", version="0.5.0")


def _serialize_submission(sub: Submission) -> SubmissionOut:
    return SubmissionOut(
        id=sub.id,
        title=sub.title,
        author=sub.author,
        subreddit=sub.subreddit,
        selftext=sub.selftext,
        url=sub.url,
        score=sub.score,
        num_comments=sub.num_comments,
        created_sgt=utc_to_sgt_iso(sub.created_utc),
        comments=[
            CommentOut(
                id=c.id,
                parent_id=c.parent_id,
                author=c.author,
                body=c.body,
                score=c.score,
                created_sgt=utc_to_sgt_iso(c.created_utc),
                is_deleted=c.is_deleted,
            )
            for c in sub.comments
        ],
    )


def _serialize_summary(s: Submission) -> SubmissionSummary:
    return SubmissionSummary(
        id=s.id,
        title=s.title,
        subreddit=s.subreddit,
        author=s.author,
        score=s.score,
        num_comments=s.num_comments,
        created_sgt=utc_to_sgt_iso(s.created_utc),
        crawled_at_sgt=utc_to_sgt_iso(s.crawled_at),
    )


# ---------- Core: single submission + auto subreddit expansion ----------

@app.post("/api/crawl")
def crawl(req: CrawlRequest, db: Session = Depends(get_db)):
    """
    Crawl a Reddit submission by URL.

    Per the brief's Bonus Objective 1 (Subreddit Expansion Crawling):
    after fetching the specified submission, the same subreddit is
    automatically expanded — up to 50 more posts from that subreddit
    are crawled and stored.
    """
    try:
        sub = crawl_submission(req.url, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFound:
        raise HTTPException(status_code=404, detail="Submission not found")
    except Forbidden:
        raise HTTPException(status_code=403, detail="Submission is private or restricted")
    except ResponseException as e:
        raise HTTPException(status_code=502, detail=f"Reddit API error: {e}")

    # Bonus 1a: also crawl 50 more posts from the same subreddit
    batch_count = 0
    try:
        batch_subs = crawl_subreddit_batch(sub.subreddit, 50, db)
        batch_count = len(batch_subs)
    except (NotFound, Forbidden, ResponseException):
        # If the subreddit expansion fails for any reason, don't fail the whole request.
        # The user still gets the specific submission they asked for.
        batch_count = 0

    return {
        "submission": _serialize_submission(sub).model_dump(),
        "subreddit": sub.subreddit,
        "batch_count": batch_count,
    }


@app.get("/api/submissions/{submission_id}", response_model=SubmissionOut)
def get_submission(submission_id: str, db: Session = Depends(get_db)):
    sub = db.get(Submission, submission_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Not found. Crawl it first.")
    return _serialize_submission(sub)


@app.get("/api/submissions")
def list_submissions(
    subreddit: str | None = None,
    page: int = 1,
    page_size: int = 10,
    sort: str = "newest",
    db: Session = Depends(get_db),
):
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 10

    q = db.query(Submission)
    if subreddit:
        q = q.filter(Submission.subreddit == subreddit)

    if sort == "upvotes":
        q = q.order_by(Submission.score.desc())
    elif sort == "comments":
        q = q.order_by(Submission.num_comments.desc())
    else:
        q = q.order_by(Submission.crawled_at.desc())

    total = q.count()
    subs = q.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [_serialize_summary(s).model_dump() for s in subs],
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size,
        "sort": sort,
    }


# ---------- Direct subreddit batch endpoint ----------
# Kept available for API users and the analytics POC.
# Used by the subreddit page's "Crawl 50 more" button.

@app.post("/api/crawl-subreddit", response_model=list[SubmissionSummary])
def crawl_subreddit(req: SubredditCrawlRequest, db: Session = Depends(get_db)):
    if req.limit < 1 or req.limit > 100:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 100")
    try:
        subs = crawl_subreddit_batch(req.subreddit, req.limit, db)
    except NotFound:
        raise HTTPException(status_code=404, detail="Subreddit not found")
    except Forbidden:
        raise HTTPException(status_code=403, detail="Subreddit is private")
    except ResponseException as e:
        raise HTTPException(status_code=502, detail=f"Reddit API error: {e}")
    return [_serialize_summary(s) for s in subs]


# ---------- Bonus 1b: author history ----------

@app.post("/api/authors/{username}/fetch")
def fetch_author(username: str, db: Session = Depends(get_db)):
    """Fetch this author's recent comments from across Reddit."""
    try:
        count = fetch_author_history(username, db, limit=100)
    except NotFound:
        raise HTTPException(status_code=404, detail=f"Reddit user '{username}' not found")
    except Forbidden:
        raise HTTPException(status_code=403, detail="User profile is private or suspended")
    except ResponseException as e:
        raise HTTPException(status_code=502, detail=f"Reddit API error: {e}")
    return {"username": username, "fetched": count}


@app.get("/api/authors/{username}", response_model=AuthorOut)
def get_author(username: str, db: Session = Depends(get_db)):
    comments = (
        db.query(Comment, Submission)
        .join(Submission, Comment.submission_id == Submission.id)
        .filter(Comment.author == username)
        .order_by(Comment.created_utc.desc())
        .all()
    )

    if not comments:
        raise HTTPException(
            status_code=404,
            detail=f"No comments stored for u/{username}. Try clicking 'Fetch from Reddit' first.",
        )

    subreddits = sorted({s.subreddit for _, s in comments})
    author_row = db.get(Author, username)

    return AuthorOut(
        username=username,
        total_comments=len(comments),
        subreddits=subreddits,
        last_fetched_at=utc_to_sgt_iso(author_row.last_fetched_at) if author_row and author_row.last_fetched_at else None,
        comments=[
            CommentWithContext(
                id=c.id,
                body=c.body,
                score=c.score,
                created_sgt=utc_to_sgt_iso(c.created_utc),
                is_deleted=c.is_deleted,
                submission_id=s.id,
                submission_title=s.title,
                subreddit=s.subreddit,
            )
            for c, s in comments
        ],
    )


# ---------- Stats ----------

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    total_subs = db.query(func.count(Submission.id)).scalar()
    total_comments = db.query(func.count(Comment.id)).scalar()
    subreddits = db.query(func.count(func.distinct(Submission.subreddit))).scalar()
    authors = db.query(func.count(func.distinct(Comment.author))).scalar()
    return {
        "submissions": total_subs or 0,
        "comments": total_comments or 0,
        "subreddits": subreddits or 0,
        "unique_authors": authors or 0,
    }


# ---------- Static frontend ----------

app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def root():
    return FileResponse("frontend/index.html")


@app.get("/submission/{submission_id}")
def submission_page(submission_id: str):
    return FileResponse("frontend/submission.html")


@app.get("/author/{username}")
def author_page(username: str):
    return FileResponse("frontend/author.html")


@app.get("/subreddit/{name}")
def subreddit_page(name: str):
    return FileResponse("frontend/subreddit.html")