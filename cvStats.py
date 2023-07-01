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


display = Display(visible=0, size=(800, 600))
display.start()

URLS = {
    "monthly": "https://socialblade.com/youtube/channel/%s/monthly",
    "latest" : "https://socialblade.com/youtube/channel/%s/videos",
    "mostviewed" : "https://socialblade.com/youtube/channel/%s/mostviewed",
    "highestrated": "https://socialblade.com/youtube/channel/%s/highestrated"
}

def get_driver():
    options = webdriver.ChromeOptions()
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--incognito")
    options.add_argument("--ad-block")
    #options.add_argument('--headless')
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-popup-blocking")        
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins-discovery")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-logging")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options,use_subprocess=True)
    driver.maximize_window()
    return driver

def begin_monthlyStats(channelID):
    print("Starting monthly stats for channel: %s"%(channelID))
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
    print("Finished monthly stats for channel: %s"%(channelID))
    driver.quit()
    
    mdf = pd.DataFrame(monthlyStats)
    insert_data_to_monthly_stats(mdf)
    print("Inserted monthly stats for channel: %s"%(channelID))

def begin_videoStats(channelID):
    print("Starting video stats for channel: %s"%(channelID))
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
    
    print("Finished video stats for channel: %s"%(channelID))
    vdf = pd.DataFrame(videoStats)
    insert_data_to_video_stats(vdf)
    print("Inserted video stats for channel: %s"%(channelID))
    

async def start_cvStats(channelID,channelName):
    try:
        start_message = f"Monthly Stats scraping initiated for channel: {channelName}."
        await send_telegram_message({"text": start_message})
        
        begin_monthlyStats(channelID)
        
        end_message = f"Monthly Stats scraping Completed for channel: {channelName}."
        await send_telegram_message({"text": end_message})
    except Exception as e:
        print(e)
        await send_telegram_message({"text": f"Error Scraping Monthly Stats for {channelName} - {str(e)}"})
    
    try:
        start_message = f"Video Stats scraping initiated for channel: {channelName}."
        await send_telegram_message({"text": start_message})

        begin_videoStats(channelID)
        
        end_message = f"Video Stats scraping Completed for channel: {channelName}."
        await send_telegram_message({"text": end_message})
    except Exception as e:
        print(e)
        await send_telegram_message({"text": f"Error Scraping Video Stats for {channelName} - {str(e)}"}) 
    