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
            vid_view_cnt INTEGER,
            vid_like_cnt INTEGER,
            vid_comment_cnt INTEGER,
            vid_url VARCHAR,
            vid_desc VARCHAR,
            vid_duration VARCHAR,
            vid_published_at TIMESTAMP,
            vid_thumbnail VARCHAR,
            PRIMARY KEY (channel_id, vid_id),
            FOREIGN KEY (channel_id) REFERENCES Channels(channel_id)
        )
    ''')

    # Create the OnlyComments_Unfiltered table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS OnlyComments_Unfiltered (
            vid_id VARCHAR,
            comment_id VARCHAR,
            comment VARCHAR,
            PRIMARY KEY (vid_id, comment_id),
            FOREIGN KEY (vid_id) REFERENCES Videos(vid_id)
        )
    ''')

    # Create the CommentsWithReply_Unfiltered table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CommentsWithReply_Unfiltered (
            vid_id VARCHAR,
            comment_id VARCHAR,
            comment VARCHAR,
            PRIMARY KEY (vid_id, comment_id),
            FOREIGN KEY (vid_id) REFERENCES Videos(vid_id)
        )
    ''')

    # Create the OnlyComments_filtered table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS OnlyComments_filtered (
            vid_id VARCHAR,
            comment_id VARCHAR,
            comment VARCHAR,
            PRIMARY KEY (vid_id, comment_id),
            FOREIGN KEY (vid_id) REFERENCES Videos(vid_id)
        )
    ''')

    # Create the CommentsWithReply_filtered table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CommentsWithReply_filtered (
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
            all_freq VARCHAR,
            PRIMARY KEY (vid_id),
            FOREIGN KEY (vid_id) REFERENCES Videos(vid_id)
        )
    ''')

    # Create the OnlyComments_SentimentAnalysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS OnlyComments_SentimentAnalysis (
            vid_id VARCHAR,
            comment_id VARCHAR,
            comment VARCHAR,
            sentiment VARCHAR,
            PRIMARY KEY (vid_id, comment_id),
            FOREIGN KEY (vid_id) REFERENCES Videos(vid_id)
        )
    ''')

    # Create the CommentsWithReply_SentimentAnalysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CommentsWithReply_SentimentAnalysis (
            vid_id VARCHAR,
            comment_id VARCHAR,
            comment VARCHAR,
            sentiment VARCHAR,
            PRIMARY KEY (vid_id, comment_id),
            FOREIGN KEY (vid_id) REFERENCES Videos(vid_id)
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
