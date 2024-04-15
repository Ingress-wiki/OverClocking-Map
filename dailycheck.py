import sqlite3
import csv
import os
import requests

def send_file_to_telegram_bot(file_path):
    telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    telegram_channel_id = os.environ.get('TELEGRAM_CHANNEL_ID')
    """
    Uploads a file to Telegram Bot and sends it to the specified chat.

    Parameters:
        bot_token (str): Telegram Bot API token.
        chat_id (str): Chat ID where you want to send the file.
        file_path (str): Path to the file you want to upload.

    Returns:
        bool: True if the file was successfully uploaded and sent, False otherwise.
    """
    # URL for sending files
    url = f'https://api.telegram.org/bot{telegram_bot_token}/sendDocument'

    # Open the file
    with open(file_path, 'rb') as file:
        # Prepare the request parameters
        files = {'document': file}
        params = {'chat_id': telegram_channel_id}

        # Send the request
        response = requests.post(url, files=files, params=params)

    # Check the response
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

    message = f"{message}"
    api_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"

    params = {
        'chat_id': telegram_channel_id,
        'text': message
    }
    response = requests.post(api_url, params=params)
    if response.status_code == 200:
        print("Counter sent to Telegram successfully.")
    else:
        print(f"Failed to send counter to Telegram. Status code: {response.status_code}")

conn = sqlite3.connect('location_data.db')
cursor = conn.cursor()
Counter = 0
cursor.execute('''
    CREATE TABLE IF NOT EXISTS locations (
        title TEXT,
        lng REAL,
        lat REAL,
        PRIMARY KEY (lng, lat)
    )
''')

with open('POIdb.csv', 'r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        cursor.execute('INSERT OR IGNORE INTO locations (title, lng, lat) VALUES (?, ?, ?)', (row['title'], float(row['lng']), float(row['lat'])))

conn.commit()

with open('dailycheck.csv', 'r', encoding='utf-8') as input_file, open('lost.csv', 'w', encoding='utf-8', newline='') as output_file:
    csv_reader = csv.DictReader(input_file)
    csv_writer = csv.DictWriter(output_file, fieldnames=csv_reader.fieldnames)
    csv_writer.writeheader()

    for row in csv_reader:
        lng_value = row.get('lng')
        lat_value = row.get('lat')

        if lng_value is not None and lat_value is not None:
            lng_float = float(lng_value)
            lat_float = float(lat_value)

            cursor.execute('SELECT * FROM locations WHERE lng = ? AND lat = ?', (lng_float, lat_float))
            result = cursor.fetchone()

            if result is None:
                csv_writer.writerow(row)
                Counter += 1
        else:
            print("Warning: 'lng' or 'lat' value is None in input file. Skipping row.")
conn.close()
send_to_telegram("In the past 24 hours, "+ str(Counter)+" portals lost their OC ability.")
send_file_to_telegram_bot("./lost.csv")
