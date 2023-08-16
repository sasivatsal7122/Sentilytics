from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver

from tqdm.auto import tqdm
import yt_dlp
import pytube
import time

from database import insert_video_rankings

driver_exceutable_path = "/home/sasi/Sentilytics-rspi/chromedriver"

def initialize_driver(options: Options):

    #driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    # uncomment in Pi4 production server, chmod +x the driver and set path in root
    driver = webdriver.Chrome(options=options, service=Service(driver_exceutable_path))
    return driver

def get_webdriverOptions():

    options = Options()
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--incognito")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins-discovery")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-logging")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--headless')
        
    return options

async def get_video_info(video_url):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'skip_download': True,
        'getduration': True,
        'getid': True,
        'getdescription': True,
        'getuploaddate': True
    }
    max_tries = 3
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        while max_tries > 0:
            try:
                info_dict = ydl.extract_info(video_url, download=False)
                duration = info_dict.get('duration')
                video_id = info_dict.get('id')
                #channel_id = info_dict.get('channel_id')
                description = info_dict.get('description')
                upload_date = info_dict.get('upload_date')
                if duration and video_id  and description and upload_date:
                    minutes, seconds = divmod(duration, 60)
                    return {
                        'duration': f'{minutes:02d}:{seconds:02d}',
                        'video_id': video_id,
                        'description': description,
                        'upload_date': upload_date
                    }
            except (yt_dlp.DownloadError,AttributeError):
                pass
            max_tries-=1
    
    return None

async def search_youtube_videos(driver: webdriver.Firefox, keyword: str, target_vid_link: str):
    
    keyword = keyword.replace(" ", "+")
    driver.get(f'https://www.youtube.com/results?search_query={keyword}')

    wait = WebDriverWait(driver, 60)
    wait.until(EC.presence_of_element_located((By.ID, "contents")))

    print("Scrolling down...")

    last_index = 0 
    target_not_found = True
    while target_not_found:
        if last_index>400:
            break
            
        video_links = driver.find_elements(By.CSS_SELECTOR, "a#video-title")
        video_links = video_links[last_index:]
        for video in video_links:
            print(video.get_attribute("href"))
            if target_vid_link in video.get_attribute("href"):
                print("==== Video FOUND =====")
                target_not_found = False
                break
            else:
                driver.execute_script("arguments[0].scrollIntoView({block: 'start', inline: 'nearest', behavior: 'smooth'});", video)
                time.sleep(0.5)
            last_index += 1
        time.sleep(5)
        
    return driver

async def scrape_video_data(driver: webdriver.Firefox) -> dict:
    """
    Scrape video data from the current YouTube search results page.
    """
    youtube_data = []
    for result in tqdm(driver.find_elements(By.CSS_SELECTOR, '.text-wrapper.style-scope.ytd-video-renderer'),desc="Processing", unit="video"):
        
        link = result.find_element(By.CSS_SELECTOR, '.title-and-badge.style-scope.ytd-video-renderer a').get_attribute('href')
        title = result.find_element(By.CSS_SELECTOR, '.title-and-badge.style-scope.ytd-video-renderer').text
        views = result.find_element(By.CSS_SELECTOR, '.style-scope ytd-video-meta-block').text.split('\n')[0]

        video_info = await get_video_info(link)
        
        if video_info:
            vid_duration = video_info['duration']
            video_id = video_info['video_id']
            dt_posted = video_info['upload_date']
            description = video_info['description']
        else:
            yt_master = pytube.YouTube(link)
            try:
                vid_duration = pytube.YouTube(link).length
            except:
                vid_duration = None
            try:
                video_id = yt_master.video_id
            except:
                video_id = None
            try:
                description = yt_master.description
            except:
                description = None
            try:
                dt_posted = yt_master.publish_date.strftime("%Y-%m-%d %H:%M:%S")
            except:
                dt_posted = None
            
        youtube_data.append({

            "Video ID" : video_id,
            "Youtube Link" :link,
            "Video Title" : title,
            "Description" : description,
            "Duration":vid_duration,
            "Views Count": views ,
            "Dt Posted": dt_posted,              
            
        })

    return youtube_data


async def start_videoRanker(videoID,keyword):
    print("Starting to Scrape....")
    print(f"Keyword : {keyword}\nVideo ID : {videoID}")
    options = get_webdriverOptions()
    print("Initializing Driver....")
    driver = initialize_driver(options=options)
    print("Driver Initialized....")
    print("Searching Youtube Videos....")
    target_vid_link = "https://www.youtube.com/watch?v=" + videoID
    await search_youtube_videos(driver=driver, keyword=keyword, target_vid_link=target_vid_link)
    print("Search Completed....")
    print("Scraping Video Data....")
    youtube_data = await scrape_video_data(driver=driver)
    print("Scraping Completed....")
    await insert_video_rankings(videoID, keyword, youtube_data)
    print("Data Inserted....")
   