import yaml
from client import Client
from apscheduler.schedulers.blocking import BlockingScheduler


if __name__ == "__main__":
    with open(file="service-cfg.yml", mode="r") as f:
        all_user_data = yaml.safe_load(f)
    clients = {}
    for key in all_user_data["users"].keys():
        clients[key] = Client(config_key=key)

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
