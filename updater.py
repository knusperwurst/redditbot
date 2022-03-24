from db import get_session
from db.models import Comment, Submission
from sqlalchemy import and_
import time
import threading
import config
import praw
import datetime
import logging

reddit = praw.Reddit(client_id=config.CLIENT_ID, client_secret=config.CLIENT_SECRET, user_agent=config.USER_AGENT)
subreddit = reddit.subreddit(config.SUBREDDIT)


def update():
    # Finalisiert Beiträge und Kommentare nach 24 Stunden und setzt den Finalen score ein

    db_session = get_session()
    query_time = datetime.datetime.now() - datetime.timedelta(hours=24)

    # Submissions abschließen
    for db_submission in db_session.query(Submission).filter(
            and_(Submission.datetime <= query_time, Submission.done == False)
    ):
        submission = reddit.submission(id=db_submission.submission_id)
        score = submission.score
        comments_count = submission.num_comments
        db_submission.comments_count = comments_count
        db_submission.score = score
        db_submission.done = True
        logging.info(f"Submission {db_submission.id} erfolgreich geupdated und geschlossen")
    db_session.commit()

    # comments abschließen
    for db_comment in db_session.query(Comment).filter(
            and_(Comment.datetime <= query_time, Comment.done == False)
    ):
        comment = reddit.comment(id=db_comment.comment_id)
        score = comment.score
        edited = comment.edited
        db_comment.score = score
        db_comment.edited = True if edited is not None else False
        db_comment.done = True
        logging.info(f"Comment {db_comment.id} erfolgreich geupdated und geschlossen")
    db_session.commit()
    db_session.close()


class Updater(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        running = True
        while running:
            try:
                time.sleep(60)
                update()
            except KeyboardInterrupt:
                logging.info("Keyboardinterrupt - schalte aus")
                running = False
            except Exception as e:
                logging.exception(e)
                time.sleep(10)
