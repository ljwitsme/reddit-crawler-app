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
    num_comments: int


class CrawlRequest(BaseModel):
    url: str