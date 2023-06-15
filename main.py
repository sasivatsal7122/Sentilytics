from fastapi import FastAPI, APIRouter, Query,HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from process import scrape_channel_info,scrape_HighLvlcomments

from sentimentAnalysis import performSentilytics

from database import retrieve_comments_by_sentiment,retrieve_all_comments,get_videos_by_channelID\
                     ,get_user_requests,get_completed_works,get_pending_works,get_videoids_by_channelID

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
    background_tasks.add_task(scrape_channel_info, userID, channelUsername,background_tasks)
    return JSONResponse(content={"message": "Scraping initiated"})


# Define the "get_hlcomments" route
@router.get("/scrape_hlcomments/")
async def get_hlcomments(background_tasks: BackgroundTasks,channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to get high-level comments.
    """
    videoIDs = await get_videoids_by_channelID(channelID)
    for videoID in videoIDs:
        background_tasks.add_task(scrape_HighLvlcomments, videoID)
    return JSONResponse(content={"message": "Comments Scraping initiated"})


async def perform_sentiment_analysis(background_tasks: BackgroundTasks, videoID: str):
    background_tasks.add_task(performSentilytics, videoID)

# Define the "perform_sentilytics" route
@router.get("/perform_sentilytics/")
async def perform_sentilytics(background_tasks: BackgroundTasks,channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to perform sentiment analysis on comments.
    """
    videoIDs = await get_videoids_by_channelID(channelID)
    for videoID in videoIDs:
        await perform_sentiment_analysis(background_tasks,videoID)
    return JSONResponse(content={"message": "Sentiment Analysis initiated"})



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