import pymysql

from database import insert_scan_info
from getMethods import select_data_by_scan_id
from postreq import send_telegram_message

async def makeReplication(scanID,channelID):
    
    data_dict = select_data_by_scan_id(scanID)
    conn_params = {
        "host": "0.0.0.0",
        "port": 3307,                # Change to your MySQL port if necessary
        "user": "admin",
        "password": "admin",
        "db": "sentireplica",
    }
    conn = pymysql.connect(**conn_params)
    cursor = conn.cursor()

    # Insert or update data in Channels table
    channel_data = data_dict.get('channel')
    if channel_data:
        sql = '''
            INSERT INTO Channels 
            (scan_id, channel_id, channel_title, channel_description, total_videos_count, total_views_count, total_subs_count, partial_likes_count, partial_comments_count, partial_views_count, channel_created_date, channel_logo_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            channel_title = VALUES(channel_title),
            channel_description = VALUES(channel_description),
            total_videos_count = VALUES(total_videos_count),
            total_views_count = VALUES(total_views_count),
            total_subs_count = VALUES(total_subs_count),
            partial_likes_count = VALUES(partial_likes_count),
            partial_comments_count = VALUES(partial_comments_count),
            partial_views_count = VALUES(partial_views_count),
            channel_created_date = VALUES(channel_created_date),
            channel_logo_url = VALUES(channel_logo_url)
        '''
        cursor.execute(sql, (
            channel_data['scan_id'], channel_data['channel_id'], channel_data['channel_title'], channel_data['channel_description'],
            channel_data['total_videos_count'], channel_data['total_views_count'], channel_data['total_subs_count'],
            channel_data['partial_likes_count'], channel_data['partial_comments_count'], channel_data['partial_views_count'],
            channel_data['channel_created_date'], channel_data['channel_logo_url']
        ))

    # Insert or update data in Videos table
    videos_data = data_dict.get('Videos')
    if videos_data:
        for video_data in videos_data:
            sql = '''
                INSERT INTO Videos 
                (channel_id, vid_id, vid_title, vid_view_cnt, vid_like_cnt, vid_comment_cnt, vid_url, vid_desc, vid_duration, vid_published_at, vid_thumbnail)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                vid_title = VALUES(vid_title),
                vid_view_cnt = VALUES(vid_view_cnt),
                vid_like_cnt = VALUES(vid_like_cnt),
                vid_comment_cnt = VALUES(vid_comment_cnt),
                vid_url = VALUES(vid_url),
                vid_desc = VALUES(vid_desc),
                vid_duration = VALUES(vid_duration),
                vid_published_at = VALUES(vid_published_at),
                vid_thumbnail = VALUES(vid_thumbnail)
            '''
            cursor.execute(sql, (
                video_data['channel_id'], video_data['vid_id'], video_data['vid_title'], video_data['vid_view_cnt'], video_data['vid_like_cnt'],
                video_data['vid_comment_cnt'], video_data['vid_url'], video_data['vid_desc'], video_data['vid_duration'],
                video_data['vid_published_at'], video_data['vid_thumbnail']
            ))

    # Insert or update data in Emoji_Frequency table
    emoji_freq_data = data_dict.get('Emoji_Frequency')
    if emoji_freq_data:
        for emoji_data in emoji_freq_data:
            sql = '''
                INSERT INTO Emoji_Frequency 
                (vid_id, highlvl_freq)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE
                highlvl_freq = VALUES(highlvl_freq)
            '''
            cursor.execute(sql, (
                emoji_data['vid_id'], emoji_data['highlvl_freq']
            ))

    # Insert or update data in Comments_SentimentAnalysis table
    comments_sentiment_data = data_dict.get('Comments_SentimentAnalysis')
    if comments_sentiment_data:
        for comment_data in comments_sentiment_data:
            sql = '''
                INSERT INTO Comments_SentimentAnalysis 
                (vid_id, comment_id, comment, sentiment)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                comment = VALUES(comment),
                sentiment = VALUES(sentiment)
            '''
            cursor.execute(sql, (
                comment_data['vid_id'], comment_data['comment_id'], comment_data['comment'], comment_data['sentiment']
            ))

    # Insert or update data in Video_Rankings table
    video_rankings_data = data_dict.get('Video_Rankings')
    if video_rankings_data:
        for ranking_data in video_rankings_data:
            sql = '''
                INSERT INTO Video_Rankings 
                (vid_id, keyword, results_vidID, results_vidurl, results_vidTitle, results_vidDesc, results_vidDuration, results_vidViewcnt, results_vidDt)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                results_vidTitle = VALUES(results_vidTitle),
                results_vidDesc = VALUES(results_vidDesc),
                results_vidDuration = VALUES(results_vidDuration),
                results_vidViewcnt = VALUES(results_vidViewcnt),
                results_vidDt = VALUES(results_vidDt)
            '''
            cursor.execute(sql, (
                ranking_data['vid_id'], ranking_data['keyword'], ranking_data['results_vidID'], ranking_data['results_vidurl'],
                ranking_data['results_vidTitle'], ranking_data['results_vidDesc'], ranking_data['results_vidDuration'],
                ranking_data['results_vidViewcnt'], ranking_data['results_vidDt']
            ))

    # Insert or update data in VideoStats table
    video_stats_data = data_dict.get('VideoStats')
    if video_stats_data:
        for stats_data in video_stats_data:
            sql = '''
                INSERT INTO VideoStats 
                (channel_id, vid_id, date, vid_title, vid_view_cnt, vid_like_cnt, vid_comment_cnt, category)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                vid_title = VALUES(vid_title),
                vid_view_cnt = VALUES(vid_view_cnt),
                vid_like_cnt = VALUES(vid_like_cnt),
                vid_comment_cnt = VALUES(vid_comment_cnt),
                category = VALUES(category)
            '''
            cursor.execute(sql, (
                stats_data['channel_id'], stats_data['vid_id'], stats_data['date'], stats_data['vid_title'], stats_data['vid_view_cnt'],
                stats_data['vid_like_cnt'], stats_data['vid_comment_cnt'], stats_data['category']
            ))

    # Insert or update data in MonthlyStats table
    monthly_stats_data = data_dict.get('MonthlyStats')
    if monthly_stats_data:
        for stats_data in monthly_stats_data:
            sql = '''
                INSERT INTO MonthlyStats 
                (channel_id, date, channel_subs, overall_views)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                channel_subs = VALUES(channel_subs),
                overall_views = VALUES(overall_views)
            '''
            cursor.execute(sql, (
                stats_data['channel_id'], stats_data['date'], stats_data['channel_subs'], stats_data['overall_views']
            ))

    # Insert or update data in ScanInfo table
    scan_info_data = data_dict.get('ScanInfo')
    scan_info_data = [item for item in scan_info_data if item.get('phase') != 'make_replica']
    if scan_info_data:
        for info_data in scan_info_data:
            sql = '''
                INSERT INTO ScanInfo 
                (scan_id,channel_id, phase, start_time, end_time, success, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                start_time = VALUES(start_time),
                end_time = VALUES(end_time),
                success = VALUES(success),
                notes = VALUES(notes)
            '''
            cursor.execute(sql, (
                info_data['scan_id'],info_data['channel_id'], info_data['phase'], info_data['start_time'], info_data['end_time'],
                info_data['success'], info_data['notes']
            ))

    conn.commit()
    conn.close()
    
    completion_message = "Replication Done."
    await insert_scan_info(scan_id = scanID,channel_id=channelID, phase='make_replica',notes=completion_message,success=True)
    #await send_telegram_message(channelID, channelName)
   
