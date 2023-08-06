import sqlite3

def select_data_by_user_id(user_id):
    
    conn = sqlite3.connect('sentilytics.db')
    cursor = conn.cursor()  
    
    def get_channel_id_by_user_id(cursor, user_id):
        cursor.execute("SELECT channel_id FROM Channels WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def get_video_ids_by_channel_id(cursor, channel_id):
        cursor.execute("SELECT vid_id FROM Videos WHERE channel_id=?", (channel_id,))
        result = cursor.fetchall()
        return [row[0] for row in result]

    channel_id = get_channel_id_by_user_id(cursor, user_id)

    if not channel_id:
        conn.close()
        return None

    data_dict = {}

    cursor.execute("SELECT * FROM Channels WHERE channel_id=?", (channel_id,))
    data_dict['Channels'] = cursor.fetchall()

    video_ids = get_video_ids_by_channel_id(cursor, channel_id)

    cursor.execute("SELECT * FROM Videos WHERE vid_id IN ({})".format(','.join(['?'] * len(video_ids))), video_ids)
    data_dict['Videos'] = cursor.fetchall()

    for table_name in ['Emoji_Frequency', 'Video_Rankings', 'VideoStats']:
        if table_name == 'VideoStats':
            cursor.execute("SELECT * FROM {} WHERE video_id IN ({})".format(table_name, ','.join(['?'] * len(video_ids))), video_ids)
            data_dict[table_name] = cursor.fetchall()
        else:
            cursor.execute("SELECT * FROM {} WHERE vid_id IN ({})".format(table_name, ','.join(['?'] * len(video_ids))), video_ids)
            data_dict[table_name] = cursor.fetchall()

    sentiment_data = []
    for vid_id in video_ids:
        cursor.execute("SELECT * FROM Comments_SentimentAnalysis WHERE vid_id=?", (vid_id,))
        sentiment_data.extend(cursor.fetchall())
    data_dict['Comments_SentimentAnalysis'] = sentiment_data

    cursor.execute("SELECT * FROM MonthlyStats WHERE channel_id=?", (channel_id,))
    data_dict['MonthlyStats'] = cursor.fetchall()

    cursor.execute("SELECT * FROM ScanInfo WHERE channel_id=?", (channel_id,))
    data_dict['ScanInfo'] = cursor.fetchall()

    return data_dict

def insert_data_into_tables(data):

    conn = sqlite3.connect('sentilyticsReplica.sqlite3')
    cursor = conn.cursor()

    # Insert data into the Channels table
    for row in data['Channels']:
        cursor.execute('''INSERT INTO Channels (user_id, channel_id, channel_title, channel_description,
                                                subscriber_count, total_videos_count, total_views_count,
                                                partial_likes_count, partial_comments_count, partial_views_count,
                                                channel_created_date, channel_logo_url)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                        row[8], row[9], row[10], row[11]))

    # Insert data into the Videos table
    for row in data['Videos']:
        cursor.execute('''INSERT INTO Videos (channel_id, vid_id, vid_title, vid_view_cnt, vid_like_cnt,
                                              vid_comment_cnt, vid_url, vid_desc, vid_duration,
                                              vid_published_at, vid_thumbnail)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                        row[8], row[9], row[10]))

    # Insert data into the Emoji_Frequency table
    for row in data['Emoji_Frequency']:
        cursor.execute('''INSERT INTO Emoji_Frequency (vid_id, highlvl_freq)
                          VALUES (?, ?)''',
                       (row[0], row[1]))

    # Insert data into the Comments_SentimentAnalysis table
    for row in data['Comments_SentimentAnalysis']:
        cursor.execute('''INSERT INTO Comments_SentimentAnalysis (vid_id, comment_id, comment, sentiment)
                          VALUES (?, ?, ?, ?)''',
                       (row[0], row[1], row[2], row[3]))

    # Insert data into the Video_Rankings table
    for row in data['Video_Rankings']:
        cursor.execute('''INSERT INTO Video_Rankings (vid_id, keyword, results_vidID, results_vidurl,
                                                      results_vidTitle, results_vidDesc, results_vidDuration,
                                                      results_vidViewcnt, results_vidDt)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))

    # Insert data into the VideoStats table
    for row in data['VideoStats']:
        cursor.execute('''INSERT INTO VideoStats (channel_id, video_id, date, vid_title, vid_view_cnt,
                                                  vid_like_cnt, vid_comment_cnt, category)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

    # Insert data into the MonthlyStats table
    for row in data['MonthlyStats']:
        cursor.execute('''INSERT INTO MonthlyStats (channel_id, date, channel_subs, overall_views)
                          VALUES (?, ?, ?, ?)''',
                       (row[0], row[1], row[2], row[3]))

    # Insert data into the ScanInfo table
    for row in data['ScanInfo']:
        cursor.execute('''INSERT INTO ScanInfo (channel_id, phase, start_time, end_time, success, notes)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (row[0], row[1], row[2], row[3], row[4], row[5]))

    conn.commit()
    
data = select_data_by_user_id("5435")
insert_data_into_tables(data)