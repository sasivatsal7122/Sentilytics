from celery import shared_task

from process import scrape_channel_info, scrape_HighLvlcomments, scrape_videos_info
from sentimentAnalysis import performSentilytics
from ytranker import start_videoRanker
from cvStats import start_cvStats
from make_replication import makeReplication

@shared_task
def scrape_channel_info_task(scanID, channel_username):
    scrape_channel_info(scanID, channel_username)

@shared_task
def scrape_HighLvlcomments_task(scanID, channelID):
    scrape_HighLvlcomments(scanID, channelID)

@shared_task
def performSentilytics_task(scanID, channelID):
    performSentilytics(scanID, channelID)

@shared_task
def start_videoRanker_task(videoID, keyword):
    start_videoRanker(videoID, keyword)

@shared_task
def start_cvStats_task(scanID, channelID, channelName):
    start_cvStats(scanID, channelID, channelName)

@shared_task
def makeReplication_task(scanID, channelID):
    makeReplication(scanID, channelID)
    
@shared_task
def scrape_videos_info_task(scanID, channelID,channelUsername):
    scrape_videos_info(scanID, channelID,channelUsername)
