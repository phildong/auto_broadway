# %% import and definition
import logging
import os
import random
import time

import undetected_chromedriver as uc
import yaml
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

USER_FILE = "users.yml"
URL = "https://lottery.broadwaydirect.com/show/mj-ny/"
LOG_PATH = "logs"
LOG_NAME = "production"
SLEEP = False
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
driver = uc.Chrome(headless=True, use_subprocess=False)
for cur_user, info in user_dict.items():
    if SLEEP:
        time.sleep(random.random() * 10)  # sleep 0-10 sec
    driver.get(URL)
    try:
        lottery_button = driver.find_element(By.CLASS_NAME, "enter-lottery-link")
    except NoSuchElementException:
        logging.error("No lottery opening at now, closing.")
        break
    lottery_button.click()
    iframe = driver.find_element(By.CLASS_NAME, "fancybox-iframe")
    driver.switch_to.frame(iframe)
    driver.find_element(By.NAME, "dlslot_name_first").send_keys(info["first_name"])
    driver.find_element(By.NAME, "dlslot_name_last").send_keys(info["last_name"])
    qty = driver.find_element(By.NAME, "dlslot_ticket_qty")
    Select(qty).select_by_visible_text("2")
    driver.find_element(By.NAME, "dlslot_email").send_keys(info["email"])
    driver.find_element(By.NAME, "dlslot_dob_year").send_keys(info["dob"]["yy"])
    driver.find_element(By.NAME, "dlslot_dob_month").send_keys(info["dob"]["mm"])
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
        logging.info("Lottery entered for {}".format(cur_user))
    else:
        logging.error("Unsucessful lottery for {}: {}".format(cur_user, result.text))
driver.close()
