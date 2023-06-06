from fastapi import FastAPI, APIRouter, Query,HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import yt_dlp

from process import get_channel_info,get_HighLvlcomments,get_Lowlvlcomments

from sentimentAnalysis import performSentilytics

from database import insert_videos_info,retrieve_comments_by_sentiment,retrieve_all_comments,get_videos_by_channelID\
                     ,get_user_requests,get_completed_works,get_pending_works

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
    from datetime import datetime
    import pandas as pd
    import json
    
    channel_url = f'https://www.youtube.com/channel/{channelID}/videos'
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'skip_download': True,
        'getduration': True,
        'getdescription': True,
        'getuploaddate': True,
        'playlistend': 20
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(channel_url, download=False)
        videos = info_dict['entries']

    video_data = []
    for video in videos:
        video_id = video['id']
        title = video['title']
        url = video['webpage_url']
        description = video.get('description', '')
        duration = video.get('duration')
        published_at = video.get('upload_date', '')
        thumbnails = video.get('thumbnails', [])
        view_count = video.get('view_count', 0)
        like_count = video.get('like_count', 0)
        comment_count = video.get('comment_count', 0)
        minutes, seconds = divmod(duration, 60)
        
        video_data.append({
            'channel_id': channelID,
            'video_id': video_id,
            'title': title,
            'view_count': str(view_count),
            'like_count': str(like_count),
            'comment_count': str(comment_count),
            'url': url,
            'description': description,
            'duration': f'{minutes:02d}:{seconds:02d}',
            'published_at': datetime.strptime(published_at, "%Y%m%d").strftime("%B %d, %Y"),
            'thumbnails': thumbnails[-1]['url']           
    })
    df = pd.DataFrame(video_data)
    
    insert_videos_info(df)
    return json.loads(json.dumps(video_data, indent=4))


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

@router.get("/get_videos/")
async def perform_sentilytics(channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to perform sentiment analysis on comments.
    """
    video_result = get_videos_by_channelID(channelID)
    return JSONResponse(content=video_result)

@app.get("/get_comments/")
async def get_comments(comments: str, videoID: str, sentiment: str = None):
    
    # Determine the table name based on the query parameters
    if comments == "hl":
        table_name = "OnlyComments_SentimentAnalysis"
    elif comments == "ll":
        table_name = "CommentsWithReply_SentimentAnalysis"
    else:
        raise HTTPException(status_code=400, detail="Either 'hl' or 'll' parameter is required.")

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
async def perform_sentilytics(userID: str = Query(..., description="User ID")):
    """
    Endpoint to get all the user requests.
    """
    return JSONResponse(content=get_user_requests(userID))


@router.get("/get_completed_works/")
async def perform_sentilytics(channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to get work progress for a given channelID
    """
    return JSONResponse(content=get_completed_works(channelID))


@router.get("/get_pending_works/")
async def perform_sentilytics(channelID: str = Query(..., description="Channel ID")):
    """
    Endpoint to get pending works for a given channelID
    """
    return JSONResponse(content=get_pending_works(channelID))


# Include the router in the main app
app.include_router(router)
