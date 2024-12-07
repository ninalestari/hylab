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
url = 'https://api.sevimaplatform.com/siakadcloud/v1/perkuliahan'
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-App-Key': '11459983A63B0DEADD7C2A7D45BF6000',
    'X-Secret-Key': '3D9337C5320EEF78EAA0026BCF67F7BF5953EC0B575050008BFD1155B0BAA95F'
}

def fetch_siakad_data (page):
    params = {"f-id_periode": 20232, "f-id_program_studi": 20201,"page": page}
    response = siakad_session.get(url, headers=headers, params=params)
    #print(response.json())
    return response.json()
    
fetch_siakad_data(1)

def perkuliahan (page):
    results = []
    response_data = fetch_siakad_data(1)
    if "meta" not in response_data or "last_page" not in response_data["meta"]:
        print("Meta data or last_page not found in the response. Skipping...")
        exit()
    max_pages = response_data["meta"]["last_page"]
    start_page = 1
    #print (max_pages)
    for page in range (1, max_pages+1):
        siakad_data = fetch_siakad_data(page)
        if 'data' not in siakad_data:
            print(f"No data found for page {page}. Exiting loop.")
            continue
       #print(f"fetching page {page} of {max_pages}")
        for perkuliahan in siakad_data['data']:
            perkuliahan_details = perkuliahan['attributes'] 
            prodi = perkuliahan_details ['id_program_studi']     
            periode = perkuliahan_details['id_periode'] 
            id_kelas = perkuliahan_details ['id_kelas']
            kode_mata_kuliah = perkuliahan_details['kode_mata_kuliah']
            mata_kuliah = perkuliahan_details ['mata_kuliah']
            nomor_pertemuan = perkuliahan_details['nomor_pertemuan']
            tanggal = perkuliahan_details ['tanggal']
            waktu_mulai = perkuliahan_details ['waktu_mulai']
            waktu_diselesaikan = perkuliahan_details ['waktu_diselesaikan'].split("T")
            if len(waktu_diselesaikan) > 1:
                waktu_selesai = waktu_diselesaikan[1].split('.')[0]
            else:
                waktu_selesai = '-'
            rps_mingguan = perkuliahan_details['rencana_materi']
            realisasi_mingguan = perkuliahan_details['bahasan']
            if id_kelas == 46153:
                result = (periode, prodi,  kode_mata_kuliah, mata_kuliah, nomor_pertemuan, tanggal, waktu_mulai, waktu_selesai, rps_mingguan, realisasi_mingguan)
                results.append(result)
                result_array = result
                print (f"Realisasi materi:{result_array[4]} - {result_array[9]}")
                
        time.sleep (5)
    return results

#results_array = perkuliahan(1)
'''
csv_directory = "D:/PROJECT/"
prodi = "20201"
periode = "20222"
dt = datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%Y%m%d%H%M%S")
csv_file_path = os.path.join(csv_directory, f"Data perkuliahan {prodi}_{periode}_{dt}.csv")
# Write results to the CSV file when quitting
try:
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Periode", "KOde Prodi", "Kode Mata Kuliah","Nama Mata Kuliah", "Pertemuan", 'Tanggal', "Waktu Mulai","Waktu Selesai", "Rencana", "Pembahasan"])
        writer.writerows(results_array)
        print(f"Saved recognition results to {csv_file_path}")
except PermissionError as e:
    print(f"Failed to write file due to permission error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
'''