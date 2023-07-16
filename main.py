from fastapi import FastAPI, APIRouter, Query,HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import asyncio
from process import scrape_channel_info,scrape_HighLvlcomments

from sentimentAnalysis import performSentilytics

from database import retrieve_comments_by_sentiment,retrieve_all_comments,get_videos_by_channelID\
                     ,get_user_requests,get_completed_works,get_pending_works,get_videoids_by_channelID\
                    ,get_channel_name

from ytranker import start_videoRanker
from postreq import send_telegram_message
from cvStats import start_cvStats

from getMethods import get_channel_info,get_monthly_stats,get_video_stats,\
                       get_emoji_analysis,get_video_comments


app = FastAPI()
# Create an APIRouter instance for grouping related routes
router = APIRouter()

# Define the root route
@router.get("/")
async def root():
    return {"message": "Hello World"}

# Define the "scrape_channel" route
@router.get("/scrape_channel/")
async def scrape_channel(background_tasks: BackgroundTasks,
                         userID: str = Query(..., description="User ID"),
                         channelUsername: str = Query(..., description="Channel Username")):
    """
    Endpoint to scrape channel information.
    """
    start_message = f"Scraping Channel Info for {channelUsername} initiated. User ID: {userID}"
    background_tasks.add_task(send_telegram_message, {"text": start_message})
    background_tasks.add_task(scrape_channel_info,userID, channelUsername,background_tasks)
    return JSONResponse(content={"message": "Scraping initiated"})

# Define the "get_hlcomments" route
@router.get("/scrape_hlcomments/")
async def get_hlcomments(background_tasks: BackgroundTasks, channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to get high-level comments.
    """
    channelName = await get_channel_name(channelID)
    start_message = f"Scraping high-level comments initiated for channel: {channelName}."
    background_tasks.add_task(send_telegram_message, {"text": start_message})
    
    videoIDs = await get_videoids_by_channelID(channelID)
    background_tasks.add_task(scrape_HighLvlcomments,videoIDs, channelName, channelID)
    return JSONResponse(content={"message": "Comments Scraping initiated"})


# Define the "perform_sentilytics" route
@router.get("/perform_sentilytics/")
async def perform_sentilytics(background_tasks: BackgroundTasks, channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to perform sentiment analysis on comments.
    """
    channelName = await get_channel_name(channelID)
    start_message = f"Sentiment Analysis initiated for channel: {channelName}."
    background_tasks.add_task(send_telegram_message, {"text": start_message})
    
    videoIDs = await get_videoids_by_channelID(channelID)
    background_tasks.add_task(performSentilytics,videoIDs, channelName)
    return JSONResponse(content={"message": "Sentiment Analysis initiated"})


async def perform_youtube_ranker(background_tasks: BackgroundTasks, videoID: str, keyword: str):
    background_tasks.add_task(start_videoRanker, videoID, keyword)

# Define the "perform_youtube_ranker" route
@router.get("/perform_youtube_ranker/")
async def perform_youtube_ranker_route(background_tasks: BackgroundTasks, videoID: str = Query(..., description="Video ID"), keyword: str = Query(..., description="Keyword")):
    """
    Endpoint to perform YouTube ranking.
    """
    await perform_youtube_ranker(background_tasks, videoID, keyword)
    return JSONResponse(content={"message": "YouTube ranking initiated"})


@router.get("/cvstats/")
async def scrape_cvStats(background_tasks: BackgroundTasks,channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to perform Channel and Video Statistics.
    """
    channelName = await get_channel_name(channelID)
    background_tasks.add_task(start_cvStats, channelID, channelName)
    return JSONResponse(content={"message": "CV Stats initiated"})


# ====  GET METHODS  ====

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

@app.get("/get_vid_comments/")
async def getVid_comments(videoID: str = Query(..., description="Video ID")):
    """
    Endpoint to get sentiment analysed comments for a given video.
    """
    return JSONResponse(content=get_video_comments(videoID))

@router.get("/get_videos/")
async def get_videos(channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to perform sentiment analysis on comments.
    """
    video_result = get_videos_by_channelID(channelID)
    return JSONResponse(content=video_result)

@app.get("/get_comments/")
async def get_comments(videoID: str, sentiment: str = None):
    
    # Determine the table name based on the query parameters
    
    table_name = "Comments_SentimentAnalysis"
    videoID = videoID

    # Retrieve comments from the table based on the sentiment parameter
    if sentiment:
        if sentiment not in ["positive", "negative", "neutral"]:
            raise HTTPException(status_code=400, detail="Invalid value for 'sentiment' parameter.")
        sentiment = sentiment.title()
        comments = retrieve_comments_by_sentiment(table_name, videoID, sentiment)
        count = len(comments[videoID])
        return {"count": count, "comments": comments}
    else:
        comments = retrieve_all_comments(table_name, videoID)
        positive_count = len([c for c in comments[videoID] if c["sentiment"] == "Positive"])
        negative_count = len([c for c in comments[videoID] if c["sentiment"] == "Negative"])
        neutral_count = len([c for c in comments[videoID] if c["sentiment"] == "Neutral"])
        return {
            
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "total_count": len(comments[videoID]),
            "comments":comments,
        }

@router.get("/get_user_requests/")
async def get_user_requests(userID: str = Query(..., description="User ID")):
    """
    Endpoint to get all the user requests.
    """
    return JSONResponse(content=get_user_requests(userID))


@router.get("/get_completed_works/")
async def get_completed_works(channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to get work progress for a given channelID
    """
    return JSONResponse(content=get_completed_works(channelID))


@router.get("/get_pending_works/")
async def get_completed_works(channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to get pending works for a given channelID
    """
    return JSONResponse(content=get_pending_works(channelID))


# Include the router in the main app
app.include_router(router)
