import os
import csv
from datetime import datetime,time
import requests

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


file_path = 'POIsLightshipDevPortal.csv'
OCCounter = 0
FairCounter = 0
PendingCounter=0
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
            if 'img_uri' in header and header.index('img_uri') < len(row) and row[header.index('img_uri')] :
                if row[header.index('localizability')] == "PRODUCTION":
                    new_row = [row[i] for i in range(len(row)) if i not in indices_to_remove]
                    writer.writerow(new_row)
                    OCCounter += 1
                else:
                    FairCounter += 1
            else:
                PendingCounter += 1

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record_writer.writerow([timestamp, OCCounter,FairCounter,PendingCounter])

send_to_telegram(timestamp+'\n'+"OC-Activated:"+str(OCCounter)+'\n'+"Experimental/Fair quality:"+str(FairCounter)+'\n'+"Pending(Not visible in the game):"+str(PendingCounter))

current_time = datetime.now().time()

# Check if the current time is between 0:00 and 2:00
if time(0, 0) <= current_time <= time(2, 0):
    os.system('rm lost.csv')
    os.system('rm location_data.db')
    os.system('python3 dailycheck.py')
    os.system('cp POIdb.csv dailycheck.csv')
    

print("Processing is complete")
