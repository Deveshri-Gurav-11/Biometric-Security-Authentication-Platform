# delete_data_mongo.py
from pymongo import MongoClient

# Connect to your MongoDB (same as in app_mongo.py)
client = MongoClient("mongodb://localhost:27017")
db = client.appEncryption

print("⚠️  WARNING: This will permanently delete ALL data from the database!")
confirm = input("Type 'YES' to continue: ")

if confirm == "YES":
    try:
        db.users.delete_many({})
        db.uploads.delete_many({})
        db.biometrics.delete_many({})
        print("✅ SUCCESS: All collections (users, uploads, biometrics) have been cleared.")
    except Exception as e:
        print("❌ ERROR while deleting data:", e)
else:
    print("❌ Operation cancelled. No data deleted.")
