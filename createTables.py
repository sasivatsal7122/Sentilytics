import pymysql

conn_params = {
    "host": "127.0.0.1",
    "port": 3306,                # Change to your MySQL port if necessary
    "user": "admin",
    "password": "admin",
    "db": "sentilytics",
}

conn = pymysql.connect(**conn_params)
cursor = conn.cursor()

def createIntialTables():
    
     # Create the Channels table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Channels (
            scan_id VARCHAR(255),
            channel_id VARCHAR(255),
            channel_title VARCHAR(255),
            channel_description TEXT,
            total_videos_count INTEGER,
            total_views_count INTEGER,
            total_subs_count INTEGER,
            partial_likes_count INTEGER,
            partial_comments_count INTEGER,
            partial_views_count INTEGER,
            channel_created_date VARCHAR(255),
            channel_logo_url TEXT,
            PRIMARY KEY (scan_id, channel_id)
        )
    ''')
    cursor.execute('''ALTER TABLE Channels ADD INDEX idx_channels_channel_id (channel_id)''')
    # Create the Videos table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Videos (
            channel_id VARCHAR(255),
            vid_id VARCHAR(255),
            vid_title VARCHAR(255),
            vid_view_cnt INTEGER,
            vid_like_cnt INTEGER,
            vid_comment_cnt INTEGER,
            vid_url VARCHAR(255),
            vid_desc TEXT,
            vid_duration VARCHAR(255),
            vid_published_at TEXT,
            vid_thumbnail VARCHAR(255),
            PRIMARY KEY (channel_id, vid_id),
            FOREIGN KEY (channel_id) REFERENCES Channels(channel_id) 
        )
    ''')
    cursor.execute('''ALTER TABLE Videos ADD INDEX idx_videos_vid_id (vid_id)''')

    # Create the Comments_Unfiltered table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Comments_Unfiltered (
            vid_id VARCHAR(255),
            comment_id VARCHAR(255),
            comment TEXT,
            PRIMARY KEY (vid_id,comment_id),
            FOREIGN KEY (vid_id) REFERENCES Videos(vid_id) 
        )
    ''')

    # Create the Comments_filtered table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Comments_filtered (
            vid_id VARCHAR(255),
            comment_id VARCHAR(255),
            comment TEXT,
            FOREIGN KEY (vid_id) REFERENCES Videos(vid_id) 
        )
    ''')

    # Create the Emoji_Frequency table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Emoji_Frequency (
            vid_id VARCHAR(255),
            highlvl_freq TEXT,
            PRIMARY KEY (vid_id),
            FOREIGN KEY (vid_id) REFERENCES Videos(vid_id) 
        )
    ''')

    # Create the Comments_SentimentAnalysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Comments_SentimentAnalysis (
            vid_id VARCHAR(255),
            comment_id VARCHAR(255),
            comment TEXT,
            sentiment VARCHAR(255),
            PRIMARY KEY (vid_id,comment_id),
            FOREIGN KEY (vid_id) REFERENCES Videos(vid_id) 
        )
    ''')
    
    # Create the Video_Rankings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Video_Rankings (
            vid_id VARCHAR(255),
            keyword VARCHAR(255),
            results_vidID VARCHAR(255),
            results_vidurl VARCHAR(255),
            results_vidTitle VARCHAR(255),
            results_vidDesc TEXT,
            results_vidDuration VARCHAR(255),
            results_vidViewcnt VARCHAR(255),
            results_vidDt VARCHAR(255),
            PRIMARY KEY (vid_id,keyword,results_vidID),
            FOREIGN KEY (vid_id) REFERENCES Videos(vid_id) 
        )
    ''')
    
    # Create the VideoStats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS VideoStats (
            channel_id VARCHAR(255),
            vid_id VARCHAR(255),
            date VARCHAR(255),
            vid_title VARCHAR(255),
            vid_view_cnt VARCHAR(255),
            vid_like_cnt VARCHAR(255),
            vid_comment_cnt VARCHAR(255),
            category VARCHAR(255),
            PRIMARY KEY (channel_id,vid_id,category),
            FOREIGN KEY (channel_id) REFERENCES Channels(channel_id) 
        )
    ''')

    # Create the MonthlyStats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MonthlyStats (
            channel_id VARCHAR(255),
            date VARCHAR(255),
            channel_subs VARCHAR(255),
            overall_views VARCHAR(255),
            PRIMARY KEY (channel_id, date),
            FOREIGN KEY (channel_id) REFERENCES Channels(channel_id) 
        )
    ''')
    
    # Create the ScanInfo table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ScanInfo (
        scan_id VARCHAR(255),
        channel_id VARCHAR(255),
        phase VARCHAR(255),
        start_time VARCHAR(255),
        end_time VARCHAR(255),
        success BOOLEAN,
        notes VARCHAR(255),
        PRIMARY KEY (scan_id,channel_id,phase)
    )
    ''')


    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__=="__main__":
    createIntialTables()