import sqlite3

conn = sqlite3.connect('sentilyticsReplica.db')
cursor = conn.cursor()


def createIntialTables():

    # Create the Channels table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Channels (
            user_id VARCHAR,
            channel_id VARCHAR,
            channel_title VARCHAR,
            channel_description VARCHAR,
            subscriber_count INTEGER,
            total_videos_count INTEGER,
            total_views_count INTEGER,
            partial_likes_count INTEGER,
            partial_comments_count INTEGER,
            partial_views_count INTEGER,
            channel_created_date TIMESTAMP,
            channel_logo_url VARCHAR,
            PRIMARY KEY (user_id, channel_id),
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    ''')

    # Create the Videos table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Videos (
            channel_id VARCHAR,
            vid_id VARCHAR,
            vid_title VARCHAR,
            vid_view_cnt VARCHAR,
            vid_like_cnt VARCHAR,
            vid_comment_cnt VARCHAR,
            vid_url VARCHAR,
            vid_desc VARCHAR,
            vid_duration VARCHAR,
            vid_published_at TIMESTAMP,
            vid_thumbnail VARCHAR,
            PRIMARY KEY (vid_id),
            FOREIGN KEY (channel_id) REFERENCES Channels(channel_id)
        )
    ''')

    # Create the Emoji_Frequency table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Emoji_Frequency (
            vid_id VARCHAR,
            highlvl_freq VARCHAR,
            PRIMARY KEY (vid_id),
            FOREIGN KEY (vid_id) REFERENCES Videos(vid_id)
        )
    ''')

    # Create the OnlyComments_SentimentAnalysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Comments_SentimentAnalysis (
            vid_id VARCHAR,
            comment_id VARCHAR,
            comment VARCHAR,
            sentiment VARCHAR,
            PRIMARY KEY (vid_id, comment_id),
            FOREIGN KEY (vid_id) REFERENCES Videos(vid_id)
        )
    ''')
    
    # Create the Video_Rankings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Video_Rankings (
            vid_id VARCHAR,
            keyword VARCHAR,
            results_vidID VARCHAR,
            results_vidurl VARCHAR,
            results_vidTitle VARCHAR,
            results_vidDesc VARCHAR,
            results_vidDuration VARCHAR,
            results_vidViewcnt VARCHAR,
            results_vidDt VARCHAR,
            PRIMARY KEY (vid_id, keyword,results_vidID),
            FOREIGN KEY (vid_id) REFERENCES Videos(vid_id)
        )
    ''')
    
    # Create the VideoStats table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS VideoStats (
        channel_id VARCHAR,
        video_id VARCHAR,
        date TIMESTAMP,
        vid_title VARCHAR,
        vid_view_cnt VARCHAR,
        vid_like_cnt VARCHAR,
        vid_comment_cnt VARCHAR,
        category VARCHAR,
        PRIMARY KEY (channel_id,video_id, vid_title,category),
        FOREIGN KEY (channel_id) REFERENCES Channels(channel_id)
    )
    ''')

    # Create the MonthlyStats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MonthlyStats (
            channel_id VARCHAR,
            date TIMESTAMP,
            channel_subs VARCHAR,
            overall_views VARCHAR,
            PRIMARY KEY (channel_id, date),
            FOREIGN KEY (channel_id) REFERENCES Channels(channel_id)
        )
    ''')
    
    # Create the ScanInfo table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ScanInfo (
            channel_id VARCHAR,
            phase VARCHAR,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            success BOOLEAN,
            notes VARCHAR,
            PRIMARY KEY (channel_id, phase),
            FOREIGN KEY (channel_id) REFERENCES Channels(channel_id)
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__=="__main__":
    createIntialTables()