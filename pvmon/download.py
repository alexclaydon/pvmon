from liblogger.legacy import local_logger
import codecs
import datetime
import pickle
import sys
from selenium import webdriver


def config_firefox_driver(download_dir):
    try:
        options = webdriver.firefox.options.Options()
        options.headless = True
        options.set_preference("browser.download.dir", str(download_dir))
        options.set_preference("browser.download.folderList", 2)
        options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            "text/plain, text/csv, application/csv, application/excel, text/comma-separated-values, application/comma-separated-values",
        )
        options.set_preference(
            "browser.helperApps.alwaysAsk.force", False
        )
        options.set_preference(
            "browser.download.manager.showWhenStarting", False
        )
        options.set_preference("pdfjs.disabled", True)
        driver = webdriver.Firefox(
            firefox_options=options, service_log_path="geckodriver.log"
        )
        local_logger.info(f"Firefox/Selenium options successfully set")
        return driver
    except Exception as e:
        local_logger.error(
            f"Unable to set Firefox/Selenium options; returned exception {e}; exiting"
        )
        sys.exit()


def _load_cookies(driver, cookies_file):
    try:
        driver.get("https://eco-megane.jp/index.php")
    except Exception as e:
        local_logger.error(
            f"In the course of trying to load cookies, was unable to successfully navigate to ecomegane homepage; returned exception {e}; check connection to server; exiting"
        )
        sys.exit()
    try:
        cookies = pickle.load(open(cookies_file, "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        local_logger.info(f"Cookies successfully loaded")
    except FileNotFoundError as e:
        local_logger.warning(
            f"No cookies file found; returned exception {e}; skipping load"
        )


def _pickle_cookies(driver, cookies_file):
    try:
        cookies = driver.get_cookies()
    except Exception as e:
        local_logger.error(
            f"Firefox/Selenium unable to return cookies; returned exception {e}; exiting"
        )
        sys.exit()
    pickle.dump(cookies, open(cookies_file, "wb"))


# TODO: Validation library to check that provided date strings give at least 30 days worth of data
def select_data_by_dates(driver, start_date: str, end_date: str = None):
    # Switch to "by sensor" data download mode
    driver.find_element_by_css_selector(".credit_btn > label:nth-child(4)").click()
    # Set start and end dates for data download
    start_date_field = driver.find_element_by_id("measureGenerateAmountFrom")
    end_date_field = driver.find_element_by_id("measureGenerateAmountTo")
    start_date_field.clear()
    try:
        start = datetime.datetime.strptime(start_date, "%Y/%m/%d")
        start_date_field.send_keys(start.strftime("%Y/%m/%d"))
        if end_date:
            end_date_field.clear()
            end = datetime.datetime.strptime(end_date, "%Y/%m/%d")
            end_date_field.send_keys(end.strftime("%Y/%m/%d"))
    except Exception as e:
        local_logger.error(
            f"Unable to parse and/or input at least one of the provided date strings; returned exception {e}; exiting"
        )
        sys.exit()


def select_data_by_days(driver, days: int = 30):
    # Switch to "by sensor" data download mode
    driver.find_element_by_css_selector(".credit_btn > label:nth-child(4)").click()
    # Set relative start date for data download
    start_date_field = driver.find_element_by_id("measureGenerateAmountFrom")
    start_date_field.clear()
    if days < 30:
        local_logger.error(
            f"Downloading less than 30 days data will not produce enough data for a useful calculation of sensor production averages; please use a start parameter of >= 30 days; exiting"
        )
        sys.exit()
    try:
        start = datetime.datetime.now() + datetime.timedelta(-days)
        start_date_field.send_keys(start.strftime("%Y/%m/%d"))
    except Exception as e:
        local_logger.error(
            f"Unable to parse number of provided days; returned exception {e}; exiting"
        )
        sys.exit()


def encode_utf8(csv_file):
    try:
        with codecs.open(csv_file, mode="r", encoding="shift_jis") as file:
            lines = file.read()
        with codecs.open(csv_file, mode="w", encoding="utf_8") as file:
            for line in lines:
                file.write(line)
        local_logger.info("Data re-encoded into UTF-8 format.")
    except Exception as e:
        local_logger.error(
            f"Unable to successfully re-encode .csv file from shift-jis into utf-8; returned exception {e}; exiting"
        )
        sys.exit()
