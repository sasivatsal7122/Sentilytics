import pymysql

conn_params = {
    "host": "0.0.0.0",
    "port": 3306,                # Change to your MySQL port if necessary
    "user": "admin",
    "password": "admin",
    "db": "sentilytics",
}

conn = pymysql.connect(**conn_params)
cursor = conn.cursor()

def createInitialTables():
    
     # Create the Channels table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Channels (
            scan_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255),
            channel_title VARCHAR(255),
            channel_description TEXT,
            total_videos_count INT,
            total_views_count BIGINT,
            total_subs_count BIGINT,
            partial_likes_count INT,
            partial_comments_count INT,
            partial_views_count BIGINT,
            channel_created_date VARCHAR(255),
            channel_logo_url TEXT
        )
    ''')
    
    cursor.execute('''
        ALTER TABLE Channels
        ADD INDEX idx_channel_id (channel_id)
    ''')
    # Create the ScanInfo table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ScanInfo (
            scan_index INT AUTO_INCREMENT PRIMARY KEY,
            scan_id VARCHAR(255),
            channel_id VARCHAR(255),
            phase VARCHAR(255),
            start_time VARCHAR(255),
            end_time VARCHAR(255),
            success BOOLEAN,
            notes VARCHAR(255),
            UNIQUE KEY unique_scan_id (scan_id,channel_id,phase)
        )
    ''')
    
    # Create the Videos table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Videos (
            vid_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255),
            vid_title VARCHAR(255),
            vid_view_cnt INTEGER,
            vid_like_cnt INTEGER,
            vid_comment_cnt INTEGER,
            vid_url VARCHAR(255),
            vid_desc TEXT,
            vid_duration VARCHAR(255),
            vid_published_at VARCHAR(255),
            vid_thumbnail VARCHAR(255),
            FOREIGN KEY (channel_id) REFERENCES Channels(channel_id)
        )
    ''')
    
    # Create the Comments_Unfiltered table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Comments_Unfiltered (
            vid_id VARCHAR(255),
            comment_id VARCHAR(255) PRIMARY KEY,
            comment TEXT,
            FOREIGN KEY (vid_id) REFERENCES Videos(vid_id)
        )
    ''')
    
    # Create the Comments_filtered table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Comments_filtered (
            vid_id VARCHAR(255),
            comment_id VARCHAR(255) PRIMARY KEY,
            comment TEXT,
            FOREIGN KEY (vid_id) REFERENCES Videos(vid_id)
        )
    ''')
    
    # Create the Emoji_Frequency table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Emoji_Frequency (
            vid_id VARCHAR(255) PRIMARY KEY,
            highlvl_freq TEXT,
            FOREIGN KEY (vid_id) REFERENCES Videos(vid_id)
        )
    ''')
    
    # Create the Comments_SentimentAnalysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Comments_SentimentAnalysis (
            vid_id VARCHAR(255),
            comment_id VARCHAR(255) PRIMARY KEY,  
            comment TEXT,
            sentiment VARCHAR(255),
            FOREIGN KEY (vid_id) REFERENCES Videos(vid_id)
        )
    ''')
    
    # Create the Video_Rankings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Video_Rankings (
            vid_rank_id VARCHAR(255) PRIMARY KEY,
            vid_id VARCHAR(255),
            keyword VARCHAR(255),
            results_vidID VARCHAR(255),
            results_vidurl VARCHAR(255),
            results_vidTitle VARCHAR(255),
            results_vidDesc TEXT,
            results_vidDuration VARCHAR(255),
            results_vidViewcnt VARCHAR(255),
            results_vidDt VARCHAR(255),
            FOREIGN KEY (vid_id) REFERENCES Videos(vid_id)
        )
    ''')
    
    # Create the VideoStats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS VideoStats (
            video_stats_id INT AUTO_INCREMENT PRIMARY KEY,
            channel_id VARCHAR(255),
            vid_id VARCHAR(255),
            date VARCHAR(255),
            vid_title VARCHAR(255),
            vid_view_cnt INT,
            vid_like_cnt INT,
            vid_comment_cnt INT,
            category VARCHAR(255),
            UNIQUE KEY unique_channel_date (channel_id,vid_id,category),
            FOREIGN KEY (channel_id) REFERENCES Channels(channel_id)
        )
    ''')

    # Create the MonthlyStats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MonthlyStats (
            monthly_stats_id INT AUTO_INCREMENT PRIMARY KEY,
            channel_id VARCHAR(255),
            date VARCHAR(255),
            channel_subs VARCHAR(255),
            overall_views VARCHAR(255),
            UNIQUE KEY unique_channel_date (channel_id,date),
            FOREIGN KEY (channel_id) REFERENCES Channels(channel_id)
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    createInitialTables()
