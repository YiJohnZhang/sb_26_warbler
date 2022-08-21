"""Seed database with sample data from CSV Files."""

from csv import DictReader
from app import db
from models import User, Message, Follows


db.drop_all()
db.create_all()

with open('generator/users.csv') as users:
    db.session.bulk_insert_mappings(User, DictReader(users))

with open('generator/messages.csv') as messages:
    db.session.bulk_insert_mappings(Message, DictReader(messages))

with open('generator/follows.csv') as follows:
    db.session.bulk_insert_mappings(Follows, DictReader(follows))

db.session.commit()

# DISREGARD:
# because I can get all the followers as a property so there is no need to query!
# Use Instructions:
#   1. Run `generator/create_csvs.py`.
#   2. Run `generator/sortFoillowsHelper.py`.
#   3. Paste `user_followers_followedBy_noSQL.csv` contents into `users.csv`.
    # Recreated as `users_nosql.csv`
    # `user_followers_followedBy_noSQL.csv` uses semicolon delimiters because it contains arrays.

    # 1 GB is the longest string length for PSQL. BIGINT goes upto 1E18 (19 characters). A legible array has 2 characters of overhead for each entry: `[]` for the 1st and `, ` for the nth after the 1st.
        # therefore each entry, at worst case is 21 chars.
        # UTF-8 standard is 1 byte / character for the basic 128. Therefore Each entry takes 21 bytes.
        # therefore each string may hold a minimum of 47.6 mn entries, legibly. 50 mn - 1 if space-condensed. 50 mn if cheaped out on `[]`
        # theoretically could just 1-to-many rel. the entry strings
    # set data type of `user_follows` and `user_followers` to Text.
