import os
from pathlib import Path

import yaml
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

from pvmon.client import Client

load_dotenv()

if os.getenv('DEBUG') == 'yes':
    RESOURCES_PATH = Path('/workspaces') / 'pvmon' / 'pvmon' / 'resources'
if os.getenv('CONTAINER') == 'no':
    RESOURCES_PATH = Path('pvmon') / 'resources'
else:
    RESOURCES_PATH = Path('/workspace') / 'pvmon' / 'resources'

CLIENTS_DATA_DIR = RESOURCES_PATH / 'client-data'
CLIENTS_CONFIG_FILE = RESOURCES_PATH / 'service-cfg.yml'

class Pvmon:

    @staticmethod
    def run():
        with open(file=CLIENTS_CONFIG_FILE.as_posix(), mode="r") as f:
            all_user_data = yaml.safe_load(f)
        for key in all_user_data["users"].keys():
            if not Path.exists(CLIENTS_DATA_DIR / key) or not Path.exists(CLIENTS_DATA_DIR / key / 'data'):
                (CLIENTS_DATA_DIR / key / 'data').mkdir(parents=True, exist_ok=True)
        clients = {}
        for key, value in all_user_data["users"].items():
            clients[key] = Client(
                user_data=value,
                client_dir=CLIENTS_DATA_DIR / key,
            )

        def main():
            for client, instance in clients.items():
                instance.download_data()
                instance.process_data()
                instance.analyse_data()
                instance.notify()

        main()

        if os.getenv('DEBUG') != 'yes':
            scheduler = BlockingScheduler()
            scheduler.add_job(
                main, 'interval', hours=24
            )
            scheduler.start()
