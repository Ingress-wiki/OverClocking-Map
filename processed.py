import csv
from datetime import datetime
import requests

def send_counter_to_telegram(counter):
    telegram_bot_token = 'YOUR_TELEGRAM_BOT_TOKEN'
    telegram_channel_id = 'YOUR_TELEGRAM_CHANNEL_ID'

    message = f"Counter: {counter}"
    api_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"

    params = {
        'chat_id': telegram_channel_id,
        'text': message
    }
    print(api_url)
    response = requests.post(api_url, params=params)
    if response.status_code == 200:
        print("Counter sent to Telegram successfully.")
    else:
        print(f"Failed to send counter to Telegram. Status code: {response.status_code}")


file_path = 'POIsLightshipDevPortal.csv'
Counter = 0
with open(file_path, 'r') as infile:
    reader = csv.reader(infile)
    header = next(reader)

    columns_to_remove = ['id', 'img_uri', 'address', 'localizability']
    indices_to_remove = [header.index(col) for col in columns_to_remove if col in header]

    with open('POIdb.csv', 'w', newline='') as outfile, open('count.csv', 'a', newline='') as recordfile:
        writer = csv.writer(outfile)
        record_writer = csv.writer(recordfile)

        new_header = [col for col in header if col not in columns_to_remove]
        writer.writerow(new_header)

        for row in reader:
            if 'img_uri' in header and header.index('img_uri') < len(row) and row[header.index('img_uri')]:
                new_row = [row[i] for i in range(len(row)) if i not in indices_to_remove]
                writer.writerow(new_row)
                Counter += 1

        # Output timestamp and counter to record.csv
        timestamp = datetime.now().strftime("%Y-%m-%d %H")
        record_writer.writerow([timestamp, Counter])

send_counter_to_telegram(Counter)



print("Processing is complete")
