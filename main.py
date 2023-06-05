from fastapi import FastAPI, APIRouter, Query
from fastapi.responses import JSONResponse

from process import get_channel_info,get_latest20,get_HighLvlcomments,get_Lowlvlcomments

from sentimentAnalysis import performSentilytics


app = FastAPI()
# Create an APIRouter instance for grouping related routes
router = APIRouter()

# Define the root route
@router.get("/")
async def root():
    return {"message": "Hello World"}

# Define the "scrape_channel" route
@router.get("/scrape_channel/")
async def scrape_channel(userID: str = Query(..., description="User ID"),
                         channelUsername: str = Query(..., description="Channel Username")):
    """
    Endpoint to scrape channel information.
    """
    channel_info = get_channel_info(userID, channelUsername)
    return JSONResponse(content=channel_info)

# Define the "get_latest20" route
@router.get("/get_latest20/")
async def get_latest20(channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to get the latest 20 records.
    """
    latest_records = get_latest20(channelID)
    return JSONResponse(content=latest_records)

# Define the "get_hlcomments" route
@router.get("/get_hlcomments/")
async def get_hlcomments(videoID: str = Query(..., description="Video ID")):
    """
    Endpoint to get high-level comments.
    """
    hl_comments = get_HighLvlcomments(videoID)
    return JSONResponse(content=hl_comments)

# Define the "get_llcomments" route
@router.get("/get_llcomments/")
async def get_llcomments(videoID: str = Query(..., description="Video ID")):
    """
    Endpoint to get low-level comments.
    """
    ll_comments = get_Lowlvlcomments(videoID)
    return JSONResponse(content=ll_comments)

# Define the "perform_sentilytics" route
@router.get("/perform_sentilytics/")
async def perform_sentilytics(videoID: str = Query(..., description="Video ID")):
    """
    Endpoint to perform sentiment analysis on comments.
    """
    sentilytics_result = performSentilytics(videoID)
    return JSONResponse(content=sentilytics_result)

# Include the router in the main app
app.include_router(router)
