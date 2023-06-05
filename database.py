import sqlite3
import pandas as pd

def insert_channel_info(user_id, channel_id, channel_title, channel_description, subscriber_count, video_count,
                        channel_created_date, channel_logo_url):
    connection = sqlite3.connect("sentilytics.db")
    cursor = connection.cursor()
    
    # Inserting the channel information into the Channels table
    cursor.execute('''
        INSERT INTO Channels (
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

    # Commit the changes to the database
    connection.commit()
    connection.close()


def insert_videos_info(df):
    connection = sqlite3.connect("sentilytics.db")
    cursor = connection.cursor()

    video_data = df.to_records(index=False)
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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', video_data)
    
    connection.commit()
    connection.close()
    
def insert_highlvl_cmntInfo(df):
    connection = sqlite3.connect("sentilytics.db")
    cursor = connection.cursor()

    comments_data = df[['Video ID', 'Comment ID', 'Comments']].to_records(index=False)
    cursor.executemany('''
        INSERT INTO OnlyComments_Unfiltered (vid_id, comment_id, comment) VALUES (?, ?, ?)
    ''', comments_data)
    
    connection.commit()
    connection.close()
    
def insert_highlvl_filtered_cmntInfo(df):
    connection = sqlite3.connect("sentilytics.db")
    cursor = connection.cursor()

    comments_data = df[['Video ID', 'Comment ID', 'Comments']].to_records(index=False)
    cursor.executemany('''
        INSERT INTO OnlyComments_filtered (vid_id, comment_id, comment) VALUES (?, ?, ?)
    ''', comments_data)
    
    connection.commit()
    connection.close()
    
def insert_lowlvl_cmntInfo(df):
    connection = sqlite3.connect("sentilytics.db")
    cursor = connection.cursor()

    comments_data = df[['Video ID', 'Comment ID', 'Comments']].to_records(index=False)
    cursor.executemany('''
        INSERT INTO CommentsWithReply_Unfiltered (vid_id, comment_id, comment) VALUES (?, ?, ?)
    ''', comments_data)
    
    connection.commit()
    connection.close()
    
def insert_lowlvl_filtered_cmntInfo(df):
    connection = sqlite3.connect("sentilytics.db")
    cursor = connection.cursor()

    comments_data = df[['Video ID', 'Comment ID', 'Comments']].to_records(index=False)
    cursor.executemany('''
        INSERT INTO CommentsWithReply_filtered (vid_id, comment_id, comment) VALUES (?, ?, ?)
    ''', comments_data)
    
    connection.commit()
    connection.close()
    
    
def get_FhlComments(vid_id):
    conn = sqlite3.connect('sentilytics.db')

    query = f"SELECT * FROM OnlyComments_filtered WHERE vid_id = '{vid_id}'"
    result = conn.execute(query)
    
    columns = ['Video ID', 'Comment ID', 'Comments']
    data = result.fetchall()
    df = pd.DataFrame(data, columns=columns)
    conn.close()
    
    return df

    
def get_FllComments(vid_id):
    conn = sqlite3.connect('sentilytics.db')

    query = f"SELECT * FROM CommentsWithReply_filtered WHERE vid_id = '{vid_id}'"
    result = conn.execute(query)
    
    columns = ['Video ID', 'Comment ID', 'Comments']
    data = result.fetchall()
    df = pd.DataFrame(data, columns=columns)
    conn.close()
    
    return df

    
def get_MhlComments(vid_id):
    conn = sqlite3.connect('sentilytics.db')

    query = f"SELECT * FROM OnlyComments_Unfiltered WHERE vid_id = '{vid_id}'"
    result = conn.execute(query)
    
    columns = ['Video ID', 'Comment ID', 'Comments']
    data = result.fetchall()
    df = pd.DataFrame(data, columns=columns)
    conn.close()
    
    return df

    
def get_MllComments(vid_id):
    conn = sqlite3.connect('sentilytics.db')

    query = f"SELECT * FROM CommentsWithReply_Unfiltered WHERE vid_id = '{vid_id}'"
    result = conn.execute(query)
    
    columns = ['Video ID', 'Comment ID', 'Comments']
    data = result.fetchall()
    df = pd.DataFrame(data, columns=columns)
    conn.close()
    
    return df


def insert_hlSentiComments(df):
    connection = sqlite3.connect("sentilytics.db")
    cursor = connection.cursor()

    comments_data = df[['Video ID', 'Comment ID', 'Comments', 'Sentiment']].to_records(index=False)
    cursor.executemany('''
        INSERT INTO OnlyComments_SentimentAnalysis (vid_id, comment_id, comment, sentiment) VALUES (?, ?, ?, ?)
    ''', comments_data)
    
    connection.commit()
    connection.close()

def insert_llSentiComments(df):
    connection = sqlite3.connect("sentilytics.db")
    cursor = connection.cursor()

    comments_data = df[['Video ID', 'Comment ID', 'Comments', 'Sentiment']].to_records(index=False)
    cursor.executemany('''
        INSERT INTO CommentsWithReply_SentimentAnalysis (vid_id, comment_id, comment, sentiment) VALUES (?, ?, ?, ?)
    ''', comments_data)
    
    connection.commit()
    connection.close()
    

def retrieve_comments_by_sentiment(table_name: str, videoID: str, sentiment: str):
    conn = sqlite3.connect("sentilytics.db")
    cursor = conn.cursor()

    query = f"SELECT vid_id, comment_id, comment, sentiment FROM {table_name} WHERE vid_id = ? AND sentiment = ?"
    print(query)
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


def retrieve_all_comments(table_name: str, videoID: str):
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




