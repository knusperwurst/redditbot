import logging

from updater import Updater
from streamer import CommentStreamer, SubmissionStreamer
from db import create_db

if __name__ == "__main__":
    create_db()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s -> %(message)s")
comment_streamer_thread = CommentStreamer()
comment_streamer_thread.start()

submission_streamer_thread = SubmissionStreamer()
submission_streamer_thread.start()

updater_thread = Updater()
updater_thread.start()

comment_streamer_thread.join()
submission_streamer_thread.join()
updater_thread.join()


