from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:28018/")

client = MongoClient(MONGO_URI)
db = client["appointment_scheduling_db"]
appointments = db["appointments"]

result = appointments.delete_many({})

print(f"Deleted {result.deleted_count} appointment(s).")