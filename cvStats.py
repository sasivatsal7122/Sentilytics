from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium_stealth import stealth
from pyvirtualdisplay import Display
import pandas as pd
from googleapiclient.discovery import build
import time
from datetime import datetime
# local import
from database import insert_data_to_monthly_stats,insert_data_to_video_stats,get_DevKey
from postreq import send_telegram_message
from cvutil import getLatest_videos,getMostviewed_videos,getHighestrated_videos

# set the correct path in production server
driver_executable_path = "/home/sasi/Sentilytics-rspi/chromedriver"

# display = Display(visible=0)
# display.start()

DEVELOPER_KEY,YOUTUBE_API_SERVICE_NAME,YOUTUBE_API_VERSION = get_DevKey()
youtube = build(YOUTUBE_API_SERVICE_NAME,YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

URLS = {
    "monthly": "https://socialblade.com/youtube/channel/%s/monthly",
    "latest" : "https://socialblade.com/youtube/channel/%s/videos",
    "mostviewed" : "https://socialblade.com/youtube/channel/%s/mostviewed",
    "highestrated": "https://socialblade.com/youtube/channel/%s/highestrated"
}

def get_driver():
    options=webdriver.ChromeOptions()
 
    options.add_argument("start-maximized")
    #options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-images")
    options.add_argument("--blink-settings=imagesEnabled=false")

    driver = webdriver.Chrome(options=options)
    
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
 
    
    # options = uc.ChromeOptions()
    # options.add_argument("--user-data-dir=/home/satyasasivatsal/.config/google-chrome")
    # options.add_argument("--profile-directory=Default")
    # driver = uc.Chrome(options=options,headless=True)

    # replace with this if you want to use the driver in Pi4
    # options.add_argument("--user-data-dir=/home/sasi/.config/chromium")
    # options.add_argument("--profile-directory=Default")
    #driver = webdriver.Chrome(options=options,driver_executable_path=driver_executable_path,use_subprocess=True)    
    return driver

def begin_monthlyStats(channelID,channelName):
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
    

async def start_cvStats(channelID,channelName):
    try:
        start_message = f"Monthly Stats scraping initiated for channel: {channelName}."
        await send_telegram_message({"text": start_message})
        
        begin_monthlyStats(channelID,channelName)
        
        end_message = f"Monthly Stats scraping Completed for channel: {channelName}."
        await send_telegram_message({"text": end_message})
    except Exception as e:
        print(e)
        await send_telegram_message({"text": f"Error Scraping Monthly Stats for {channelName} - {str(e)}"})
    
    max_retries = 3
    retry_delay = 5  
    
    for retry in range(1, max_retries+1):
        try:
            start_message = f"Video Stats scraping initiated for channel: {channelName}."
            await send_telegram_message({"text": start_message})

            begin_videoStats(channelID,channelName)

            end_message = f"Video Stats scraping Completed for channel: {channelName}."
            await send_telegram_message({"text": end_message})

            print("Video Stats scraping successful!")
            break

        except Exception as e:
            print(f"Error scraping Video Stats for {channelName} (Attempt {retry}/{max_retries}): {str(e)}")
            await send_telegram_message({"text": f"Error Scraping Video Stats for {channelName} - {str(e)}, TRYING AGAIN..."})

            if retry < max_retries:
                print(f"Retrying after {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Maximum number of retries reached. Exiting.")
                await send_telegram_message({"text": f"Maximum number of retries reached. Exiting. [{channelName}]"})

