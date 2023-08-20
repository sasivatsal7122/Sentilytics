import pymysql
import pandas as pd
import json
import datetime
import configparser
import random

conn_params = {
    "host": "0.0.0.0",
    "port": 3306,                # Change to your MySQL port if necessary
    "user": "admin",
    "password": "admin",
    "db": "sentilytics",
}

# connection = pymysql.connect(**conn_params)
# cursor = connection.cursor()

def get_DevKey():
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    developer_keys = config.get('KEYS', 'DEVELOPER_KEY')
    keys_list = developer_keys.split(',')

    random_key = random.choice(keys_list)

    api_service_name = config.get('KEYS', 'YOUTUBE_API_SERVICE_NAME')
    api_version = config.get('KEYS', 'YOUTUBE_API_VERSION')

    return random_key, api_service_name, api_version

def update_scaninfo_channelid(channel_id, scan_id, phase="scrape_channel"):
    with pymysql.connect(**conn_params) as connection:
        with connection.cursor() as cursor:
            cursor.execute('''
                UPDATE ScanInfo
                SET channel_id=%s
                WHERE scan_id=%s AND phase=%s
            ''', (channel_id, scan_id, phase))
        connection.commit()

    
async def insert_scan_info(scan_id=None, channel_id=None, phase=None, is_start=False, success=False, notes=None):
    with pymysql.connect(**conn_params) as connection:
        with connection.cursor() as cursor:
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if is_start:
                cursor.execute('''
                    INSERT INTO ScanInfo (scan_id, channel_id, phase, start_time, success, notes)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE start_time=%s, success=%s, notes=%s
                ''', (scan_id, channel_id, phase, current_time, success, notes, current_time, success, notes))
            else:
                cursor.execute('''
                    UPDATE ScanInfo
                    SET end_time=%s, success=%s, notes=%s
                    WHERE channel_id=%s AND phase=%s
                ''', (current_time, success, notes, channel_id, phase))
                
        connection.commit()

async def insert_channel_info(scan_id, channel_info):
    with pymysql.connect(**conn_params) as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute('''
                    INSERT INTO Channels (
                        scan_id,
                        channel_id,
                        channel_title,
                        channel_description,
                        total_subs_count,
                        total_videos_count,
                        total_views_count,
                        partial_likes_count,
                        partial_comments_count,
                        partial_views_count,
                        channel_created_date,
                        channel_logo_url
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        scan_id=VALUES(scan_id),
                        channel_title=VALUES(channel_title),
                        channel_description=VALUES(channel_description),
                        total_subs_count=VALUES(total_subs_count),
                        total_videos_count=VALUES(total_videos_count),
                        total_views_count=VALUES(total_views_count),
                        channel_created_date=VALUES(channel_created_date),
                        channel_logo_url=VALUES(channel_logo_url)
                ''', (
                    scan_id,
                    channel_info['channel_id'],
                    channel_info['channel_title'],
                    channel_info['channel_description'],
                    channel_info['subscriber_count'],
                    channel_info['total_video_count'],
                    channel_info['total_views_count'],
                    0,
                    0,
                    0,
                    channel_info['channel_created_date'],
                    json.dumps(channel_info['channel_logo_url']),
                ))
            except pymysql.IntegrityError as e:
                pass

        connection.commit()
    
async def update_channel_partialData(channel_id, partial_likes_count, partial_comments_count, partial_views_count):
    
    update_query = '''
        UPDATE Channels
        SET partial_likes_count = %s,
            partial_comments_count = %s,
            partial_views_count = %s
        WHERE channel_id = %s
    '''
    with pymysql.connect(**conn_params) as connection:
        with connection.cursor() as cursor:
            cursor.execute(update_query, (partial_likes_count, partial_comments_count, partial_views_count, channel_id))
        connection.commit()
    
async def insert_videos_info(df):
    video_data = df.to_records(index=False)
    with pymysql.connect(**conn_params) as connection:
        with connection.cursor() as cursor:
            try:
                video_data_tuples = [tuple(record) for record in video_data]

                cursor.executemany('''
                    INSERT INTO Videos (
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
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        vid_title=VALUES(vid_title),
                        vid_view_cnt=VALUES(vid_view_cnt),
                        vid_like_cnt=VALUES(vid_like_cnt),
                        vid_comment_cnt=VALUES(vid_comment_cnt),
                        vid_url=VALUES(vid_url),
                        vid_desc=VALUES(vid_desc),
                        vid_duration=VALUES(vid_duration),
                        vid_published_at=VALUES(vid_published_at),
                        vid_thumbnail=VALUES(vid_thumbnail)
                ''', video_data_tuples)
            except pymysql.IntegrityError as e:
                pass

        connection.commit()

