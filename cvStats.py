from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import undetected_chromedriver as webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display
import pandas as pd
import time

# local import
from database import insert_data_to_monthly_stats,insert_data_to_video_stats
from postreq import send_telegram_message

# set the correct path in production server
driver_executable_path = "/home/sasi/Sentilytics-rspi/chromedriver"

display = Display(visible=0)
display.start()

URLS = {
    "monthly": "https://socialblade.com/youtube/channel/%s/monthly",
    "latest" : "https://socialblade.com/youtube/channel/%s/videos",
    "mostviewed" : "https://socialblade.com/youtube/channel/%s/mostviewed",
    "highestrated": "https://socialblade.com/youtube/channel/%s/highestrated"
}

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    options.add_argument("--user-data-dir=/home/sasi/.config/chromium")
    options.add_argument("--profile-directory=Default")
    #driver = webdriver.Chrome(options=options,use_subprocess=True)
    # replace with this if you want to use the driver in Pi4
    driver = webdriver.Chrome(options=options,driver_executable_path=driver_executable_path,use_subprocess=True)    
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
    driver = get_driver()
    driver.get(f"https://socialblade.com/youtube/channel/{channelID}")
    wait = WebDriverWait(driver, 10)
    user_videos_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'User Videos')]")))
    user_videos_link.click()

    subsection_divs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "subsection")))
    
    videoStats = []

    def util(driver,categ):
        wait = WebDriverWait(driver, 10)
        divs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.RowRecentTable')))
        data = [div.text.split("\n") for div in divs[:20]]

        for _ in data:
            videoStats.append(
            {
                "channel_id": channelID,
                "date": _[0],
                "vid_title": _[1],
                "vid_view_cnt": _[2],
                "vid_comment_cnt": _[4],
                "category" : categ
            })
            
    # 20 Latest Videos
    print("Scraping Latest Video stats")
    util(driver,"latest")
    
    # 20 Most Viewed Videos
    print("Scraping Most Viewed Video stats")
    action = ActionChains(driver)
    action.key_down(Keys.CONTROL).click(subsection_divs[1]).key_up(Keys.CONTROL).perform()
    driver.switch_to.window(driver.window_handles[-1])
    util(driver,"mostviewed")
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(5)

    # 50 Most Liked Videos
    print("Scraping Most Liked Video stats")
    action = ActionChains(driver)
    action.key_down(Keys.CONTROL).click(subsection_divs[2]).key_up(Keys.CONTROL).perform()
    driver.switch_to.window(driver.window_handles[-1])
    util(driver,"highestrated")
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(5)

    driver.quit()
    
    print("Finished video stats for channel: %s"%(channelName))
    vdf = pd.DataFrame(videoStats)
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
