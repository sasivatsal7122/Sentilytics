import sqlite3
from sqlite3 import IntegrityError
import pandas as pd
import json

async def insert_channel_info(user_id, channel_id, channel_title, channel_description, subscriber_count, video_count,
                        channel_created_date, channel_logo_url):
    connection = sqlite3.connect("sentilytics.db")
    cursor = connection.cursor()
    
    # Inserting the channel information into the Channels table
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO Channels (
                user_id,
                channel_id,
                channel_title,
                channel_description,
                subscriber_count,
                video_count,
                channel_created_date,
                channel_logo_url
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            channel_id,
            channel_title,
            channel_description,
            subscriber_count,
            video_count,
            channel_created_date,
            channel_logo_url
        ))
    except IntegrityError as e:
        pass
    # Commit the changes to the database
    connection.commit()
    connection.close()


async def insert_videos_info(df):
    connection = sqlite3.connect("sentilytics.db")
    cursor = connection.cursor()

    video_data = df.to_records(index=False)
    try:
        cursor.executemany('''
            INSERT OR REPLACE INTO Videos (
                channel_id,
                vid_id,
                vid_title,
                vid_view_cnt,
                vid_like_cnt,
                vid_comment_cnt,
                vid_url,
                vid_desc,
                vid_duration,
                vid_published_at,
                vid_thumbnail
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', video_data)
    except IntegrityError as e:
        pass
    
    connection.commit()
    connection.close()
    
async def insert_highlvl_cmntInfo(df):
    connection = sqlite3.connect("sentilytics.db")
    cursor = connection.cursor()

    comments_data = df[['Video ID', 'Comment ID', 'Comments']].to_records(index=False)
    try:
        cursor.executemany('''
            INSERT OR REPLACE INTO Comments_Unfiltered (vid_id, comment_id, comment) VALUES (?, ?, ?)
        ''', comments_data)
    except IntegrityError as e:
        pass
    
    connection.commit()
    connection.close()
    
async def insert_highlvl_filtered_cmntInfo(df):
    connection = sqlite3.connect("sentilytics.db")
    cursor = connection.cursor()

    comments_data = df[['Video ID', 'Comment ID', 'Comments']].to_records(index=False)
    try:
        cursor.executemany('''
            INSERT OR REPLACE INTO Comments_filtered (vid_id, comment_id, comment) VALUES (?, ?, ?)
        ''', comments_data)
    except IntegrityError as e:
        pass
        
    connection.commit()
    connection.close()
    
async def get_FhlComments(vid_id):
    conn = sqlite3.connect('sentilytics.db')

    query = f"SELECT * FROM Comments_filtered WHERE vid_id = '{vid_id}'"
    result = conn.execute(query)
    
    columns = ['Video ID', 'Comment ID', 'Comments']
    data = result.fetchall()
    df = pd.DataFrame(data, columns=columns)
    conn.close()
    
    return df
    
async def get_MhlComments(vid_id):
    conn = sqlite3.connect('sentilytics.db')

    query = f"SELECT * FROM Comments_Unfiltered WHERE vid_id = '{vid_id}'"
    result = conn.execute(query)
    
    columns = ['Video ID', 'Comment ID', 'Comments']
    data = result.fetchall()
    df = pd.DataFrame(data, columns=columns)
    conn.close()
    
    return df

async def insert_hlSentiComments(df):
    connection = sqlite3.connect("sentilytics.db")
    cursor = connection.cursor()

    comments_data = df[['Video ID', 'Comment ID', 'Comments', 'Sentiment']].to_records(index=False)
    cursor.executemany('''
        INSERT OR REPLACE INTO Comments_SentimentAnalysis (vid_id, comment_id, comment, sentiment) VALUES (?, ?, ?, ?)
    ''', comments_data)
    
    connection.commit()
    connection.close()
    
async def insert_EmojiFreq(videoID,freqDict):
    connection = sqlite3.connect("sentilytics.db")
    cursor = connection.cursor()
    
    freqDictString = str(freqDict)
    query = "INSERT OR REPLACE INTO Emoji_Frequency (vid_id, highlvl_freq) VALUES (?, ?)"
    cursor.execute(query, (videoID, freqDictString))
    connection.commit()
    connection.close()


async def retrieve_comments_by_sentiment(table_name: str, videoID: str, sentiment: str):
    conn = sqlite3.connect("sentilytics.db")
    cursor = conn.cursor()

    query = f"SELECT vid_id, comment_id, comment, sentiment FROM {table_name} WHERE vid_id = ? AND sentiment = ?"
    cursor.execute(query,(videoID, sentiment))

    comments = []
    for row in cursor.fetchall():
        comment = {
            "comment_id": row[1],
            "comment": row[2],
            "sentiment": row[3]
        }
        comments.append(comment)
    conn.close()

    return  {videoID: comments}


async def retrieve_all_comments(table_name: str, videoID: str):
    conn = sqlite3.connect("sentilytics.db")
    cursor = conn.cursor()

    query = f"SELECT vid_id, comment_id, comment, sentiment FROM {table_name} WHERE vid_id = ?"
    print(query)
    cursor.execute(query, (videoID,))
    comments = []
    for row in cursor.fetchall():
        comment = {
            "comment_id": row[1],
            "comment": row[2],
            "sentiment": row[3]
        }
        comments.append(comment)
    
    conn.close()

    return {videoID: comments}


async def get_videos_by_channelID(channelID):
    conn = sqlite3.connect("sentilytics.db")
    cursor = conn.cursor()

    query = "SELECT vid_id, vid_title, vid_view_cnt, vid_like_cnt, vid_comment_cnt, vid_url, vid_desc, vid_duration, vid_published_at, vid_thumbnail FROM Videos WHERE channel_id = ?"
    cursor.execute(query, (channelID,))
    rows = cursor.fetchall()

    videos = {}
    for row in rows:
        video_id = row[0]
        video_data = {
            "vid_title": row[1],
            "vid_view_cnt": row[2],
            "vid_like_cnt": row[3],
            "vid_comment_cnt": row[4],
            "vid_url": row[5],
            "vid_desc": row[6],
            "vid_duration": row[7],
            "vid_published_at": row[8],
            "vid_thumbnail": row[9]
        }
        videos[video_id] = video_data

    conn.close()

    return {"channelID":channelID, "videos": videos}



async def get_videoids_by_channelID(channelID):
    conn = sqlite3.connect("sentilytics.db")
    cursor = conn.cursor()

    query = "SELECT vid_id FROM Videos WHERE channel_id = ?"
    cursor.execute(query, (channelID,))
    rows = cursor.fetchall()

    videos = []
    for row in rows:
        video_id = row[0]
        videos.append(video_id)
        
    conn.close()

    return videos


async def get_user_requests(user_id):
    conn = sqlite3.connect('sentilytics.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM Channels
        WHERE user_id = ?
    ''', (user_id,))

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    data = []

    for row in rows:
        data.append(dict(zip(columns, row)))

    conn.close()
    json_string = json.dumps(data)
    return json.loads(json_string)


