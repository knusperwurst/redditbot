from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
import datetime

from . import Base


class Redditor(Base):
    __tablename__ = "redditor"

    id = Column(Integer, primary_key=True)
    redditor_id = Column(String(20), nullable=False)
    redditor_name = Column(String(20), nullable=False)
    uploads = Column(Integer, nullable=False)
    comments_count = Column(Integer, nullable=False)
    submission = relationship("Submission", backref="redditor")
    comments = relationship("Comment", backref="redditor")


class Submission(Base):
    __tablename__ = "submission"

    id = Column(Integer, primary_key=True)
    submission_id = Column(String(20), nullable=False)
    score = Column(Integer, nullable=False)
    created = Column(Integer, nullable=False)
    datetime = Column(DateTime, default=datetime.datetime.now)
    url = Column(String(2048), nullable=False)
    done = Column(Boolean, nullable=False)
    comments_count = Column(Integer, nullable=False)
    author_id = Column(Integer, ForeignKey("redditor.id"), nullable=False)


class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True)
    comment_id = Column(String(16), nullable=False)
    permalink = Column(String(2048), nullable=False)
    score = Column(Integer, nullable=False)
    edited = Column(Boolean, nullable=False)
    datetime = Column(DateTime, default=datetime.datetime.now)
    done = Column(Boolean, nullable=False)
    author_id = Column(Integer, ForeignKey("redditor.id"), nullable=False)
    comment_body = relationship("CommentBody", backref="comment", uselist=False)


class CommentBody(Base):
    __tablename__ = "comment_body"

    id = Column(Integer, primary_key=True)
    body = Column(Text, nullable=False)
    comment_id = Column(Integer, ForeignKey("comment.id"))
