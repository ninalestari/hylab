import os
import pymongo
from dotenv import load_dotenv

load_dotenv(".env")

def DbConnection():
    db = os.environ.get("MONGODB")
    myclient = pymongo.MongoClient(db)
    db = myclient["hylab"]
    collection_log = db["log"]
    collection_report = db["datahasils"]
    return collection_report, collection_log
