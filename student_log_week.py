from pymongo import MongoClient
from datetime import datetime

# MongoDB Configuration
SOURCE_DB = "hylab"
LOG_COLLECTION = "course_log"
WEEK_COLLECTION = "course_week"
TARGET_DB = "hylab"
TARGET_COLLECTION = "student_activity_week"

# MongoDB Connection
client = MongoClient("mongodb://hylab:hlbTuy4m!1@database2.pptik.id/?authMechanism=DEFAULT&authSource=hylab")
source_db = client[SOURCE_DB]
target_db = client[TARGET_DB]

def get_course_weeks():
    """
    Load course weeks from the MongoDB collection.
    Convert firstday and lastday fields to datetime objects.
    """
    course_weeks = list(source_db[WEEK_COLLECTION].find({}))
    for week in course_weeks:
        week["firstday"] = datetime.strptime(week["firstday"], "%A, %B %d, %Y")
        week["lastday"] = datetime.strptime(week["lastday"], "%A, %B %d, %Y")
    return course_weeks

def determine_week(activity_date, course_weeks):
    """
    Determine the week based on the activity_date and course_week date ranges.
    """
    activity_date = datetime.strptime(activity_date, "%d/%m/%y, %H:%M")  # Convert string to datetime
    for week in course_weeks:
        if week["firstday"] <= activity_date <= week["lastday"]:
            return week["week"]
    return None

def process_course_log(course_weeks):
    """
    Process course_log data to match each activity with the corresponding week.
    """
    course_logs = source_db[LOG_COLLECTION].find({})
    processed_activities = []

    for log in course_logs:
        activity_week = determine_week(log["Time"], course_weeks)  # Function that determines the week
        if activity_week:
            processed_activities.append({
                "user": log.get("username", "Unknown"),  # Use .get() to handle missing keys
                "activity": log["Event name"],
                "course": log["Event context"],
                "component": log["Component"],
                "week": activity_week,
                "time": log["Time"],
                "description": log.get("Description", ""),
                "ip_address": log.get("IP address", ""),
            })

    return processed_activities

def save_to_target_db(data):
    """
    Save processed data to the target MongoDB collection.
    """
    target_collection = target_db[TARGET_COLLECTION]
    if data:
        target_collection.insert_many(data)
        print(f"Successfully saved {len(data)} records to the target database.")
    else:
        print("No records to save.")

if __name__ == "__main__":
    # Step 1: Get course weeks
    course_weeks = get_course_weeks()

    # Step 2: Process course logs
    processed_logs = process_course_log(course_weeks)

    # Step 3: Save to target database
    save_to_target_db(processed_logs)
