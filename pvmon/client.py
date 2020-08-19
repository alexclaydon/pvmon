from liblogger.legacy import local_logger
from pathlib import Path
from pvmon.download import (
    config_firefox_driver,
    _load_cookies,
    _pickle_cookies,
    select_data_by_days,
    encode_utf8,
)
from pvmon.analyse import (
    load_data_for_multi_sensor_projects,
    load_data_for_single_sensor_projects,
    transform_data_for_multi_sensor_projects,
    transform_data_for_single_sensor_projects,
    analyse_data_consecutive_days_multi_sensor,
    analyse_data_consecutive_days_single_sensor
)
from pvmon.notify import log_event
from libnotify import notify_to_pushover


# TODO: Consider whether BeautifulSoup could be a drop in replacement for Selenium


class Client:
    def __init__(
            self,
            user_data: dict,
            data_dir: Path,
    ):
        self.user_data = user_data
        self.data_dir = data_dir
        self.driver = None
        self.logged_in = False
        self.csv_production_data = None
        self._locate_csv_production_data()
        self.df_production_data_multi_sensor = None
        self.df_production_data_single_sensor = None
        self.analysis_multi_sensor = None
        self.analysis_single_sensor = None

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
            local_logger.info(
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
        local_logger.info("Data successfully downloaded and re-encoded.")

    def process_data(self):
        if not self.csv_production_data:
            local_logger.info("Failed attempt to process data.")
            return (
                "There is no .csv format production data present on disk.  "
                "Please download before invoking this method."
            )
        self.df_production_data_multi_sensor = transform_data_for_multi_sensor_projects(
            load_data_for_multi_sensor_projects(self.csv_production_data)
            # relabel_data(
            #     load_data(self.csv_production_data),
            #     self.user_data["ecomegane"]["replacements"],
            # )
        )
        self.df_production_data_single_sensor = transform_data_for_single_sensor_projects(
            load_data_for_single_sensor_projects(self.csv_production_data)
        )
        msg = "Production data successfully loaded into memory and processed."
        local_logger.info(msg)

    def analyse_data(self):
        if self.df_production_data_multi_sensor is None:
            return (
                "There is no dataframe production data loaded in memory.  "
                "Please process (after downloading, if necessary) before "
                "invoking this method."
            )
        self.analysis_multi_sensor = log_event(
            analyse_data_consecutive_days_multi_sensor(
                self.df_production_data_multi_sensor, days=3
            )
        )
        self.analysis_single_sensor = log_event(
            analyse_data_consecutive_days_single_sensor(
                self.df_production_data_single_sensor, days=3
            )
        )
        local_logger.info("Data successfully analysed.")

    def notify(self):
        if not self.analysis_multi_sensor:
            local_logger.warning('Please analyse multi-sensor data at least once before calling this method.')
        if self.analysis_multi_sensor:
            notify_to_pushover(self.analysis_multi_sensor)
        if not self.analysis_single_sensor:
            return local_logger.warning('Please analyse singe-sensor data at least once before calling this method.')
        if self.analysis_single_sensor:
            notify_to_pushover(self.analysis_single_sensor)

    def _close_driver(self):
        if not self.driver:
            return "There is no driver to quit."
        self.driver.quit()
        self.driver = None
        self.logged_in = False

    def __str__(self):
        return f"Class: {self.__class__.__qualname__} "

    def __repr__(self):
        pass
