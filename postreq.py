import httpx

async def make_post_request(url: str, data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)
        print(response.status_code)
        
        

# # Make the post request upon completion
# post_data = {
#     "message": "Scraping completed",
#     "userID": userID,
#     "channelUsername": channelUsername
# }
# await make_post_request("http://dummy-ip-address.com/endpoint", post_data)
