from fastapi import FastAPI, APIRouter, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

#from process import scrape_channel_info,scrape_HighLvlcomments
# from sentimentAnalysis import performSentilytics
# from ytranker import start_videoRanker
# from cvStats import start_cvStats
# from make_replication import makeReplication

from getMethods import get_channel_info,get_monthly_stats,get_video_stats,\
                       get_emoji_analysis,select_data_by_scan_id

from database import get_channel_name, insert_scan_info
from celery_conf import celeryApp

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

# Define the "scrape_channel" route
@router.get("/scrape_channel/")
async def scrape_channel(scanID: str = Query(..., description="Scan ID"),
                         channelUsername: str = Query(..., description="Channel Username")):
    """
    Endpoint to scrape channel information.
    """
    try:
        await insert_scan_info(scan_id=scanID, channel_id="channelID", phase='scrape_channel', is_start=True)
    except:
        return JSONResponse(content={"message": "Scan ID already exists"})
    celeryApp.send_task("celery_tasks.scrape_channel_info_task", args=[scanID, channelUsername])
    return JSONResponse(content={"message": "Scraping initiated"})

# Define the "get_hlcomments" route
@router.get("/scrape_hlcomments/")
async def get_hlcomments(scanID: str = Query(..., description="Scan ID"),
                         channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to get high-level comments.
    """
    await insert_scan_info(scan_id = scanID,channel_id=channelID, phase='scrape_hlcomments',is_start=True)
    celeryApp.send_task("celery_tasks.scrape_HighLvlcomments_task", args=[scanID, channelID])
    return JSONResponse(content={"message": "Comments Scraping initiated"})

# Define the "perform_sentilytics" route
@router.get("/perform_sentilytics/")
async def perform_sentilytics(scanID: str = Query(..., description="Scan ID"),
                              channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to perform sentiment analysis on comments.
    """    
    await insert_scan_info(scan_id = scanID, channel_id=channelID, phase='perform_sentilytics',is_start=True)
    celeryApp.send_task("celery_tasks.performSentilytics_task", args=[scanID, channelID])
    return JSONResponse(content={"message": "Sentiment Analysis initiated"})

# Define the "perform_youtube_ranker" route
@router.get("/perform_youtube_ranker/")
async def perform_youtube_ranker_route(scanID: str = Query(..., description="Scan ID"), videoID: str = Query(..., description="Video ID"), keyword: str = Query(..., description="Keyword")):
    """
    Endpoint to perform YouTube ranking.
    """
    await insert_scan_info(scan_id = scanID,channel_id=videoID, phase='perform_youtube_ranker',is_start=True)
    celeryApp.send_task("celery_tasks.start_videoRanker_task", args=[videoID, keyword])
    return JSONResponse(content={"message": "YouTube ranking initiated"})

# Define the "cvstats" route
@router.get("/cvstats/")
async def scrape_cvStats( scanID: str = Query(..., description="Scan ID"),
                         channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to perform Channel and Video Statistics.
    """
    channelName = await get_channel_name(channelID)
    celeryApp.send_task("celery_tasks.start_cvStats_task", args=[scanID, channelID, channelName])
    return JSONResponse(content={"message": "CV Stats initiated"})

@router.get("/make_replica/")
async def scrape_cvStats(scanID: str = Query(..., description="Scan ID"),channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to make data replication for a given scan/Scan id.
    """
    await insert_scan_info(scan_id = scanID,channel_id=channelID, phase='make_replica',is_start=True)
    celeryApp.send_task("celery_tasks.makeReplication_task", args=[scanID, channelID])
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
