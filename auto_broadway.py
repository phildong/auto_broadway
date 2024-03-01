# %% import and definition
import logging
import os
import random
import time

import undetected_chromedriver as uc
import yaml
from selenium.common.exceptions import ElementNotInteractableException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

USER_FILE = "users.yml"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
URLS = [
    "https://lottery.broadwaydirect.com/show/six-ny/",
    "https://lottery.broadwaydirect.com/show/sweeney-todd-ny/",
    "https://lottery.broadwaydirect.com/show/the-lion-king/",
]
LOG_PATH = "logs"
LOG_NAME = "production"
SLEEP = True
LOG_FORMAT = "%(asctime)s: %(levelname)8s - %(message)s"

# %% setup
dirname = os.path.dirname(__file__)
USER_FILE = os.path.join(dirname, USER_FILE)
LOG_PATH = os.path.join(dirname, LOG_PATH)
if SLEEP:
    time.sleep(random.random() * 5 * 60 * 60)  # sleep 0-5 hrs
os.makedirs(LOG_PATH, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(
        LOG_PATH, "{}.log".format(int(time.time()) if LOG_NAME is None else LOG_NAME)
    ),
    format=LOG_FORMAT,
    level=logging.INFO,
)
with open(USER_FILE) as uf:
    user_dict = yaml.safe_load(uf)

# %% start webdriver and enter lottery
opts = uc.ChromeOptions()
opts.add_argument("--headless=new")
opts.add_argument("--user-agent={}".format(UA))
driver = uc.Chrome(options=opts, use_subprocess=False)
for url in URLS:
    showname = list(filter(lambda s: bool(s), url.split("/")))[-1]
    for cur_user, info in user_dict.items():
        if SLEEP:
            time.sleep(random.random() * 10)  # sleep 0-10 sec
        driver.get(url)
        driver.refresh()
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "lottery-notice"))
            )
        except TimeoutException:
            driver.get_screenshot_as_file("./debug.png")
            logging.error("Unable to load lottery page for {}".format(showname))
            break
        lottery_buttons = driver.find_elements(By.CLASS_NAME, "enter-lottery-link")
        if not lottery_buttons:
            logging.error("No lottery opening for {}.".format(showname))
            break
        for ilottery in range(len(lottery_buttons)):
            driver.get(url)
            lottery_button = driver.find_elements(By.CLASS_NAME, "enter-lottery-link")[
                ilottery
            ]
            try:
                lottery_button.click()
            except ElementNotInteractableException:
                continue
            iframe = driver.find_element(By.CLASS_NAME, "fancybox-iframe")
            driver.switch_to.frame(iframe)
            driver.find_element(By.NAME, "dlslot_name_first").send_keys(
                info["first_name"]
            )
            driver.find_element(By.NAME, "dlslot_name_last").send_keys(
                info["last_name"]
            )
            qty = driver.find_element(By.NAME, "dlslot_ticket_qty")
            Select(qty).select_by_visible_text("2")
            driver.find_element(By.NAME, "dlslot_email").send_keys(info["email"])
            driver.find_element(By.NAME, "dlslot_dob_year").send_keys(info["dob"]["yy"])
            driver.find_element(By.NAME, "dlslot_dob_month").send_keys(
                info["dob"]["mm"]
            )
            driver.find_element(By.NAME, "dlslot_dob_day").send_keys(info["dob"]["dd"])
            driver.find_element(By.NAME, "dlslot_zip").send_keys(info["zip"])
            country = driver.find_element(By.NAME, "dlslot_country")
            Select(country).select_by_visible_text("USA")
            driver.execute_script("document.getElementById('dlslot_agree').click()")
            driver.find_element(By.CSS_SELECTOR, ".enter-now-button").click()
            result = driver.find_element(By.CLASS_NAME, "entry-header")
            # reason = driver.find_element(By.CLASS_NAME, "entry-content").find_element(
            #     By.TAG_NAME, "h3"
            # )
            if result.text == "SUCCESS":
                logging.info(
                    "Lottery entered for {} with {}".format(showname, cur_user)
                )
            else:
                logging.error(
                    "Unsucessful lottery for {} with {}: {}".format(
                        showname, cur_user, result.text
                    )
                )
driver.close()
