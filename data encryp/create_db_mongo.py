# create_db_mongo.py
from pymongo import MongoClient, ASCENDING
import sys

client = MongoClient("mongodb://localhost:27017")
db = client.appEncryption

try:
    db.users.create_index([("username", ASCENDING)], unique=True)
    db.users.create_index([("email", ASCENDING)], unique=True)
    db.uploads.create_index([("user_id", ASCENDING)])
    db.biometrics.create_index([("user_id", ASCENDING)], unique=True)
    print("✅ Indexes and collections ensured (users, uploads, biometrics).")
except Exception as e:
    print("❌ Error creating indexes or collections:", e)
    sys.exit(1)
