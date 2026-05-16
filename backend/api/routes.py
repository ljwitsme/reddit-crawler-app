from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from prawcore.exceptions import NotFound, Forbidden, ResponseException

from backend.database import engine, Base, get_db
from backend.db.models import Submission
from backend.crawler.service import crawl_submission
from backend.utils.timezone import utc_to_sgt_iso
from backend.api.schemas import (
    CrawlRequest,
    SubmissionOut,
    CommentOut,
    SubmissionSummary,
)

# Auto-create tables on startup (idempotent)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Reddit Crawler", version="0.1.0")


def _serialize(sub: Submission) -> SubmissionOut:
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
    return _serialize(sub)


@app.get("/api/submissions/{submission_id}", response_model=SubmissionOut)
def get_submission(submission_id: str, db: Session = Depends(get_db)):
    sub = db.get(Submission, submission_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Not found. Crawl it first.")
    return _serialize(sub)


@app.get("/api/submissions", response_model=list[SubmissionSummary])
def list_submissions(db: Session = Depends(get_db)):
    subs = db.query(Submission).order_by(Submission.crawled_at.desc()).all()
    return [
        SubmissionSummary(
            id=s.id, title=s.title, subreddit=s.subreddit, num_comments=s.num_comments
        )
        for s in subs
    ]


# Static frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def root():
    return FileResponse("frontend/index.html")