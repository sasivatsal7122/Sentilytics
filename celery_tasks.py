from celery import shared_task
import asyncio
from process import scrape_channel_info, scrape_HighLvlcomments, scrape_videos_info
from sentimentAnalysis import performSentilytics
from ytranker import start_videoRanker
from cvStats import start_cvStats
from make_replication import makeReplication

@shared_task
def scrape_channel_info_task(scanID, channel_username):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scrape_channel_info(scanID, channel_username))

@shared_task
def scrape_HighLvlcomments_task(scanID, channelID):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scrape_HighLvlcomments(scanID, channelID))

@shared_task
def performSentilytics_task(scanID, channelID):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(performSentilytics(scanID, channelID))

@shared_task
def start_videoRanker_task(videoID, keyword):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_videoRanker(videoID, keyword))

@shared_task
def start_cvStats_task(scanID, channelID, channelName):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_cvStats(scanID, channelID, channelName))

@shared_task
def makeReplication_task(scanID, channelID):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(makeReplication(scanID, channelID))
    
@shared_task
def scrape_videos_info_task(scanID, channelID,channelUsername):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scrape_videos_info(scanID, channelID,channelUsername))
