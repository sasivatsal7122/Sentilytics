import aiohttp
from datetime import datetime

async def make_post_request(url: str):
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout()) as session:
        async with session.get(url) as response:
            print(F"GET METHOD STATUS CODE [{url}]:", response.status)
        
BOT_ID = "6196937033:AAHYgPHhos1kTSXNGU-CrZ7O0BPpa0ubrSQ"
CHAT_ID = "919334359"

async def send_telegram_message(data: dict):
    url = f"https://api.telegram.org/bot{BOT_ID}/sendMessage"

    current_time = datetime.now().strftime("%I:%M%p")
    current_date = datetime.now().strftime("%d %B, %Y")
    message = f"{current_time} - {current_date}\n{data['text']}"
    data["text"] = message

    data["chat_id"] = CHAT_ID
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