async def insert_highlvl_cmntInfo(df):
    comments_data = df[['Video ID', 'Comment ID', 'Comments']].to_records(index=False)
    comments_data_tuples = [tuple(record) for record in comments_data]
    with pymysql.connect(**conn_params) as connection:
        with connection.cursor() as cursor:
            try:
                cursor.executemany('''
                    INSERT INTO Comments_Unfiltered (vid_id, comment_id, comment) VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE comment=VALUES(comment)
                ''', comments_data_tuples)
            except pymysql.IntegrityError as e:
                pass

        connection.commit()
    
async def insert_highlvl_filtered_cmntInfo(df):
    comments_data = df[['Video ID', 'Comment ID', 'Comments']].to_records(index=False)
    comments_data_tuples = [tuple(record) for record in comments_data]
    with pymysql.connect(**conn_params) as connection:
        with connection.cursor() as cursor:
            try:
                cursor.executemany('''
                    INSERT INTO Comments_filtered (vid_id, comment_id, comment) VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE comment=VALUES(comment)
                ''', comments_data_tuples)
            except pymysql.IntegrityError as e:
                pass

        connection.commit()

async def insert_hlSentiComments(df):
    comments_data = df[['Video ID', 'Comment ID', 'Comments', 'Sentiment']].to_records(index=False)
    comments_data_tuples = [tuple(record) for record in comments_data]
    with pymysql.connect(**conn_params) as connection:
        with connection.cursor() as cursor:
            cursor.executemany('''
                INSERT INTO Comments_SentimentAnalysis (vid_id, comment_id, comment, sentiment) VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE comment=VALUES(comment), sentiment=VALUES(sentiment)
            ''', comments_data_tuples)
            
        connection.commit()

async def insert_EmojiFreq(videoID, freqDict):
    freqDictString = str(freqDict)
    query = "INSERT INTO Emoji_Frequency (vid_id, highlvl_freq) VALUES (%s, %s) ON DUPLICATE KEY UPDATE highlvl_freq=VALUES(highlvl_freq)"
    with pymysql.connect(**conn_params) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (videoID, freqDictString))
        connection.commit()
    
async def insert_video_rankings(videoID, keyword, video_data):
    query = '''
        INSERT INTO Video_Rankings (
            vid_id,
            keyword,
            results_vidID,
            results_vidurl,
            results_vidTitle,
            results_vidDesc,
            results_vidDuration,
            results_vidViewcnt,
            results_vidDt
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            results_vidID=VALUES(results_vidID),
            results_vidurl=VALUES(results_vidurl),
            results_vidTitle=VALUES(results_vidTitle),
            results_vidDesc=VALUES(results_vidDesc),
            results_vidDuration=VALUES(results_vidDuration),
            results_vidViewcnt=VALUES(results_vidViewcnt),
            results_vidDt=VALUES(results_vidDt)
    '''

    for video in video_data:
        results_vidID = video["Video ID"]
        results_vidurl = video["Youtube Link"]
        results_vidTitle = video["Video Title"]
        results_vidDesc = video["Description"]

        duration_str = video["Duration"]

        try:
            minutes, seconds = map(int, duration_str.split(":"))

            if minutes >= 60:
                hours = minutes // 60
                minutes %= 60
                formatted_duration = f"{hours} hours {minutes} minutes {seconds} seconds"
            else:
                formatted_duration = f"{minutes} minutes {seconds} seconds"
        except:
            formatted_duration = duration_str

        views_count = video["Views Count"]
        try:
            dt_posted = video["Dt Posted"]
            date_obj = datetime.datetime.strptime(dt_posted, "%Y%m%d")
            formatted_date = date_obj.strftime("%B %d, %Y")
        except Exception as e:
            print(e)
            formatted_date = video["Dt Posted"]
        with pymysql.connect(**conn_params) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (
                    videoID,
                    keyword,
                    results_vidID,
                    results_vidurl,
                    results_vidTitle,
                    results_vidDesc,
                    formatted_duration,
                    views_count,
                    formatted_date
                ))

            connection.commit()    

