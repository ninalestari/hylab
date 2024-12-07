import requests
import os
from dotenv import load_dotenv

MOODLE_URL = os.environ.get("MOODLE_URL")
MOODLE_TOKEN = os.environ.get("MOODLE_TOKEN")

def get_user_by_field(field, value):
    url = f"{MOODLE_URL}/webservice/rest/server.php"
    params = {
        'wstoken': MOODLE_TOKEN,
        'wsfunction': 'core_user_get_users_by_field',
        'moodlewsrestformat': 'json',
        'field': field,
        'values[0]': value
    }
    response = requests.get(url, params=params)
    return response.json()

def login_to_moodle(username):
    user = get_user_by_field('username', username)
    if user:
        print(f"User {username} logged in successfully.")
    else:
        print(f"User {username} not found in Moodle.")

login_to_moodle("ninalestari")

def get_user_details(username):
    """
    Fetch and display detailed information about a user.
    """
    user = get_user_by_field('username', username)
    if user:
        print("User Details:")
        for key, value in user.items():
            print(f"{key}: {value}")
    else:
        print(f"User {username} not found in Moodle.")

if __name__ == "__main__":
    # Replace with the username you want to fetch details for
    username_to_test = "ninalestari"
    get_user_details(username_to_test)