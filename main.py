from fastapi import FastAPI

from process import get_channel_info,get_latest20,get_HighLvlcomments,get_Lowlvlcomments

from sentimentAnalysis import performSentilytics

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/scrape_channel/")
async def root(userID: str, channelUsername: str):
    
    return get_channel_info(userID, channelUsername)

@app.get("/get_latest20/")
async def root(channelID: str):
    
    return get_latest20(channelID)

@app.get("/get_hlcomments/")
async def root(videoID: str):
    
    return get_HighLvlcomments(videoID)

@app.get("/get_llcomments/")
async def root(videoID: str):
    
    return get_Lowlvlcomments(videoID)

@app.get("/perform_sentilytics/")
async def root(videoID: str):
    
    return performSentilytics(videoID)

