from typing import Optional, List
from pydantic import BaseModel


class CommentOut(BaseModel):
    id: str
    parent_id: Optional[str]
    author: Optional[str]
    body: Optional[str]
    score: int
    created_sgt: str
    is_deleted: bool


class SubmissionOut(BaseModel):
    id: str
    title: str
    author: Optional[str]
    subreddit: str
    selftext: Optional[str]
    url: str
    score: int
    num_comments: int
    created_sgt: str
    comments: List[CommentOut]


class SubmissionSummary(BaseModel):
    id: str
    title: str
    subreddit: str
    author: str | None
    score: int
    num_comments: int
    created_sgt: str
    crawled_at_sgt: str


class CommentWithContext(BaseModel):
    id: str
    body: Optional[str]
    score: int
    created_sgt: str
    is_deleted: bool
    submission_id: str
    submission_title: str
    subreddit: str


class AuthorOut(BaseModel):
    username: str
    total_comments: int
    subreddits: List[str]
    last_fetched_at: Optional[str]
    comments: List[CommentWithContext]


class CrawlRequest(BaseModel):
    url: str


class SubredditCrawlRequest(BaseModel):
    subreddit: str
    limit: int = 50

