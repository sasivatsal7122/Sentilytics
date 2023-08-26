import configparser
import requests

config = configparser.ConfigParser()
config.read('config.ini')

BOT_ID = str(config['KEYS']['BOT_ID'])
CHAT_ID = (config['KEYS']['CHAT_ID'])

def make_post_request(url: str):
    response = requests.get(url)
    print(f"GET METHOD STATUS CODE [{url}]: {response.status_code}")

# # Make the post request upon completion
# post_data = {
#     "message": "Scraping completed",
#     "userID": userID,
#     "channelUsername": channelUsername
# }
# await make_post_request("http://dummy-ip-address.com/endpoint", post_data)
