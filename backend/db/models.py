from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean, Index
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import relationship
from backend.database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String(20), primary_key=True)
    title = Column(Text, nullable=False)
    author = Column(String(255), nullable=True)
    subreddit = Column(String(255), nullable=False, index=True)
    selftext = Column(MEDIUMTEXT, nullable=True)
    url = Column(Text, nullable=False)
    score = Column(Integer, default=0)
    num_comments = Column(Integer, default=0)
    created_utc = Column(DateTime, nullable=False, index=True)
    crawled_at = Column(DateTime, nullable=False)

    comments = relationship(
        "Comment",
        back_populates="submission",
        cascade="all, delete-orphan",
    )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(String(20), primary_key=True)
    submission_id = Column(String(20), ForeignKey("submissions.id"), nullable=False, index=True)
    parent_id = Column(String(20), nullable=True, index=True)
    author = Column(String(255), nullable=True, index=True)
    body = Column(MEDIUMTEXT, nullable=True)
    score = Column(Integer, default=0)
    created_utc = Column(DateTime, nullable=False)
    is_deleted = Column(Boolean, default=False)

    submission = relationship("Submission", back_populates="comments")

    __table_args__ = (
        Index("ix_comments_submission_parent", "submission_id", "parent_id"),
    )