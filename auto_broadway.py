# %% import and definition
import yaml
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

USER_FILE = "users.yml"
URL = "https://lottery.broadwaydirect.com/show/mj-ny/"


def scroll_element_into_view(driver, element):
    """Scroll element into view"""
    y = element.location["y"]
    driver.execute_script("window.scrollTo(0, {0})".format(y))


# %% start webdriver
with open(USER_FILE) as uf:
    user_dict = yaml.safe_load(uf)
# driver = webdriver.Chrome(executable_path="./chromedriver")
driver = webdriver.Firefox(executable_path="./drivers/geckodriver")
driver.maximize_window()
for cur_user, info in user_dict.items():
    driver.get(URL)
    try:
        lottery_button = driver.find_element(By.CLASS_NAME, "enter-lottery-link")
    except NoSuchElementException:
        raise NoSuchElementException("No lottery opening at now")
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
    chk = driver.find_element(By.NAME, "dlslot_agree")
    # driver.find_element(By.CSS_SELECTOR, '.enter-now-button').click()
