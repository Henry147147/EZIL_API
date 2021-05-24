import requests
import os
import time

PATH = os.getcwd() + "\\Data\\"


def make_file(name, config_dict, type_conf, path=PATH):
    with open(path + name + "." + type_conf, "a+") as file:
        for keys, values in zip(config_dict.keys(), config_dict.values()):
            file.write(f"{keys}={values}\n")


class API:
    def __init__(self, eth_address, zil_address, check_time, coin="eth"):
        self.check_time = check_time
        self.coin = coin
        self.bot_running = True
        self.worker_data = {}
        self.session = requests
        self.url_balance = f"https://billing.ezil.me/balances/{eth_address}.{zil_address}"
        self.url_hashrate = f"https://stats.ezil.me/current_stats/{eth_address}.{zil_address}/reported"
        self.url_workers = f"https://stats.ezil.me/current_stats/{eth_address}.{zil_address}/workers"
        if not os.path.isdir(PATH):
            os.mkdir(PATH)

    def get_data(self):
        time_dict = {"1": int(time.time())}
        while self.bot_running:
            data_workers = {}

            try:
                balance_data = self.session.get(self.url_balance).json()
                hashrate_data = self.session.get(self.url_hashrate).json()
                worker_data = self.session.get(self.url_workers).json()

                current_time = str(int(time.time()))
                time_dict["2"] = int(current_time)
                delta_time = time_dict["2"] - time_dict["1"]
                print(f"Getting Data; Time Difference: {delta_time}; Time Stamp: {current_time}")

                data_workers["pool_current_hashrate"] = hashrate_data['eth'][
                    'current_hashrate']  # 30 min average hashrate
                data_workers["pool_average_hashrate"] = hashrate_data['eth'][
                    'average_hashrate']  # 3 hour average hashrate
                data_workers["pool_reported_hashrate"] = hashrate_data['reported_hashrate']  # reported hashrate

                for worker in worker_data:
                    worker_name = worker["worker"]
                    data_workers[f"current_hashrate_{worker_name}"] = worker["current_hashrate"]
                    data_workers[f"average_hashrate_{worker_name}"] = worker["average_hashrate"]
                    data_workers[f"reported_hashrate_{worker_name}"] = worker["reported_hashrate"]

                data_workers["time_stamp"] = current_time

                data_workers["eth"] = balance_data['eth']  # eth balance
                data_workers["zil"] = balance_data['zil']

                make_file("Worker_Data", {"Data": data_workers}, "Data")

                time_dict["1"] = time_dict["2"]
            except Exception:
                print("No Workers Found")

            print(f"Sleeping {self.check_time} Seconds")
            time.sleep(self.check_time)


if __name__ == "__main__":
    a = API("0x7e35e364fe255312cc34e6efed7d3f1a6c0e67a4", "zil152gs5fj0rugqe8x4fmekp2dmn5elwcea0l69es", 60)
    a.get_data()
