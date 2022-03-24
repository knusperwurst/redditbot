from sqlalchemy.orm import joinedload
from db import get_session
from collections import Counter
from db.models import Comment, Submission
from sqlalchemy import and_
import datetime
import csv
import config


def top_word_counter(top_counter, db_session, end_date, start_date):
    word_blacklist = blacklist_loader()
    res = db_session.query(Comment).options(
        joinedload(Comment.comment_body),
        joinedload(Comment.redditor)).filter(
        and_(Comment.datetime >= start_date, Comment.datetime <= end_date, Comment.done == True)
    )
    filtered_words = []
    for comment in res:
        if comment.redditor.redditor_name == "AutoModerator":
            continue
        try:
            for word in comment.comment_body.body.split():
                if word.lower() not in word_blacklist:
                    filtered_words.append(word)
        except AttributeError:
            pass
    cnt = Counter()
    for word in filtered_words:
        cnt[word] += 1

    csv_writer(fieldnames=["wort", "anzahl"], filename="top_words.csv", data=cnt.most_common(top_counter))


def top_redditor_by_posts(top_counter, db_session, end_date, start_date):
    res = db_session.query(Submission).options(
        joinedload(Submission.redditor)).filter(
        and_(Submission.datetime >= start_date, Submission.datetime <= end_date, Submission.done == True)
    )
    cnt = Counter()
    for sub in res:
        cnt[sub.redditor.redditor_name] += 1
    csv_writer(filename="top_uploads_nummer.csv", fieldnames=["redditor", "anzahl"], data=cnt.most_common(top_counter))


def top_redditor_by_comments(top_counter, db_session, end_date, start_date):
    res = db_session.query(Comment).options(
        joinedload(Comment.redditor)).filter(
        and_(Comment.datetime >= start_date, Comment.datetime <= end_date, Comment.done == True)
    )
    cnt = Counter()
    for com in res:
        cnt[com.redditor.redditor_name] += 1
    csv_writer(filename="top_comments_nummer.csv", fieldnames=["redditor", "anzahl"], data=cnt.most_common(top_counter))


def top_posts(top_counter, db_session, end_date, start_date):
    res = db_session.query(Submission).options(
        joinedload(Submission.redditor)).filter(
        and_(Submission.datetime >= start_date, Submission.datetime <= end_date, Submission.done == True)
    ).order_by(Submission.score.desc()).limit(top_counter)

    fieldnames = ["redditor", "submission", "score", "link"]
    data = [(sub.redditor.redditor_name, sub.url, sub.score, f"https://www.reddit.com/r/{config.SUBREDDIT}/comments/{sub.submission_id}/{config.SUBREDDIT}/") for sub in res]
    csv_writer(fieldnames=fieldnames, filename="top_posts.csv", data=data)


def top_comments(top_counter, db_session, end_date, start_date):
    res = db_session.query(Comment).options(
        joinedload(Comment.redditor)).filter(
        and_(Comment.datetime >= start_date, Comment.datetime <= end_date, Comment.done == True)
    ).order_by(Comment.score.desc()).limit(top_counter)

    fieldnames = ["redditor", "comment", "score"]
    data = [(comment.redditor.redditor_name, comment.permalink, comment.score) for comment in res]
    csv_writer(fieldnames=fieldnames, filename="top_comments.csv", data=data)


def csv_writer(fieldnames, filename, data):
    with open(filename, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(fieldnames)
        for row in data:
            writer.writerow(row)


def blacklist_loader():
    word_blacklist = []
    try:
        with open("word_blacklist.txt", "r", encoding="utf-8") as word_file:
            for line in word_file.readlines():
                word_blacklist.append(line.rstrip().lower())
            print(f"{len(word_blacklist)} Wörter in der Blacklist")
    except FileNotFoundError:
        print("KEINE BLACKLIST VORHANDEN!")
    return word_blacklist


def analyze():
    days = 7
    top = 50
    db_session = get_session()
    end_date = datetime.datetime(2020, 10, 31)
    start_date = datetime.datetime(2020, 10, 1)
    # end_date = datetime.datetime.now()
    #start_date = end_date - datetime.timedelta(days=days)

    top_word_counter(top, db_session, end_date, start_date)
    top_redditor_by_posts(top, db_session, end_date, start_date)
    top_redditor_by_comments(top, db_session, end_date, start_date)
    top_posts(top, db_session, end_date, start_date)
    top_comments(top, db_session, end_date, start_date)

    db_session.close()


if __name__ == "__main__":
    analyze()
