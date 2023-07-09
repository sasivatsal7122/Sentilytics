import sqlite3

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
        formatted_data = {channel_id: channel_info}
    
    query = f"SELECT * FROM Videos WHERE channel_id = ?;"
    cursor.execute(query, (channel_id,))
    videos_data = cursor.fetchall()
    videos = []
    for row in videos_data:
        column_names = [description[0] for description in cursor.description]
        video_info = dict(zip(column_names, row))   
        videos.append(video_info)
    
    formatted_data = {"Channel Info": formatted_data,
                      "Videos Info": videos}
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


