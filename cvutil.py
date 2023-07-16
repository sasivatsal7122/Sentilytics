from googleapiclient.discovery import build

DEVELOPER_KEY = "AIzaSyD_NG--GtmImIOhDhp-5V6PFPmJhiiZN88"
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

def getLatest_videos(channelID):
    video_details = []
   
    videos_request = youtube.search().list(
        part='snippet',
        channelId=channelID,
        maxResults=20,
        order='date',
        type='video'
    )
    videos_response = videos_request.execute()

    for video in videos_response['items']:
        video_id = video['id']['videoId']
        video_title = video['snippet']['title']
        video_date = video['snippet']['publishedAt']

        video_stats_request = youtube.videos().list(
            part='statistics',
            id=video_id
        )
        video_stats_response = video_stats_request.execute()

        video_statistics = video_stats_response['items'][0]['statistics']
        video_view_cnt = video_statistics.get('viewCount', 'N/A')
        video_like_cnt = video_statistics.get('likeCount', 'N/A')
        video_comment_cnt = video_statistics.get('commentCount', 'N/A')

        video_details.append({
                    'video_id': video_id,
                    'title': video_title,
                    'date': video_date,
                    'view_count': str(video_view_cnt),
                    'comment_count': str(video_comment_cnt),
                    'like_count': str(video_like_cnt),
                    'category':'latest'
                })
    
    return video_details

def getMostviewed_videos(channelID):
    video_details = []
    
    videos_request = youtube.search().list(
    part='snippet',
    channelId=channelID,
    maxResults=20,
    order='viewCount',
    type='video'
    )
    videos_response = videos_request.execute()
    video_ids = [item['id']['videoId'] for item in videos_response['items']]

    stats_request = youtube.videos().list(
        part='snippet,statistics',
        id=','.join(video_ids)
    )
    stats_response = stats_request.execute()
    video_stats = {item['id']: item['statistics'] for item in stats_response['items']}
    sorted_videos = sorted(videos_response['items'], key=lambda x: int(video_stats[x['id']['videoId']].get('viewCount', 0)), reverse=True)

    for video in sorted_videos:
        video_id = video['id']['videoId']
        video_title = video['snippet']['title']
        video_date = video['snippet']['publishedAt']
        video_view_cnt = video_stats[video_id].get('viewCount', 'N/A')
        video_like_cnt = video_stats[video_id].get('likeCount', 'N/A')
        video_comment_cnt = video_stats[video_id].get('commentCount', 'N/A')


        video_details.append({
                    'video_id': video_id,
                    'title': video_title,
                    'date': video_date,
                    'view_count': str(video_view_cnt),
                    'comment_count': str(video_comment_cnt),
                    'like_count': str(video_like_cnt),
                    'category':'mostviewed'
                })
        
    return video_details

def getHighestrated_videos(channelID):
    video_details = []
    
    videos_request = youtube.search().list(
    part='snippet',
    channelId=channelID,
    maxResults=20,
    order='rating',
    type='video'
    )
    videos_response = videos_request.execute()
    video_ids = [item['id']['videoId'] for item in videos_response['items']]

    stats_request = youtube.videos().list(
        part='snippet,statistics',
        id=','.join(video_ids)
    )
    stats_response = stats_request.execute()

    video_stats = {item['id']: item['statistics'] for item in stats_response['items']}
    sorted_videos = sorted(videos_response['items'], key=lambda x: int(video_stats[x['id']['videoId']].get('likeCount', 0)), reverse=True)

    for video in sorted_videos:
        video_id = video['id']['videoId']
        video_title = video['snippet']['title']
        video_date = video['snippet']['publishedAt']
        video_view_count = video_stats[video_id].get('viewCount', 'N/A')
        video_like_count = video_stats[video_id].get('likeCount', 'N/A')
        video_comment_count = video_stats[video_id].get('commentCount', 'N/A')

        video_details.append({
            'video_id': video_id,
            'title': video_title,
            'date': video_date,
            'view_count': str(video_view_count),
            'comment_count': str(video_comment_count),
            'like_count': str(video_like_count),
            'category':'highestrated'
        })
    
    return video_details