async def workProgress_util1(channel_id):
    conn = sqlite3.connect('sentilytics.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM Videos WHERE channel_id = ?
    ''', (channel_id,))
    result = cursor.fetchall()

    if len(result) == 0:
        return json.dumps({"error": "No scraped videos found for the given channel_id"})

    videos = []
    for row in result:
        video = {

            "video_id": row[1],
            "video_title": row[2],
            "video_view_count": row[3],
            "video_like_count": row[4],
            "video_comment_count": row[5],
            "video_url": row[6],
            "video_description": row[7],
            "video_duration": row[8],
            "video_published_at": row[9],
            "video_thumbnail": row[10]
        }
        videos.append(video)
    scraped_videoData = {
                "Videos Count": len(videos),
                "Video Data":  { "channel_id": {row[0]: videos} }
        }
        
    return json.loads(json.dumps(scraped_videoData, indent=4))


async def workProgress_util2(channel_id,tables):
    
    conn = sqlite3.connect('sentilytics.db')
    cursor = conn.cursor()
    
    query_high_level = f'''
        SELECT DISTINCT OU.vid_id, COUNT(OU.comment_id) AS comment_count
        FROM {tables[0]} OU
        WHERE OU.vid_id IN (
            SELECT V.vid_id
            FROM Videos V
            WHERE V.channel_id = ?
        )
        GROUP BY OU.vid_id
    '''

    query_all_comments = f'''
        SELECT DISTINCT CU.vid_id, COUNT(CU.comment_id) AS comment_count
        FROM {tables[1]} CU
        WHERE CU.vid_id IN (
            SELECT V.vid_id
            FROM Videos V
            WHERE V.channel_id = ?
        )
        GROUP BY CU.vid_id
    '''

    cursor.execute(query_high_level, (channel_id,))
    rows_high_level = cursor.fetchall()

    cursor.execute(query_all_comments, (channel_id,))
    rows_all_comments = cursor.fetchall()

    high_level_comments = []
    all_comments = []

    for row in rows_high_level:
        video_id = row[0]
        comment_count = row[1]

        query_video_details = '''
            SELECT vid_title
            FROM Videos
            WHERE vid_id = ?
        '''
        cursor.execute(query_video_details, (video_id,))
        video_row = cursor.fetchone()

        if video_row:
            video_title = video_row[0]

            high_level_comment = {
                "video_id": video_id,
                "video_title": video_title,
                "video_comment_count": comment_count
            }

            high_level_comments.append(high_level_comment)

    for row in rows_all_comments:
        video_id = row[0]
        comment_count = row[1]

        query_video_details = '''
            SELECT vid_title
            FROM Videos
            WHERE vid_id = ?
        '''
        cursor.execute(query_video_details, (video_id,))
        video_row = cursor.fetchone()

        if video_row:
            video_title = video_row[0]

            all_comment = {
                "video_id": video_id,
                "video_title": video_title,
                "video_comment_count": comment_count
            }

            all_comments.append(all_comment)

    video_data = {
        "High Level Comments": {
            "Videos Count": len(high_level_comments),
            "Video Info" : high_level_comments},
        "All Comments": {
            "Videos Count": len(all_comments),
            "Video Info" : all_comments},
    }
    return json.loads(json.dumps(video_data, indent=4))

        
async def get_completed_works(channel_id):
    
    tables1 = ["OnlyComments_SentimentAnalysis","CommentsWithReply_SentimentAnalysis"]
    tables2 = ["OnlyComments_Unfiltered","CommentsWithReply_Unfiltered"]
    
    work_progressData = {
        
        "Scraped Videos": workProgress_util1(channel_id),
        "Scraped Comments": workProgress_util2(channel_id,tables2),
        "Sentiment Analysis Completed": workProgress_util2(channel_id,tables1)
           
    }
    
    return json.loads(json.dumps(work_progressData, indent=4))



async def workPending_util1(channel_id,tables):

    conn = sqlite3.connect('sentilytics.db')
    cursor = conn.cursor()

    query_high_level = f'''
        SELECT DISTINCT OU.vid_id
        FROM {tables[0]} OU
        WHERE OU.vid_id IN (
            SELECT V.vid_id
            FROM Videos V
            WHERE V.channel_id = ?
        )
    '''

    query_all_comments = f'''
        SELECT DISTINCT CU.vid_id
        FROM {tables[1]} CU
        WHERE CU.vid_id IN (
            SELECT V.vid_id
            FROM Videos V
            WHERE V.channel_id = ?
        )
    '''

    cursor.execute(query_high_level, (channel_id,))
    rows_high_level = cursor.fetchall()

    cursor.execute(query_all_comments, (channel_id,))
    rows_all_comments = cursor.fetchall()

    existing_high_level_videos = set([row[0] for row in rows_high_level])
    existing_all_comments_videos = set([row[0] for row in rows_all_comments])

    query_high_level_pending_works = '''
        SELECT vid_id, vid_title
        FROM Videos
        WHERE channel_id = ? AND vid_id NOT IN (SELECT DISTINCT vid_id FROM OnlyComments_Unfiltered)
    '''

    cursor.execute(query_high_level_pending_works, (channel_id,))
    rows_high_level_pending_works = cursor.fetchall()

    high_level_pending_works = []

    for row in rows_high_level_pending_works:
        video_id = row[0]
        video_title = row[1]

        pending_work = {
            "video_id": video_id,
            "video_title": video_title
        }

        high_level_pending_works.append(pending_work)

    query_all_comments_pending_works = '''
        SELECT vid_id, vid_title
        FROM Videos
        WHERE channel_id = ? AND vid_id NOT IN (SELECT DISTINCT vid_id FROM CommentsWithReply_Unfiltered)
    '''

    cursor.execute(query_all_comments_pending_works, (channel_id,))
    rows_all_comments_pending_works = cursor.fetchall()

    all_comments_pending_works = []

    for row in rows_all_comments_pending_works:
        video_id = row[0]
        video_title = row[1]

        pending_work = {
            "video_id": video_id,
            "video_title": video_title
        }

        all_comments_pending_works.append(pending_work)

    pending_data = {
        "Pending Works": {
            "Pending High Level Comments": {
                "Videos Count yet to be scraped": len(high_level_pending_works),
                "Video Info yet to be scraped": high_level_pending_works
            },
            "Pending All Comments": {
                "Videos Count yet to be scraped": len(all_comments_pending_works),
                "Video Info yet to be scraped": all_comments_pending_works
            }
        }
    }

    conn.close()

    return json.loads(json.dumps(pending_data, indent=4))


async def get_pending_works(channel_id):
    
    tables1 = ["OnlyComments_SentimentAnalysis","CommentsWithReply_SentimentAnalysis"]
    tables2 = ["OnlyComments_Unfiltered","CommentsWithReply_Unfiltered"]
    
    work_pendingData = {
        
        "Pending Comments Scraping": workPending_util1(channel_id, tables2),
        "Pending Sentiment Analysis": workPending_util1(channel_id, tables1)    
    }

    return json.loads(json.dumps(work_pendingData, indent=4))