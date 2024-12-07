import pandas as pd
from pymongo import MongoClient

# MongoDB Configuration
MONGO_URI = "mongodb://hylab:hlbTuy4m!1@database2.pptik.id/?authMechanism=DEFAULT&authSource=hylab"
DATABASE_NAME = "hylab"
COLLECTION_NAME = "users"

def upload_csv_to_mongodb(csv_file_path):
    """
    Uploads a CSV file to MongoDB.
    
    Args:
        csv_file_path (str): The path to the CSV file.
    """
    try:
        # 1. Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file_path)
        print(f"CSV file '{csv_file_path}' loaded successfully.")

        # 2. Convert DataFrame to a list of dictionaries
        data = df.to_dict(orient="records")
        print(f"Converted CSV data to dictionary format. Total records: {len(data)}")

        # 3. Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        # 4. Insert data into MongoDB
        result = collection.insert_many(data)
        print(f"Successfully inserted {len(result.inserted_ids)} records into MongoDB collection '{COLLECTION_NAME}'.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Replace with the plath to your CSV file
    csv_file_path = "D:/labwork/hylab/Users.csv"
    upload_csv_to_mongodb(csv_file_path)
