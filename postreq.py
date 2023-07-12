import httpx
from datetime import datetime

async def make_post_request(url: str):
    async with httpx.AsyncClient(timeout=100) as client:
        response = await client.get(url)
        print(response.status_code)
        
BOT_ID = "6196937033:AAHYgPHhos1kTSXNGU-CrZ7O0BPpa0ubrSQ"
CHAT_ID = "-836640467"

async def send_telegram_message(data: dict):
    url = f"https://api.telegram.org/bot{BOT_ID}/sendMessage"

    current_time = datetime.now().strftime("%I:%M%p")
    current_date = datetime.now().strftime("%d %B, %Y")
    message = f"{current_time} - {current_date}\n{data['text']}"
    data["text"] = message
    
    data["chat_id"] = CHAT_ID
    async with httpx.AsyncClient(timeout=100) as client:
        response = await client.post(url, json=data)
        print("Bot Response Code:",response.status_code)

# # Make the post request upon completion
# post_data = {
#     "message": "Scraping completed",
#     "userID": userID,
#     "channelUsername": channelUsername
# }
# await make_post_request("http://dummy-ip-address.com/endpoint", post_data)
