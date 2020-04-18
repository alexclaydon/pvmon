import yaml
from client import Client


def main():
    with open(file="service-cfg.yml", mode="r") as f:
        all_user_data = yaml.safe_load(f)
    clients = {}
    for key in all_user_data["users"].keys():
        clients[key] = Client(config_key=key)
    for key, instance in clients.items():
        instance.download_data()
        instance.process_data()
        instance.analyse_data()
        instance.notify()


if __name__ == "__main__":
    main()
