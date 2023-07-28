import configparser
import aiohttp
import sqlite3 

config = configparser.ConfigParser()
config.read('config.ini')

BOT_ID = str(config['KEYS']['BOT_ID'])
CHAT_ID = (config['KEYS']['CHAT_ID'])

async def make_post_request(url: str):
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout()) as session:
        async with session.get(url) as response:
            print(F"GET METHOD STATUS CODE [{url}]:", response.status)

async def fetch_scan_info_from_db(channelID, channelName):
    conn = sqlite3.connect('sentilytics.db')  # Replace with your database connection
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM ScanInfo WHERE channel_id = ?', (channelID,))
    rows = cursor.fetchall()

    message_data = f"Channel: {channelName}\n\n"

    for row in rows:
        _, phase, start_time, end_time, _, _ = row
        message = f"{phase} - Start [{start_time}], End [{end_time}]\n"
        message_data += message

    return message_data

async def send_telegram_message(channelID: str,channelName: str):
    url = f"https://api.telegram.org/bot{BOT_ID}/sendMessage"
    
    message = await fetch_scan_info_from_db(channelID,channelName)
    data = {'text':message,
            'chat_id':CHAT_ID}
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=100)) as session:
        async with session.post(url, json=data) as response:
            print("Bot Response Code:", response.status)



# # Make the post request upon completion
# post_data = {
#     "message": "Scraping completed",
#     "userID": userID,
#     "channelUsername": channelUsername
# }
# await make_post_request("http://dummy-ip-address.com/endpoint", post_data)
