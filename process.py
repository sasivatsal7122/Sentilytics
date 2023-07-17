from googleapiclient.discovery import build
from fastapi import BackgroundTasks
from googleapiclient.errors import HttpError

import yt_dlp
import pandas as pd
from datetime import datetime
import requests
import hashlib
from postreq import send_telegram_message,make_post_request
import asyncio

# local imports
from filterDF import FilterDF
from database import insert_channel_info,insert_videos_info,\
    insert_highlvl_cmntInfo,insert_highlvl_filtered_cmntInfo,\
    insert_EmojiFreq

from emojiAnalysis import calcEmojiFreq

DEVELOPER_KEY = "AIzaSyD_NG--GtmImIOhDhp-5V6PFPmJhiiZN88"
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)


async def scrape_videos_info(channelID: str,channelUsername: str):
    """
    Endpoint to get the latest 20 records.
    """    
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
    await insert_videos_info(df)
    
    completion_message = f"For Channel: {channelUsername}, Scraping of Channel Info and Videos Info completed"
    asyncio.create_task(send_telegram_message({"text": completion_message}))
    await make_post_request(f"http://0.0.0.0:8000/scrape_hlcomments/?channelID={channelID}")
    
   

async def scrape_channel_info(user_id,channel_username,background_tasks: BackgroundTasks):
    
    response = requests.get(f"https://youtube.googleapis.com/youtube/v3/search?part=snippet&q={channel_username}&type=channel&key={DEVELOPER_KEY}").json()
    channel_id =  response['items'][0]['id']['channelId']
    channel_info = {
        'channel_id': channel_id,
        'channel_title': '',
        'video_count': 0,
        'channel_logo_url': '',
        'channel_created_date': '',
        'subscriber_count': 0,
        'channel_description': ''
    }

    try:
        response = youtube.channels().list(
            part='snippet,statistics',
            id=channel_id
        ).execute()

        if 'items' in response and len(response['items']) > 0:
            channel = response['items'][0]
            channel_info['channel_title'] = channel['snippet']['title']
            channel_info['video_count'] = int(channel['statistics']['videoCount'])
            channel_info['channel_logo_url'] = channel['snippet']['thumbnails']['default']['url']
            try:
                channel_info['channel_created_date'] = datetime.strptime(channel['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%SZ").strftime("%B %d, %Y")
            except:
                channel_info['channel_created_date'] = channel['snippet']['publishedAt']
            channel_info['subscriber_count'] = int(channel['statistics']['subscriberCount'])
            channel_info['channel_description'] = channel['snippet']['description']

        await insert_channel_info(
        user_id,
        channel_info['channel_id'],
        channel_info['channel_title'],
        channel_info['channel_description'],
        channel_info['subscriber_count'],
        channel_info['video_count'],
        channel_info['channel_created_date'],
        channel_info['channel_logo_url']
        )
        print("Channel info inserted into Database successfully")
        background_tasks.add_task(scrape_videos_info, channel_id,channel_username)
        
    except HttpError as e:
        print(f'An HTTP error occurred: {e}')
        return {"Error": "An HTTP error occurred {}".format(e)}



def generate_comment_id(video_id, comment_text):
    
    text_to_hash = f'{video_id}_{comment_text}'
    comment_hash = hashlib.sha256(text_to_hash.encode()).hexdigest()
    comment_id = comment_hash[:8]

    return comment_id


async def scrape_HighLvlcomments(video_ids, channelName,channelID):
    for video_id in video_ids:
        try:
            comments = []
            response = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=100, 
                textFormat='plainText'
            ).execute()

            while response:
                for item in response['items']:
                    comment = item['snippet']['topLevelComment']['snippet']
                    text = comment['textDisplay']
                    comments.append(
                        text
                    )

                if 'nextPageToken' in response:
                    next_page_token = response['nextPageToken']
                    response = youtube.commentThreads().list(
                        part='snippet',
                        videoId=video_id,
                        maxResults=100,  
                        textFormat='plainText',
                        pageToken=next_page_token
                    ).execute()
                else:
                    break
                
            HighLvldf = pd.DataFrame(comments,columns=['Comments'])
            HighLvldf['Video ID'] = video_id
            HighLvldf['Comment ID'] = HighLvldf.apply(lambda row: generate_comment_id(row['Video ID'], row['Comments']), axis=1)
        
            
            await insert_highlvl_cmntInfo(HighLvldf)
            emoji_frequency = await calcEmojiFreq(HighLvldf)
            await insert_EmojiFreq(video_id,emoji_frequency)
            
            HighLvldf_filtered = await FilterDF(HighLvldf)
            await insert_highlvl_filtered_cmntInfo(HighLvldf_filtered)
            
            # json_data = HighLvldf.groupby('Video ID').apply(lambda x: x[['Comments', 'Comment ID']].to_dict('records')).to_json()
            # json_data = json.loads(json_data)
            # return json_data
                    
        except HttpError as e:
            print(f'An HTTP error occurred: {e}')
            return {'error':f'An HTTP error occurred: {e}'}
    
    completion_message = f"Scraping of high-level comments completed for channel: {channelName}."
    asyncio.create_task(send_telegram_message({"text": completion_message}))
    await make_post_request(f"http://0.0.0.0:8000/perform_sentilytics/?channelID={channelID}")
    
# def get_Lowlvlcomments(videoId):
    
#     def getAllTopLevelCommentReplies(topCommentId, token): 

#         replies_response= youtube.comments().list(part='snippet',maxResults=100,parentId=topCommentId,pageToken=token).execute()

#         for indx, reply in enumerate(replies_response['items']):
#             all_comments.append(reply['snippet']['textDisplay'])

#         if "nextPageToken" in replies_response: 
#             return getAllTopLevelCommentReplies(topCommentId, replies_response['nextPageToken'])
#         else:
#             return []

#     def get_comments(youtube, video_id, token): 
#         global all_comments
#         totalReplyCount = 0
#         token_reply = None

#         if (len(token.strip()) == 0): 
#             all_comments = []

#         if (token == ''): 
#             video_response=youtube.commentThreads().list(part='snippet',maxResults=100,videoId=video_id,order='relevance').execute() 
#         else: 
#             video_response=youtube.commentThreads().list(part='snippet',maxResults=100,videoId=video_id,order='relevance',pageToken=token).execute() 

#         for indx, item in enumerate(video_response['items']): 
#             all_comments.append(item['snippet']['topLevelComment']['snippet']['textDisplay'])
#             totalReplyCount = item['snippet']['totalReplyCount']

#             if (totalReplyCount > 0): 
#                 replies_response=youtube.comments().list(part='snippet',maxResults=100,parentId=item['id']).execute()
#                 for indx, reply in enumerate(replies_response['items']):
#                     all_comments.append(reply['snippet']['textDisplay'])

#                 while "nextPageToken" in replies_response:
#                     token_reply = replies_response['nextPageToken']
#                     replies_response=youtube.comments().list(part='snippet',maxResults=100,parentId=item['id'],pageToken=token_reply).execute()
#                     for indx, reply in enumerate(replies_response['items']):
#                         all_comments.append(reply['snippet']['textDisplay'])

#         if "nextPageToken" in video_response: 
#             return get_comments(youtube, video_id, video_response['nextPageToken']) 
#         else: 
#             all_comments = [x for x in all_comments if len(x) > 0]
#             print("Scraping Comments Completed")
#             return []
    
#     get_comments(youtube,videoId,'')
#     AllLvldf = pd.DataFrame(all_comments,columns=['Comments'])
#     AllLvldf['Comment ID'] = np.random.randint(1, 1000000, size=len(AllLvldf))
#     AllLvldf['Comment ID'] = AllLvldf['Comment ID'].astype(str) + '_' + AllLvldf.groupby('Comment ID').cumcount().add(1).astype(str)
#     AllLvldf['Video ID'] = videoId
    
#     insert_lowlvl_cmntInfo(AllLvldf)
#     AllLvldf_filtered = FilterDF(AllLvldf)
#     insert_lowlvl_filtered_cmntInfo(AllLvldf_filtered)
    
#     json_data = AllLvldf.groupby('Video ID').apply(lambda x: x[['Comments', 'Comment ID']].to_dict('records')).to_json()
#     json_data = json.loads(json_data)
#     return json_data

    