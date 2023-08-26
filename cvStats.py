from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium_stealth import stealth
import pandas as pd
import time

# local import
from database import insert_data_to_monthly_stats,insert_data_to_video_stats,insert_scan_info
from cvutil import getLatest_videos,getMostviewed_videos,getHighestrated_videos
from postreq import make_post_request

MAX_RETRIES = 3
RETRY_DELAY = 5  

# set the correct path in production server
driver_executable_path = "/home/sasi/Sentilytics-rspi/chromedriver"

URLS = {
    "monthly": "https://socialblade.com/youtube/channel/%s/monthly",
}

def get_driver():
    options=webdriver.ChromeOptions()
 
    options.add_argument("start-maximized")
    options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-images")
    options.add_argument("--blink-settings=imagesEnabled=false")

    driver = webdriver.Chrome(options=options)
    #driver = webdriver.Chrome(options=options,service=Service(driver_executable_path)) 
    
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win64",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )

    return driver

def begin_monthlyStats(channelID,channelName):
    try:
        print("Starting monthly stats for channel: %s"%(channelName))
        driver = get_driver()
        driver.get(URLS["monthly"]%(channelID))
        target_styles = ['width: 860px; height: 32px; line-height: 32px; background: #f8f8f8;; padding: 0px 20px; color:#444; font-size: 9pt; border-bottom: 1px solid #eee;',
                    "width: 860px; height: 32px; line-height: 32px; background: #fcfcfc; padding: 0px 20px; color:#444; font-size: 9pt; border-bottom: 1px solid #eee;"]

        wait = WebDriverWait(driver, 60)
        divs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, f'div[style*="{target_styles[0]}"], div[style*="{target_styles[1]}"]')))
        print("Found %s divs"%(len(divs)))
        data = [div.text.split() for div in divs]
        monthlyStats = []

        for _ in data:
            monthlyStats.append(
            {   
                "channel_id": channelID,
                "date": _[0] +", "+ _[1],
                "channel_subs": _[2] +", "+ _[3],
                "overall_views": _[4] +", "+ _[5]
            })
        print("Finished monthly stats for channel: %s"%(channelName))
        driver.quit()
        
        mdf = pd.DataFrame(monthlyStats)
        insert_data_to_monthly_stats(mdf)
        print("Inserted monthly stats for channel: %s"%(channelName))
    finally:
        driver.quit()

def begin_videoStats(channelID,channelName):
    print("Starting video stats for channel: %s"%(channelName))
    video_details_ls = []
    
    latestVideos = getLatest_videos(channelID)
    mostviewedVideos = getMostviewed_videos(channelID)
    highestratedVideos = getHighestrated_videos(channelID)
    
    video_details_ls.extend(latestVideos)
    video_details_ls.extend(mostviewedVideos)
    video_details_ls.extend(highestratedVideos)
    
    vdf = pd.DataFrame(video_details_ls)
    vdf['channel_id'] = channelID
    column_order = ['channel_id', 'video_id', 'date', 'title', 'view_count','like_count', 'comment_count', 'category']
    vdf = vdf[column_order]
    
    insert_data_to_video_stats(vdf)
    print("Inserted video stats for channel: %s"%(channelName))


def start_cvStats(scanID, channelID,channelName):
    
    for retry in range(1, MAX_RETRIES+1):
        try:
            insert_scan_info(scan_id = scanID,channel_id=channelID,phase="cvstats_monthly",is_start=True)
        
            begin_monthlyStats(channelID,channelName)
            
            completion_message = f"Monthly Stats scraping Completed for channel: {channelName}."
            insert_scan_info(scan_id = scanID,channel_id=channelID,phase="cvstats_monthly",notes=completion_message,success=True)
            
            print("Monthly Stats scraping successful!")
            break
        
        except Exception as e:  
            print(f"Error scraping Monthly Stats for {channelName} (Attempt {retry}/{MAX_RETRIES}): {str(e)}")
            
            if retry < MAX_RETRIES:
                print(f"Retrying after {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print("Maximum number of retries reached. Exiting.")
                error_message = f"Error Scraping Monthly Stats for {channelName} - {str(e)}"
                insert_scan_info(scan_id = scanID,channel_id=channelID,phase="cvstats_monthly",notes=error_message,success=False)
            
    
    for retry in range(1, MAX_RETRIES+1):
        try:
            insert_scan_info(scan_id = scanID,channel_id=channelID,phase="cvstats_video",is_start=True)

            begin_videoStats(channelID,channelName)

            completion_message = f"Video Stats scraping Completed for channel: {channelName}."
            insert_scan_info(scan_id = scanID,channel_id=channelID,phase="cvstats_video",notes=completion_message,success=True)

            print("Video Stats scraping successful!")
            break

        except Exception as e:
            print(f"Error scraping Video Stats for {channelName} (Attempt {retry}/{MAX_RETRIES}): {str(e)}")
            
            if retry < MAX_RETRIES:
                print(f"Retrying after {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print("Maximum number of retries reached. Exiting.")
                error_message = f"Error Scraping Video Stats for {channelName} - {str(e)}"
                insert_scan_info(scan_id = scanID,channel_id=channelID,phase="cvstats_video",notes=error_message,success=False)
            
    make_post_request(f"http://0.0.0.0:8000/make_replica/?scanID={scanID}&channelID={channelID}")
