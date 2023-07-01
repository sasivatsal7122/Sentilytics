import sqlite3

conn = sqlite3.connect('sentilytics.db')
cursor = conn.cursor()


def createIntialTables():
    # Create the Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id VARCHAR PRIMARY KEY,
            Username VARCHAR,
            email VARCHAR,
            password VARCHAR,
            created_at TIMESTAMP
        )
    ''')

    # Create the Channels table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Channels (
            user_id VARCHAR,
            channel_id VARCHAR,
            channel_title VARCHAR,
            channel_description VARCHAR,
            subscriber_count INTEGER,
            video_count INTEGER,
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

    # Create the OnlyComments_Unfiltered table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Comments_Unfiltered (
            vid_id VARCHAR,
            comment_id VARCHAR,
            comment VARCHAR,
            PRIMARY KEY (vid_id, comment_id),
            FOREIGN KEY (vid_id) REFERENCES Videos(vid_id)
        )
    ''')

    # Create the OnlyComments_filtered table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Comments_filtered (
            vid_id VARCHAR,
            comment_id VARCHAR,
            comment VARCHAR,
            PRIMARY KEY (vid_id, comment_id),
            FOREIGN KEY (vid_id) REFERENCES Videos(vid_id)
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
    
    # Create the OnlyComments_SentimentAnalysis table
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
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS VideoStats (
        channel_id VARCHAR,
        date TIMESTAMP,
        vid_title VARCHAR,
        vid_view_cnt VARCHAR,
        vid_comment_cnt VARCHAR,
        category VARCHAR,
        PRIMARY KEY (channel_id, vid_title,category),
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

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__=="__main__":
    createIntialTables()