import pymysql
import json 

conn_params = {
    "host": "0.0.0.0",
    "port": 3306,              
    "user": "admin",
    "password": "admin",
    "db": "sentilytics",
}

connection = pymysql.connect(**conn_params)
cursor = connection.cursor()

def get_channel_info(channel_id):
    
    query = f"SELECT * FROM Channels WHERE channel_id = %s;"
    cursor.execute(query, (channel_id,))
    channel_data = cursor.fetchall()
    
    formatted_data = {}
    for row in channel_data:
        column_names = [description[0] for description in cursor.description]
        channel_info = dict(zip(column_names, row))
        channel_info['channel_logo_url'] = json.loads(channel_info['channel_logo_url'])
        formatted_data = {channel_id: channel_info}
    
    query = f"SELECT * FROM Videos WHERE channel_id = %s;"
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
    
    query = f"SELECT * FROM MonthlyStats WHERE channel_id = %s;"
    cursor.execute(query, (channel_id,))
    stats_data = cursor.fetchall()

    stats = []
    for row in stats_data:
        column_names = [description[0] for description in cursor.description]
        stats_info = dict(zip(column_names, row))
        stats.append(stats_info)
    
    return {"Monthly Stat": stats}

def get_video_stats(channel_id):

    query = f"SELECT * FROM VideoStats WHERE channel_id = %s;"
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
        WHERE v.channel_id = %s
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

def select_data_by_scan_id(scan_id):
    
    data_dict = {}
    
    def get_channel_id_by_scan_id(cursor, scan_id):
        cursor.execute("SELECT channel_id FROM Channels WHERE scan_id=%s", (scan_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def get_video_ids_by_channel_id(cursor, channel_id):
        cursor.execute("SELECT vid_id FROM Videos WHERE channel_id=%s", (channel_id,))
        result = cursor.fetchall()
        return [row[0] for row in result]
    
    channel_id = get_channel_id_by_scan_id(cursor, scan_id)

    if not channel_id:
        return "Given Scan ID not found"

    # =========== CHANNELS TABLE DATA ===========
    cursor.execute("SELECT * FROM Channels WHERE channel_id=%s", (channel_id,))
    channel_columns = [column[0] for column in cursor.description]

    cursor.execute("SELECT * FROM Channels WHERE channel_id=%s", (channel_id,))
    channel_data = cursor.fetchone()
    data_dict['channel'] = dict(zip(channel_columns, channel_data))

    video_ids = get_video_ids_by_channel_id(cursor, channel_id)

    # =========== VIDEOS TABLE DATA ===========
    cursor.execute("SELECT * FROM Videos WHERE vid_id IN ({})".format(','.join(['%s'] * len(video_ids))), video_ids)
    video_columns = [column[0] for column in cursor.description]

    cursor.execute("SELECT * FROM Videos WHERE vid_id IN ({})".format(','.join(['%s'] * len(video_ids))), video_ids)
    video_data = cursor.fetchall()
    data_dict['Videos'] = [dict(zip(video_columns, row)) for row in video_data]

    # =========== OTHER TABLE DATA ===========
    for table_name in ['Emoji_Frequency', 'Video_Rankings']:
        cursor.execute("SELECT * FROM {} WHERE vid_id IN ({})".format(table_name, ','.join(['%s'] * len(video_ids))), video_ids)
        table_columns = [column[0] for column in cursor.description]
        table_data = cursor.fetchall()
        data_dict[table_name] = [dict(zip(table_columns, row)) for row in table_data]

    # =========== SENTIMENT ANALYSIS  TABLE DATA ===========
    sentiment_data = []; 
    for vid_id in video_ids:
        cursor.execute("SELECT * FROM Comments_SentimentAnalysis WHERE vid_id=%s", (vid_id,))
        sentiment_data.extend(cursor.fetchall())
    sentiment_columns = [column[0] for column in cursor.description]
    data_dict['Comments_SentimentAnalysis'] = [dict(zip(sentiment_columns, row)) for row in sentiment_data]

    # =========== MONTHLY STATS TABLE DATA ===========
    cursor.execute("SELECT * FROM MonthlyStats WHERE channel_id=%s", (channel_id,))
    monthly_stats_columns = [column[0] for column in cursor.description]

    cursor.execute("SELECT * FROM MonthlyStats WHERE channel_id=%s", (channel_id,))
    monthly_stats_data = cursor.fetchall()
    data_dict['MonthlyStats'] = [dict(zip(monthly_stats_columns, row)) for row in monthly_stats_data]
    
    # =========== VIDEO STATS TABLE DATA ===========
    cursor.execute("SELECT * FROM VideoStats WHERE channel_id=%s", (channel_id,))
    video_stats_columns = [column[0] for column in cursor.description]

    cursor.execute("SELECT * FROM VideoStats WHERE channel_id=%s", (channel_id,))
    video_stats_data = cursor.fetchall()
    data_dict['VideoStats'] = [dict(zip(video_stats_columns, row)) for row in video_stats_data]

    # =========== SCAN INFO TABLE DATA ===========
    cursor.execute("SELECT * FROM ScanInfo WHERE scan_id=%s", (scan_id,))
    scan_info_columns = [column[0] for column in cursor.description]

    cursor.execute("SELECT * FROM ScanInfo WHERE scan_id=%s", (scan_id,))
    scan_info_data = cursor.fetchall()
    data_dict['ScanInfo'] = [dict(zip(scan_info_columns, row)) for row in scan_info_data]
   
    return data_dict

