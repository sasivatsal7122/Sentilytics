import sqlite3
import json 

conn = sqlite3.connect('sentilytics.db')
cursor = conn.cursor()

def get_channel_info(channel_id):
    
    query = f"SELECT * FROM Channels WHERE channel_id = ?;"
    cursor.execute(query, (channel_id,))
    channel_data = cursor.fetchall()
    
    formatted_data = {}
    for row in channel_data:
        column_names = [description[0] for description in cursor.description]
        channel_info = dict(zip(column_names, row))
        channel_info['channel_logo_url'] = json.loads(channel_info['channel_logo_url'])
        formatted_data = {channel_id: channel_info}
    
    query = f"SELECT * FROM Videos WHERE channel_id = ?;"
    cursor.execute(query, (channel_id,))
    videos_data = cursor.fetchall()
    videos = []
    for row in videos_data:
        column_names = [description[0] for description in cursor.description]
        video_info = dict(zip(column_names, row))   
        videos.append(video_info)
    
    formatted_data = {"channel": formatted_data,
                      "video": videos}
    return formatted_data

def get_monthly_stats(channel_id):
    
    query = f"SELECT * FROM MonthlyStats WHERE channel_id = ?;"
    cursor.execute(query, (channel_id,))
    stats_data = cursor.fetchall()

    stats = []
    for row in stats_data:
        column_names = [description[0] for description in cursor.description]
        stats_info = dict(zip(column_names, row))
        stats.append(stats_info)
    
    return {"Monthly Stat": stats}

def get_video_stats(channel_id):

    query = f"SELECT * FROM VideoStats WHERE channel_id = ?;"
    cursor.execute(query, (channel_id,))
    stats_data = cursor.fetchall()

    video_stats = {}
    for row in stats_data:
        column_names = [description[0] for description in cursor.description]
        video_info = dict(zip(column_names, row))
        category = video_info['category']

        if category not in video_stats:
            video_stats[category] = []

        video_stats[category].append(video_info)

    return {"Video Stats": video_stats}

def get_emoji_analysis(channel_id):

    cursor.execute('''
        SELECT v.vid_id, v.vid_title, e.highlvl_freq
        FROM Videos v
        INNER JOIN Emoji_Frequency e ON v.vid_id = e.vid_id
        WHERE v.channel_id = ?
    ''', (channel_id,))
    results = cursor.fetchall()

    data = {}
    for row in results:
        vid_id, vid_title, highlvl_freq = row
        if channel_id not in data:
            data[channel_id] = []
        data[channel_id].append({
            'video_id': vid_id,
            'video_title': vid_title,
            'emoji_frequency': highlvl_freq
        })

    return data

def get_video_comments(video_id):
    
    query = '''
        SELECT C.comment_id, C.comment, SA.sentiment
        FROM Comments_SentimentAnalysis SA
        LEFT JOIN Comments_Unfiltered C ON SA.vid_id = C.vid_id AND SA.comment_id = C.comment_id
        WHERE SA.vid_id = ?
    '''

    cursor.execute(query, (video_id,))
    rows = cursor.fetchall()

    video_comments = {}

    for row in rows:
        comment_id = row[0]
        comment = row[1]
        sentiment = row[2]

        video_comments[comment_id] = {
            'Comment': comment,
            'Sentiment': sentiment
        }

    conn.close()
    import json
    with open(f'{video_id}_comments.json', 'w') as json_file:
        json.dump({video_id: video_comments}, json_file, indent=4)

    return {video_id: video_comments}


def select_data_by_user_id(user_id):
    
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
    
    conn = sqlite3.connect('sentilyticsReplica.db')
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
    