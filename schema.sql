-- Create the Channels table
CREATE TABLE IF NOT EXISTS Channels (
    channel_id VARCHAR(255) PRIMARY KEY,
    channel_title VARCHAR(255),
    channel_description TEXT,
    total_videos_count INTEGER,
    total_views_count INTEGER,
    total_subs_count INTEGER,
    partial_likes_count INTEGER,
    partial_comments_count INTEGER,
    partial_views_count INTEGER,
    channel_created_date VARCHAR(255),
    channel_logo_url TEXT
);

-- Create the ScanInfo table
CREATE TABLE IF NOT EXISTS ScanInfo (
    scan_id VARCHAR(255),
    channel_id VARCHAR(255),
    phase VARCHAR(255),
    start_time VARCHAR(255),
    end_time VARCHAR(255),
    success BOOLEAN,
    notes VARCHAR(255),
    PRIMARY KEY (scan_id, channel_id, phase),
    FOREIGN KEY (channel_id) REFERENCES Channels(channel_id)
);

-- Create the Videos table
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
    vid_published_at TEXT,
    vid_thumbnail VARCHAR(255),
    FOREIGN KEY (channel_id) REFERENCES Channels(channel_id)
);

-- Create the Comments_Unfiltered table
CREATE TABLE IF NOT EXISTS Comments_Unfiltered (
    comment_id VARCHAR(255) PRIMARY KEY,
    vid_id VARCHAR(255),
    comment TEXT,
    FOREIGN KEY (vid_id) REFERENCES Videos(vid_id)
);

-- Create the Comments_filtered table
CREATE TABLE IF NOT EXISTS Comments_filtered (
    comment_id VARCHAR(255) PRIMARY KEY,
    vid_id VARCHAR(255),
    comment TEXT,
    FOREIGN KEY (vid_id) REFERENCES Videos(vid_id)
);

-- Create the Emoji_Frequency table
CREATE TABLE IF NOT EXISTS Emoji_Frequency (
    vid_id VARCHAR(255) PRIMARY KEY,
    highlvl_freq TEXT,
    FOREIGN KEY (vid_id) REFERENCES Videos(vid_id)
);

-- Create the Comments_SentimentAnalysis table
CREATE TABLE IF NOT EXISTS Comments_SentimentAnalysis (
    comment_id VARCHAR(255) PRIMARY KEY,
    vid_id VARCHAR(255),
    comment TEXT,
    sentiment VARCHAR(255),
    FOREIGN KEY (vid_id) REFERENCES Videos(vid_id)
);

-- Create the Video_Rankings table
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
);

-- Create the VideoStats table
CREATE TABLE IF NOT EXISTS VideoStats (
    video_stats_id VARCHAR(255) PRIMARY KEY,
    channel_id VARCHAR(255),
    vid_id VARCHAR(255),
    date VARCHAR(255),
    vid_title VARCHAR(255),
    vid_view_cnt VARCHAR(255),
    vid_like_cnt VARCHAR(255),
    vid_comment_cnt VARCHAR(255),
    category VARCHAR(255),
    FOREIGN KEY (channel_id) REFERENCES Channels(channel_id),
    FOREIGN KEY (vid_id) REFERENCES Videos(vid_id)
);

-- Create the MonthlyStats table
CREATE TABLE IF NOT EXISTS MonthlyStats (
    monthly_stats_id VARCHAR(255) PRIMARY KEY,
    channel_id VARCHAR(255),
    date VARCHAR(255),
    channel_subs VARCHAR(255),
    overall_views VARCHAR(255),
    FOREIGN KEY (channel_id) REFERENCES Channels(channel_id)
);
