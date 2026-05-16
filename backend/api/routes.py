from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from prawcore.exceptions import NotFound, Forbidden, ResponseException

from backend.database import engine, Base, get_db
from backend.db.models import Submission, Comment
from backend.crawler.service import crawl_submission, crawl_subreddit_batch
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

app = FastAPI(title="Reddit Crawler", version="0.2.0")


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
    )


# ---------- Core: single submission ----------

@app.post("/api/crawl", response_model=SubmissionOut)
def crawl(req: CrawlRequest, db: Session = Depends(get_db)):
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
    return _serialize_submission(sub)


@app.get("/api/submissions/{submission_id}", response_model=SubmissionOut)
def get_submission(submission_id: str, db: Session = Depends(get_db)):
    sub = db.get(Submission, submission_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Not found. Crawl it first.")
    return _serialize_submission(sub)


@app.get("/api/submissions", response_model=list[SubmissionSummary])
def list_submissions(
    subreddit: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Submission)
    if subreddit:
        q = q.filter(Submission.subreddit == subreddit)
    subs = q.order_by(Submission.crawled_at.desc()).all()
    return [_serialize_summary(s) for s in subs]


# ---------- Bonus 1a: subreddit batch crawl ----------

@app.post("/api/crawl-subreddit", response_model=list[SubmissionSummary])
def crawl_subreddit(req: SubredditCrawlRequest, db: Session = Depends(get_db)):
    if req.limit < 1 or req.limit > 100:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 100")
    subs = crawl_subreddit_batch(req.subreddit, req.limit, db)
    return [_serialize_summary(s) for s in subs]


# ---------- Bonus 1b: author history ----------

@app.get("/api/authors/{username}", response_model=AuthorOut)
def get_author(username: str, db: Session = Depends(get_db)):
    # Find all comments by this author
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
            detail=f"No comments found for user '{username}' in our database.",
        )

    subreddits = sorted({s.subreddit for _, s in comments})

    return AuthorOut(
        username=username,
        total_comments=len(comments),
        subreddits=subreddits,
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


# ---------- Stats for homepage ----------

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