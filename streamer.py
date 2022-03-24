import threading
import praw
import config
import logging
import time

from db import get_session
from db.models import Redditor, Comment, Submission, CommentBody

reddit = praw.Reddit(client_id=config.CLIENT_ID, client_secret=config.CLIENT_SECRET, user_agent=config.USER_AGENT)
subreddit = reddit.subreddit(config.SUBREDDIT)


def db_add_submission(submission):
    try:
        db_session = get_session()
        db_submission = db_session.query(Submission).filter_by(submission_id=submission.id).first()
        db_redditor = db_session.query(Redditor).filter_by(redditor_id=submission.author.id).first()
        if db_redditor is None:
            logging.critical("Submission vor Redditor angelegt")
            return
    except Exception as e:
        logging.critical(e)
        return
    if db_submission is None:
        try:
            db_submission = Submission()
            db_submission.submission_id = submission.id
            db_submission.score = submission.score
            db_submission.created = submission.created_utc
            db_submission.done = False
            db_submission.url = submission.url
            db_submission.comments_count = 0
            db_submission.redditor = db_redditor
            db_redditor.uploads += 1
            db_session.add(db_submission)
            db_session.commit()
        except Exception as e:
            logging.critical(e)
        logging.info(f"submission erstellt >{submission.id}<")

    else:
        logging.info(f"submission schon vorhanden >{submission.id}<")
    db_session.close()


def db_add_comment(comment):
    try:
        db_session = get_session()
        db_comment = db_session.query(Comment).filter_by(comment_id=comment.id).first()
        db_redditor = db_session.query(Redditor).filter_by(redditor_id=comment.author.id).first()
        if db_redditor is None:
            logging.critical("Comment vor Redditor angelegt")
            return
    except Exception as e:
        logging.critical(e)
        return
    if db_comment is None:
        try:
            db_comment = Comment()
            db_comment_body = CommentBody()

            db_comment.comment_id = comment.id
            db_comment.permalink = comment.permalink
            db_comment.score = 0
            db_comment.edited = False
            db_comment.done = False
            db_comment.redditor = db_redditor

            db_comment_body.body = comment.body
            db_comment.comment_body = db_comment_body

            db_redditor.comments_count += 1

            db_session.add(db_comment)
            db_session.commit()
        except Exception as e:
            print(e)
            logging.critical(e)
        logging.info(f"neuer comment angelegt >{comment.id}<")
    else:
        logging.info(f"comment gefunden >{comment.id}<")
    db_session.close()


def db_add_user(redditor):
    db_session = get_session()
    try:
        db_redditor = db_session.query(Redditor).filter_by(redditor_id=redditor.id).first()
    except Exception as e:
        logging.critical(e)
        return
    if db_redditor is None:
        try:
            db_redditor = Redditor()
            db_redditor.redditor_id = redditor.id
            db_redditor.redditor_name = redditor.name
            db_redditor.uploads = 0
            db_redditor.comments_count = 0
            db_session.add(db_redditor)
            db_session.commit()
        except Exception as e:
            logging.critical(e)
        logging.info(f"neuer User angelegt >{redditor.name}<")
    else:
        logging.info(f"user gefunden >{redditor.name}<")
    db_session.close()


class CommentStreamer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        running = True
        while running:
            try:
                for comment in subreddit.stream.comments():
                    db_add_user(comment.author)
                    db_add_comment(comment)
            except KeyboardInterrupt:
                logging.info("Keyboardinterrupt - schalte aus")
                running = False
            except Exception as e:
                logging.exception(e)
                time.sleep(10)


class SubmissionStreamer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        running = True
        while running:
            try:
                for submission in subreddit.stream.submissions():
                    db_add_user(submission.author)
                    db_add_submission(submission)
            except KeyboardInterrupt:
                logging.info("Keyboardinterrupt - schalte aus")
                running = False
            except Exception as e:
                logging.exception(e)
                time.sleep(10)
