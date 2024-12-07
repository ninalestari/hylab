import requests
import json
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import pymongo
from datetime import datetime, timezone, timedelta
import csv
import os
import pytz

# Create a session object for Siakad API
siakad_session = requests.Session()
siakad_retries = Retry(total=5, backoff_factor=0.1,
                       status_forcelist=[500, 502, 503, 504])
siakad_session.mount('https://', HTTPAdapter(max_retries=siakad_retries))

# Create a session object for Moodle API
moodle_session = requests.Session()
moodle_retries = Retry(total=5, backoff_factor=0.1,
                       status_forcelist=[500, 502, 503, 504])
moodle_session.mount('https://', HTTPAdapter(max_retries=moodle_retries))


# siakad_API
url = 'https://api.sevimaplatform.com/siakadcloud/v1/dosen'
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-App-Key': '11459983A63B0DEADD7C2A7D45BF6000',
    'X-Secret-Key': '3D9337C5320EEF78EAA0026BCF67F7BF5953EC0B575050008BFD1155B0BAA95F'
}
#moodle API

base_url_moodle = "https://kuliahonline.usbypkp.ac.id/webservice/rest/server.php"
api_key = "2f1479d06cb564961bbc56a2c5a2a0f7"

#base_url_moodle = "https://lms.pptik.id/webservice/rest/server.php"
#api_key = "6c5b3c6a8d87906050f61b8dbd476a4f"

current_date = datetime.now()
print(current_date)
tahun_akademik = current_date.year
current_month = current_date.month
if current_month >1 and current_month < 6:
    semester = '2'
    periode_akademik = str(tahun_akademik-1)+str(semester)
else:
    if current_month >6 and current_month < 9:
        semester = '1'
        periode_akademik = str(tahun_akademik)+str(semester)
    else:
        semester = '3'
        periode_akademik = str(tahun_akademik-1)+str(semester)

print(f"Periode Akademik: {periode_akademik}")

def fetch_siakad_data(page):
    params = {"page": page}
    response = siakad_session.get(url, headers=headers, params=params)
    #print (response.json())
    return response.json()
fetch_siakad_data(1)

def get_course_id():
    # Parameters for the web service call
    params = {
        'wstoken': api_key,
        'wsfunction': 'core_course_get_courses',
        'moodlewsrestformat': 'json'
    }
    # Make the web service call
    response = requests.get(base_url_moodle, params=params)
    results = []
    # Check the response status
    if response.status_code == 200:
        try:
            # Parse the JSON response
            courses = response.json()
            print(courses)

            # Check if the response is a list
            if isinstance(courses, list):
                # Print course information
                for course in courses:
                    #print(f"ID: {course['id']}, Course Name: {course['fullname']}")#, Short Name: {course['shortname']}")
                    result = (course['id'], course['fullname'])
                    results.append(result)
                    result_array = result
            else:
                print("Unexpected response format:", courses)
        except ValueError as e:
            print("Error parsing JSON response:", e)
    else:
        print(f"Failed to fetch courses. HTTP Status Code: {response.status_code}")
        print("Response content:", response.text)
    return results

def get_section_id(course_id):
    #print ("course_id:", course_id)
    # Parameters for the web service call
    params = {
        'wstoken': api_key,
        'wsfunction': 'core_course_get_contents',
        'moodlewsrestformat': 'json',
        'courseid': course_id
    }

    # Make the web service call
    response = requests.get(base_url_moodle, params=params)

    # Check the response status
    if response.status_code == 200:
        results = []
        try:
            # Parse the JSON response
            sections = response.json()
            #print(sections)
            # Print section details
            for section in sections:
                if isinstance(section, dict):
                    print(f"Topic: {section['name']}")
                    for module in section.get('modules', []):
                        print(f"  Activity: {module['name']}, {module['modname']}")
                        if module['modname'] == 'quiz':
                            attemp = json.loads(module['customdata'])
                            timeopen = attemp['timeopen']
                            timeclose = attemp['timeclose']
                            dt_open = datetime.utcfromtimestamp(int(timeopen))
                            str_timeopen = dt_open.strftime('%Y-%m-%d %H:%M:%S')
                            dt_close= datetime.utcfromtimestamp(int(timeclose))
                            str_timeclose = dt_close.strftime('%Y-%m-%d %H:%M:%S')
                            print(f"    Timeopen: {str_timeopen}")
                            print(f"    Timeclose: {str_timeclose}")
                        result = (section['name'],module['name'])
                        results.append(result)
                        result_array = result
                else:
                    print(f"Unexpected section format: {section}")
        except ValueError as e:
            print("Error parsing JSON response:", e)
    else:
        print(f"Failed to fetch course contents. HTTP Status Code: {response.status_code}")
        print("Response content:", response.text)
    return results

def get_teacher_id(course_id):
    # Parameters for the web service call
    params = {
        'wstoken': api_key,
        'wsfunction': 'core_enrol_get_enrolled_users',
        'moodlewsrestformat': 'json',
        'courseid': course_id
    }

    # Make the web service call
    response = requests.get(base_url_moodle, params=params)

    # Check the response status
    if response.status_code == 200:
        try:
            # Parse the JSON response
            users = response.json()

            # Debug print to check the structure of users
            #print("Response JSON:", users)

            # Check if the response is a list of users
            if isinstance(users, list):
                # Print user information
                for user in users:
                    # Check if roles list is not empty and get the first roleid
                    if user['roles']:
                        roleid = user['roles'][0]['roleid']
                        role = "teacher" if roleid == 3 else f"roleid: {roleid}"
                    else:
                        role = "No roles assigned"
                    if role == "teacher":
                        print(f"Teacher: {user['fullname']}")
                    
            else:
                print("Unexpected response format:", users)
        except ValueError as e:
            print("Error parsing JSON response:", e)
    else:
        print(f"Failed to fetch enrolled users. HTTP Status Code: {response.status_code}")
        print("Response content:", response.text)

get_teacher_id(15497)
get_section_id(15497)

'''
# Fetch and print course IDs and details
result_array = get_course_id()
#print (result_array)
for i in result_array:
    course_name = (i[1])
        
    id = (i[0])
    if id > 14975:
        print ("Course:",course_name)
        # Fetch and print section IDs and details
        get_teacher_id(id)
        get_section_id(id)
        # Fetch and print teacher IDs and details
''' 
