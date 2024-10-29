import sqlite3
import csv
import os
import requests
import reverse_geocode
from collections import Counter

def send_file_to_telegram_bot(file_path):
    telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    telegram_channel_id = os.environ.get('TELEGRAM_CHANNEL_ID')
    
    url = f'https://api.telegram.org/bot{telegram_bot_token}/sendDocument'

    with open(file_path, 'rb') as file:
        files = {'document': file}
        params = {'chat_id': telegram_channel_id}
        response = requests.post(url, files=files, params=params)

    if response.status_code == 200:
        print('File uploaded successfully.')
        return True
    else:
        print(f'Failed to upload file. Status code: {response.status_code}')
        print(response.text)
        return False

def send_to_telegram(message):
    telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    telegram_channel_id = os.environ.get('TELEGRAM_CHANNEL_ID')

    api_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    params = {'chat_id': telegram_channel_id, 'text': message}
    response = requests.post(api_url, params=params)

    if response.status_code == 200:
        print("Message sent to Telegram successfully.")
    else:
        print(f"Failed to send message to Telegram. Status code: {response.status_code}")

# Connect to the database
conn = sqlite3.connect('location_data.db')
cursor = conn.cursor()

# Create locations table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS locations (
        title TEXT,
        lng REAL,
        lat REAL,
        PRIMARY KEY (lng, lat)
    )
''')

# Read today's POIs
today_pois = set()
with open('POIdb.csv', 'r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        today_pois.add((row['title'], float(row['lng']), float(row['lat'])))
        cursor.execute('INSERT OR IGNORE INTO locations (title, lng, lat) VALUES (?, ?, ?)', (row['title'], float(row['lng']), float(row['lat'])))

conn.commit()

# Read yesterday's POIs
yesterday_pois = set()
with open('dailycheck.csv', 'r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        yesterday_pois.add((row['title'], float(row['lng']), float(row['lat'])))

# Compare POIs to find new ones
new_pois = today_pois - yesterday_pois
country_counter = Counter()

# Write new POIs to add.csv, including country information
with open('add.csv', 'w', encoding='utf-8', newline='') as add_file:
    fieldnames = ['title', 'lng', 'lat', 'country']  # Add 'country' to fieldnames
    csv_writer_add = csv.DictWriter(add_file, fieldnames=fieldnames)
    csv_writer_add.writeheader()

    for poi in new_pois:
        title, lng, lat = poi
        
        # Reverse geocode to get country information
        location_info = reverse_geocode.get((lat, lng))
        country = location_info['country']  # Get country from location info
        
        # Write POI and country to add.csv
        csv_writer_add.writerow({'title': title, 'lng': lng, 'lat': lat, 'country': country})

        # Count occurrences of countries
        country_counter[country] += 1

# Compare POIs to find lost ones
lost_pois = yesterday_pois - today_pois
lost_counter = len(lost_pois)  # Count the number of lost POIs

# Write lost POIs to lost.csv
with open('lost.csv', 'w', encoding='utf-8', newline='') as lost_file:
    csv_writer_lost = csv.DictWriter(lost_file, fieldnames=['title', 'lng', 'lat'])
    csv_writer_lost.writeheader()

    for poi in lost_pois:
        title, lng, lat = poi
        csv_writer_lost.writerow({'title': title, 'lng': lng, 'lat': lat})

conn.close()

# Send lost POIs count to Telegram
send_to_telegram(f"In the past 24 hours, {lost_counter} portals lost their OC ability.")

# Send country statistics to Telegram
if country_counter:
    country_message = "Countries with new OC-Portal:\n"
    for country, count in country_counter.most_common():
        if country == "China":
            country_message += f"Chinese mainland: {count}\n"
        else:
            country_message += f"{country}: {count}\n"
    country_message+="Visit https://ingress-wiki.github.io/OverClocking-Map/new to check new oc portal on the map"
    send_to_telegram(country_message)

# Send the add and lost files to Telegram
send_file_to_telegram_bot("./add.csv")
send_file_to_telegram_bot("./lost.csv")
