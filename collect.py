import os
import sys
import time
import warnings
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from log import logger, root_logger

event_name = sys.argv[1].strip()
url = "https://polymarket.com/event/" + event_name
logger.info(f"Collecting data from {url}")

if len(sys.argv) > 2:
    scroll_time = int(sys.argv[2])
else:
    scroll_time = 10
logger.info(f"scroll_time {scroll_time}")

chromedriver_autoinstaller.install()

option = webdriver.ChromeOptions()
option.add_argument("--headless")
option.add_argument('--log-level=3')
option.add_argument("--disable-logging")
option.add_argument("--disable-notifications")
option.add_argument("--disable-popup-blocking")
os.environ['WDM_LOG_LEVEL'] = '0'
warnings.filterwarnings("ignore")
browser = webdriver.Chrome(options=option)
root_logger.handlers.clear()  # or borwser will print log
logger.debug(f"visiting {url}")
browser.get(url)
wait = WebDriverWait(browser, timeout=30)

try:
    logger.debug("waiting for activity element")
    comments_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#comments")))
    activity_elem = comments_div.find_element(By.CSS_SELECTOR, "#comments > :nth-child(3)")

    logger.debug("clicking activity element")
    browser.execute_script("window.scrollBy(0, 500)")
    time.sleep(1)
    ActionChains(browser).move_to_element(activity_elem).click().perform()
    time.sleep(1)

    logger.debug("waiting for target data element")
    target_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#comments + * > * > * > * > * > *")))

    logger.debug("creating data file")
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    file_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    f = open(f"data-{file_time}.txt", "w")
    f.write(f"{now_time}\n")

    logger.debug("scrolling to target data element")
    for i in range(scroll_time * 2):
        if i % 2 == 0:
            logger.debug(f"scrolling {(i + 1) // 2}/{scroll_time}")
        browser.execute_script("window.scrollBy(0, document.body.scrollHeight)")
        time.sleep(0.5)

    # with open("text.txt", "w") as f:
    #     f.write(target_elem.get_attribute("outerHTML"))

    logger.debug("collecting data")
    sub_element_list = target_elem.find_elements(By.XPATH, "./*")
    estimate_total = len(sub_element_list)
    logger.debug(f"data number (estimate): {estimate_total}")

    logger.debug("parse data")
    profile_list = []
    for num, i in enumerate(sub_element_list):
        if num % 10 == 0:
            logger.debug(f"now reach number {num + 1}/{estimate_total}")
        links = i.find_elements(By.XPATH, "./a")
        divs = i.find_elements(By.XPATH, "./div")
        href = name = reltime = stock = ""
        for j in links:
            href = j.get_attribute("href")
            break
        for j in divs:
            name, relatime, stock, *_ = j.text.split("\n")
            break
        if href != "":
            profile_list.append([href, name, relatime, stock])
    total = len(profile_list)
    logger.debug(f"data number (real): {total}")

    logger.debug("get distinct href profit")
    href_set = set()
    href_list = []
    distinct_num = 0
    for num, profile in enumerate(profile_list):
        href = profile[0]
        distinct = href not in href_set
        if distinct:
            distinct_num += 1
            href_list.append(href)
            href_set.add(href)
    del href_set
    logger.debug(f"distinct num: {distinct_num} in {total}")
    if len(href_list) != distinct_num:
        logger.error(f"distinct num error: {len(href_list)} != {distinct_num}")
        raise Exception(f"distinct num error: {len(href_list)} != {distinct_num}")

    logger.debug("visit distinct href profit")
    href_profit_dict = {}
    parallel_len = 5
    href_parallel_list = []
    for num, profile in enumerate(href_list):
        if num % 10 == 0:
            logger.debug(f"visiting {num + 1}/{distinct_num}")
        href_parallel_list.append(profile)
        if len(href_parallel_list) < parallel_len and num != distinct_num - 1:
            continue
        for href in href_parallel_list:
            href_exec = f"window.open('{href}')"
            browser.execute_script(href_exec)
        for _ in range(len(href_parallel_list)):
            browser.switch_to.window(browser.window_handles[-1])
            href = browser.current_url
            profit_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#__pm_layout > * > * + * + * > * + *")))
            profit = ""
            while profit == "":
                profit = profit_elem.text.lstrip("Profit/loss").strip()
            href_profit_dict[href] = profit
            browser.close()
            browser.switch_to.window(browser.window_handles[0])
        href_parallel_list.clear()
    if len(href_parallel_list) != 0:
        logger.error(f"href_parallel_list not clear: remaining {len(href_parallel_list)}")
        raise Exception(f"href_parallel_list not clear: remaining {len(href_parallel_list)}")
    if len(href_profit_dict) != distinct_num:
        logger.error(f"href_profit_dict num error: {len(href_profit_dict)} != {distinct_num}")
        raise Exception(f"href_profit_dict num error: {len(href_profit_dict)} != {distinct_num}")

    logger.debug("write data")
    for num, profile in enumerate(profile_list):
        for info in profile:
            f.write(f"{info}\n")
        f.write(f"{href_profit_dict[profile[0]]}\n")

    f.close()

except Exception as e:
    logger.error(e)

else:
    logger.info("Data collected successfully")

# while True:
#     try:
#         data = input("next order: ")
#         if data == "exit":
#             break
#         exec(data)
#     except Exception as e:
#         logger.error(e)

