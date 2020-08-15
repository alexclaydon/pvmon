from pvmon.client import Client
import yaml
from apscheduler.schedulers.blocking import BlockingScheduler
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

RESOURCES_PATH = Path.home() / 'dev' / 'projects' / 'pvmon' / 'pvmon' / 'resources'
CLIENTS_DATA_DIR = RESOURCES_PATH / 'client-data'
CLIENTS_CONFIG_FILE = RESOURCES_PATH / 'service-cfg.yml'

class Pvmon:

    @staticmethod
    def run():
        with open(file=CLIENTS_CONFIG_FILE.as_posix(), mode="r") as f:
            all_user_data = yaml.safe_load(f)
        for key in all_user_data["users"].keys():
            if not Path.exists(CLIENTS_DATA_DIR / key):
                (CLIENTS_DATA_DIR / key).mkdir(parents=True, exist_ok=True)
        clients = {}
        for key, value in all_user_data["users"].items():
            clients[key] = Client(
                user_data=value,
                data_dir=CLIENTS_DATA_DIR / key,
            )

        for client, instance in clients.items():
            instance.download_data()
            instance.process_data()
            instance.analyse_data()
            instance.notify()

        def main():
            for client, instance in clients.items():
                instance.download_data()
                instance.process_data()
                instance.analyse_data()
                instance.notify()

            scheduler = BlockingScheduler()
            scheduler.add_job(
                main, 'interval', hours=24
            )
            scheduler.start()
