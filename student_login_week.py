from pymongo import MongoClient
from datetime import datetime

# MongoDB Configuration
SOURCE_DB = "hylab"
SOURCE_COLLECTION_LOGS = "log_login"
SOURCE_COLLECTION_WEEKS = "course_week"
TARGET_DB = "hylab"
TARGET_COLLECTION = "student_week_logs"

# MongoDB Connection
client = MongoClient("mongodb://hylab:hlbTuy4m!1@database2.pptik.id/?authMechanism=DEFAULT&authSource=hylab")
source_db = client[SOURCE_DB]
target_db = client[TARGET_DB]

def get_course_weeks():
    """
    Load course weeks from the MongoDB collection.
    """
    course_week_data = list(source_db[SOURCE_COLLECTION_WEEKS].find({}))
    for week in course_week_data:
        week["firstday"] = datetime.strptime(week["firstday"], "%A, %B %d, %Y")
        week["lastday"] = datetime.strptime(week["lastday"], "%A, %B %d, %Y")
    return course_week_data

def determine_week(log_date, course_weeks):
    """
    Determine the week based on the log_date and course_week date ranges.
    """
    log_date = datetime.strptime(log_date, "%m/%d/%Y")  # Convert string to datetime
    for week in course_weeks:
        if week["firstday"] <= log_date <= week["lastday"]:
            return week["week"]
    return None

def process_log_data(course_weeks):
    """
    Process log_login data to match each log with the corresponding week.
    """
    logs = source_db[SOURCE_COLLECTION_LOGS].find({})
    processed_logs = []
    for log in logs:
        week = determine_week(log["log_datecreated"], course_weeks)
        if week:
            processed_logs.append({
                "username": log["username"],
                "action": log["log_action"],
                "week": week,
                "date": log["log_datecreated"],
                "time": log["log_timecreated"]
            })
    return processed_logs

def save_to_target_db(data):
    """
    Save processed data to the target MongoDB collection.
    """
    target_collection = target_db[TARGET_COLLECTION]
    target_collection.insert_many(data)
    print(f"Successfully saved {len(data)} records to the target database.")

if __name__ == "__main__":
    # Step 1: Get course weeks
    course_weeks = get_course_weeks()

    # Step 2: Process log data
    processed_logs = process_log_data(course_weeks)

    # Step 3: Save to target database
    save_to_target_db(processed_logs)
