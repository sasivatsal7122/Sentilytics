from fastapi import FastAPI, APIRouter, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from process import scrape_channel_info,scrape_HighLvlcomments
import httpx

from sentimentAnalysis import performSentilytics

from database import get_channel_name, insert_scan_info, get_DevKey

from ytranker import start_videoRanker
from cvStats import start_cvStats

from getMethods import get_channel_info,get_monthly_stats,get_video_stats,\
                       get_emoji_analysis,select_data_by_scan_id

from make_replication import makeReplication


#gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Create an APIRouter instance for grouping related routes
router = APIRouter()

# Define the root route
@router.get("/")
async def root():
    return {"message": "Hello World"}

# helper function for scrape channel endpoint
async def scrapeCHannelUtil(scanID, channelUsername, background_tasks):
    DEVELOPER_KEY, _, _ = get_DevKey()
    async with httpx.AsyncClient(timeout=300) as client:
        response = await client.get(f"https://youtube.googleapis.com/youtube/v3/search?part=snippet&q={channelUsername}&type=channel&key={DEVELOPER_KEY}")
        response_json = response.json()
    channelID = response_json['items'][0]['id']['channelId']
    
    await insert_scan_info(scan_id = scanID,channel_id=channelID, phase='scrape_channel', is_start=True)
    background_tasks.add_task(scrape_channel_info, scanID, channelUsername, background_tasks)
  

# Define the "scrape_channel" route
@router.get("/scrape_channel/")
async def scrape_channel(background_tasks: BackgroundTasks,
                         scanID: str = Query(..., description="Scan ID"),
                         channelUsername: str = Query(..., description="Channel Username")):
    """
    Endpoint to scrape channel information.
    """
    background_tasks.add_task(scrapeCHannelUtil, scanID, channelUsername,background_tasks)
    return JSONResponse(content={"message": "Scraping initiated"})

# Define the "get_hlcomments" route
@router.get("/scrape_hlcomments/")
async def get_hlcomments(background_tasks: BackgroundTasks,
                         scanID: str = Query(..., description="Scan ID"),
                         channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to get high-level comments.
    """

    await insert_scan_info(scan_id = scanID,channel_id=channelID, phase='scrape_hlcomments',is_start=True)
    background_tasks.add_task(scrape_HighLvlcomments,scanID,channelID)
    return JSONResponse(content={"message": "Comments Scraping initiated"})

# Define the "perform_sentilytics" route
@router.get("/perform_sentilytics/")
async def perform_sentilytics(background_tasks: BackgroundTasks, 
                              scanID: str = Query(..., description="Scan ID"),
                              channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to perform sentiment analysis on comments.
    """
    
    await insert_scan_info(scan_id = scanID, channel_id=channelID, phase='perform_sentilytics',is_start=True)
    background_tasks.add_task(performSentilytics, scanID,channelID)
    return JSONResponse(content={"message": "Sentiment Analysis initiated"})


async def perform_youtube_ranker(background_tasks: BackgroundTasks, videoID: str, keyword: str):
    background_tasks.add_task(start_videoRanker, videoID, keyword)

# Define the "perform_youtube_ranker" route
@router.get("/perform_youtube_ranker/")
async def perform_youtube_ranker_route(background_tasks: BackgroundTasks,scanID: str = Query(..., description="Scan ID"), videoID: str = Query(..., description="Video ID"), keyword: str = Query(..., description="Keyword")):
    """
    Endpoint to perform YouTube ranking.
    """
    await insert_scan_info(scan_id = scanID,channel_id=videoID, phase='perform_youtube_ranker',is_start=True)
    await perform_youtube_ranker(background_tasks, videoID, keyword)
    return JSONResponse(content={"message": "YouTube ranking initiated"})


@router.get("/cvstats/")
async def scrape_cvStats(background_tasks: BackgroundTasks, 
                         scanID: str = Query(..., description="Scan ID"),
                         channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to perform Channel and Video Statistics.
    """
    channelName = await get_channel_name(channelID)
    background_tasks.add_task(start_cvStats, scanID, channelID, channelName)
    return JSONResponse(content={"message": "CV Stats initiated"})

@router.get("/make_replica/")
async def scrape_cvStats(scanID: str = Query(..., description="Scan ID"),channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to make data replication for a given scan/Scan id.
    """
    await insert_scan_info(scan_id = scanID,channel_id=channelID, phase='make_replica',is_start=True)
    await makeReplication(scanID,channelID)
    return JSONResponse(content={"message": "Replication Done"})

# ====  GET METHODS  ====

@app.get("/get_complete_scan/")
async def getChannel_info(scanID: str = Query(..., description="Scan ID")):
    """
    Endpoint to get all tables information for a given scan/Scan id.
    """
    return JSONResponse(content=select_data_by_scan_id(scanID))

@app.get("/get_channel_info/")
async def getChannel_info(channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to get channel information.
    """
    return JSONResponse(content=get_channel_info(channelID))

@app.get("/get_monthly_stats/")
async def getMonthly_stats(channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to get monthly statistics information.
    """
    return JSONResponse(content=get_monthly_stats(channelID))

@app.get("/get_video_stats/")
async def getVideo_stats(channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to get video statistics information.
    """
    return JSONResponse(content=get_video_stats(channelID))

@app.get("/get_emoji_stats/")
async def getEmoji_stats(channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to get emoji frequency of 20 videos for a given channel.
    """
    return JSONResponse(content=get_emoji_analysis(channelID))

# Include the router in the main app
app.include_router(router)
