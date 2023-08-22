from celery import Celery

celeryApp = Celery(
    'senti_worker',
    broker='redis://0.0.0.0:6379/0',
    result_backend='redis://0.0.0.0:6379/1',
    task_serializer='json',
    result_serializer='json',
    timezone='UTC',
    enable_utc=True
)
celeryApp.conf.imports = ['celery_tasks']
celeryApp.conf.task_default_priority = 5  
celeryApp.conf.task_routes = {
    'celery_tasks.scrape_channel_info_task': {'priority': 10},
    'celery_tasks.scrape_videos_info_task': {'priority': 10},
    'celery_tasks.scrape_HighLvlcomments_task': {'priority': 10},
    'celery_tasks.performSentilytics_task': {'priority': 5},
    'celery_tasks.start_videoRanker_task': {'priority': 1},
    'celery_tasks.start_cvStats_task': {'priority': 5},
    'celery_tasks.makeReplication_task': {'priority': 15}, 
}