def insert_data_to_video_stats(df):
    values = df[['channel_id', 'video_id', 'date', 'title', 'view_count', 'like_count', 'comment_count', 'category']].values.tolist()
    
    modified_values = []
    for row in values:
        modified_row = [str(val) if isinstance(val, pd.Timestamp) else val for val in row]
        if modified_row[4] == 'N/A':
            modified_row[4] = None  # Set view count to NULL if 'N/A'
        modified_values.append(tuple(modified_row))
    
    sql = '''
        INSERT INTO VideoStats (channel_id, vid_id, date, vid_title, vid_view_cnt, vid_like_cnt, vid_comment_cnt, category)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        vid_title = VALUES(vid_title),
        vid_view_cnt = VALUES(vid_view_cnt),
        vid_like_cnt = VALUES(vid_like_cnt),
        vid_comment_cnt = VALUES(vid_comment_cnt),
        category = VALUES(category)
    '''
    
    with pymysql.connect(**conn_params) as connection:
        with connection.cursor() as cursor:
            cursor.executemany(sql, modified_values)
        connection.commit()

def insert_data_to_monthly_stats(df):
    with pymysql.connect(**conn_params) as connection:
        with connection.cursor() as cursor:
            
            for _, row in df.iterrows():
                channel_id = row['channel_id']
                date = row['date']
                channel_subs = row['channel_subs']
                overall_views = row['overall_views']

                # Insert a row into MonthlyStats table
                cursor.execute('''
                    INSERT INTO MonthlyStats (channel_id, date, channel_subs, overall_views)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    channel_subs = VALUES(channel_subs),
                    overall_views = VALUES(overall_views)
                ''', (channel_id, date, channel_subs, overall_views))

        connection.commit()

async def get_FhlComments(vid_id):
    with pymysql.connect(**conn_params) as connection:
        with connection.cursor() as cursor:
            query = f"SELECT * FROM Comments_filtered WHERE vid_id = '{vid_id}'"
            cursor.execute(query)
            data = cursor.fetchall()
    columns = ['Video ID', 'Comment ID', 'Comments']
    df = pd.DataFrame(data, columns=columns)
    return df

async def get_MhlComments(vid_id):
    with pymysql.connect(**conn_params) as connection:
        with connection.cursor() as cursor:
            query = f"SELECT * FROM Comments_Unfiltered WHERE vid_id = '{vid_id}'"
            cursor.execute(query)
            data = cursor.fetchall()
    columns = ['Video ID', 'Comment ID', 'Comments']
    df = pd.DataFrame(data, columns=columns)
    return df


async def get_channel_name(channel_id):
    with pymysql.connect(**conn_params) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT channel_title FROM Channels WHERE channel_id = %s', (channel_id,))
            result = cursor.fetchone()
    return result[0] if result else None

async def retrieve_comments_by_sentiment(table_name, videoID, sentiment):
    with pymysql.connect(**conn_params) as connection:
        with connection.cursor() as cursor:
            query = f"SELECT vid_id, comment_id, comment, sentiment FROM {table_name} WHERE vid_id = %s AND sentiment = %s"
            cursor.execute(query, (videoID, sentiment))

            comments = []
            for row in cursor.fetchall():
                comment = {
                    "comment_id": row[1],
                    "comment": row[2],
                    "sentiment": row[3]
                }
                comments.append(comment)

    return {videoID: comments}

async def retrieve_all_comments(table_name, videoID):
    with pymysql.connect(**conn_params) as connection:
        with connection.cursor() as cursor:
            query = f"SELECT vid_id, comment_id, comment, sentiment FROM {table_name} WHERE vid_id = %s"
            cursor.execute(query, (videoID,))
            comments = []
            for row in cursor.fetchall():
                comment = {
                    "comment_id": row[1],
                    "comment": row[2],
                    "sentiment": row[3]
                }
                comments.append(comment)    

    return {videoID: comments}

async def get_videos_by_channelID(channelID):
    with pymysql.connect(**conn_params) as connection:
        with connection.cursor() as cursor:
            query = "SELECT vid_id, vid_title, vid_view_cnt, vid_like_cnt, vid_comment_cnt, vid_url, vid_desc, vid_duration, vid_published_at, vid_thumbnail FROM Videos WHERE channel_id = %s"
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

    return {"channelID": channelID, "videos": videos}


async def get_videoids_by_channelID(channelID):
    with pymysql.connect(**conn_params) as connection:
        with connection.cursor() as cursor:
            query = "SELECT vid_id FROM Videos WHERE channel_id = %s"
            cursor.execute(query, (channelID,))
            rows = cursor.fetchall()

    videos = []
    for row in rows:
        video_id = row[0]
        videos.append(video_id)

    return videos


async def get_user_requests(scan_id):
    with pymysql.connect(**conn_params) as connection:
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT * FROM Channels
                WHERE scan_id = %s
            ''', (scan_id,))

            rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    data = []

    for row in rows:
        data.append(dict(zip(columns, row)))

    json_string = json.dumps(data)
    return json.loads(json_string)
