from libs.liblogger import local_logger
import yaml
from pathlib import Path
from download import (
    config_firefox_driver,
    _load_cookies,
    _pickle_cookies,
    select_data_by_days,
    encode_utf8,
)
from analyse import (
    load_data,
    relabel_data,
    transform_data,
    analyse_data_consecutive_days,
)
from notify import log_event, sms_event

# TODO: Consider whether BeautifulSoup could be a drop in replacement for Selenium


class Client:
    def __init__(self, config_key: str):
        self.config_key = config_key
        self.user_data = self._load_user_data()
        self.data_dir = Path.cwd() / "data" / self.config_key
        if not Path.exists(self.data_dir):
            self.data_dir.mkdir(parents=True, exist_ok=True)
        self.driver = None
        self.logged_in = False
        self.csv_production_data = None
        self._locate_csv_production_data()
        if self.csv_production_data:
            self.process_data()
        else:
            self.df_production_data = None
        self.analysis = None

    def _load_user_data(self, file="service-cfg.yml"):
        with open(file, "r") as f:
            all_user_data = yaml.safe_load(f)
            # Using safe_load() method is required to overcome a deficiency with the way the ordinary load() method handles numbers
        local_logger.info("User data located and parsed into memory.")
        return all_user_data["users"][self.config_key]

    def _locate_csv_production_data(self):
        for file in self.data_dir.iterdir():
            if file.is_file() and "eco_megane" in file.as_posix():
                self.csv_production_data = file.as_posix()
                return local_logger.info("CSV production data located.")

    def _login(self):
        if self.logged_in:
            return local_logger.info("Already logged in.  Proceeding to data download.")
        else:
            self.driver = config_firefox_driver(self.data_dir)
            if Path.exists(self.data_dir / "cookies.pkl"):
                _load_cookies(self.driver, self.data_dir / "cookies.pkl")
            else:
                self.driver.get("https://eco-megane.jp/index.php")
                self.driver.find_element_by_css_selector(
                    ".btn-login > a:nth-child(1) > span:nth-child(1)"
                ).click()
                mail_field = self.driver.find_element_by_css_selector("#mailaddress")
                mail_field.click()
                mail_field.clear()
                mail_field.send_keys(self.user_data["ecomegane"]["login"])
                pass_field = self.driver.find_element_by_css_selector("#password")
                pass_field.click()
                pass_field.clear()
                pass_field.send_keys(self.user_data["ecomegane"]["pass"])
                self.driver.find_element_by_css_selector(
                    ".submit > span:nth-child(3)"
                ).click()
                _pickle_cookies(
                    driver=self.driver, cookies_file=self.data_dir / "cookies.pkl"
                )
            self.logged_in = True
            return local_logger.info(
                "You've been successfully logged in.  Proceeding to data download."
            )

    def download_data(self):
        if not self.logged_in:
            self._login()
        for file in self.data_dir.iterdir():
            if file.is_file() and "eco_megane" in file.as_posix():
                file.unlink()
                local_logger.info("Old data deleted from data directory.")
        self.driver.get("https://eco-megane.jp/index.php")
        self.driver.find_element_by_id("personal_menu").click()
        self.driver.find_element_by_id("personal_edit").click()
        select_data_by_days(self.driver, days=30)
        self.driver.find_element_by_id("measureGenerateAmountBtn").click()
        local_logger.info("Data successfully downloaded.")
        for file in self.data_dir.iterdir():
            if file.is_file() and "eco_megane" in file.as_posix():
                encode_utf8(file.as_posix())
        self._locate_csv_production_data()
        self._close_driver()
        return "Data successfully downloaded and re-encoded."

    def process_data(self):
        if not self.csv_production_data:
            local_logger.info("Failed attempt to process data.")
            return (
                "There is no .csv format production data present on disk.  "
                "Please download before invoking this method."
            )
        self.df_production_data = transform_data(
            relabel_data(
                load_data(self.csv_production_data),
                self.user_data["ecomegane"]["replacements"],
            )
        )
        msg = "Production data successfully loaded into memory and processed."
        local_logger.info(msg)
        return msg

    def analyse_data(self):
        if self.df_production_data is None:
            return (
                "There is no dataframe production data loaded in memory.  "
                "Please process (after downloading, if necessary) before "
                "invoking this method."
            )
        self.analysis = log_event(
            analyse_data_consecutive_days(self.df_production_data, days=3,)
        )
        local_logger.info("Data successfully analysed.")
        return self.analysis

    def notify(self):
        sms_event(
            messages=self.analysis,
            account_sid=self.user_data["twilio"]["account_sid"],
            auth_token=self.user_data["twilio"]["auth_token"],
            to_phone=self.user_data["twilio"]["to_phone"],
            from_phone=self.user_data["twilio"]["from_phone"],
            sms_on_no_anomaly=self.user_data["user_settings"]["analyse"][
                "sms_on_no_anomaly"
            ],
        )

    def visualise_data(self):
        pass

    def _close_driver(self):
        if not self.driver:
            return "There is no driver to quit."
        self.driver.quit()
        self.driver = None
        self.logged_in = False

    def __str__(self):
        return f"Class: {self.__class__.__qualname__} "

    def __repr__(self):
        return f"Client(config_key={self.config_key})"
