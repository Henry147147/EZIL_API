from ast import literal_eval

PATH = os.getcwd() + "\\Data\\"
WORKER_SPLIT = 0.50  # used if start balance is not 0


def make_file(name, config_dict, type_conf, path=PATH):
    with open(path + name + "." + type_conf, "a+") as file:
        for keys, values in zip(config_dict.keys(), config_dict.values()):
            file.write(f"{keys}={values}\n")


def read_data(path, file_name):
    data = []
    with open(path + file_name, "r+") as config:
        lines = config.readlines()
        for line in lines:
            line = line[line.find("=") + 1:]
            line_data = literal_eval(line)
            data.append(line_data)
    return data


def eval_data():
    workers = []
    start_balance_eth = 0
    start_balance_zil = 0
    balance_eth = []
    balance_zil = []
    balance_delta_eth = []
    balance_delta_zil = []
    delta_eth_range = [0]
    time = []
    time_delta = []
    balance_workers_eth = {}
    balance_workers_zil = {}
    hashrate_workers = {}
    integral_worker = {}
    worker_percentage = {}
    b = {}
    odd = 0
    even = 0
    hashrate_pool = []
    balance_eth_delta = []
    total_integral = []
    temp_integral = 0

    files_workers = read_data(path=PATH, file_name="Worker_Data.Data")

    for worker_data in files_workers:
        index = files_workers.index(worker_data)
        for keys in worker_data.keys():
            if "average_hashrate_" in keys:
                worker = keys[17:]
                if worker not in workers:
                    workers.append(worker)
                    hashrate_workers[worker] = []
                    balance_workers_eth[worker] = 0
                    balance_workers_zil[worker] = 0
                    integral_worker[worker] = []
                    worker_percentage[worker] = []
                    b[worker] = []

        current_balance_eth = float(worker_data["eth"])
        current_balance_zil = float(worker_data["zil"])
        current_time = int(worker_data["time_stamp"])

        for worker in workers:
            current_worker_in_keys = False
            for keys in worker_data.keys():
                if worker in keys:
                    current_worker_in_keys = True
            if current_worker_in_keys:
                worker_hashrate = worker_data[f"current_hashrate_{worker}"]
                hashrate_workers[worker].append(int(worker_hashrate))
            else:
                hashrate_workers[worker].append(0)

        hashrate_pool.append(float(worker_data["pool_current_hashrate"]))

        if index > 0:
            if current_balance_eth > balance_eth[-1]:
                delta_eth = current_balance_eth - balance_eth[-1]
                balance_delta_eth.append(delta_eth)
            else:
                balance_delta_eth.append(0)
            if current_balance_zil > balance_zil[-1]:
                delta_zil = current_balance_zil - balance_zil[-1]
                balance_delta_zil.append(delta_zil)
            else:
                balance_delta_zil.append(0)

            delta_time = current_time - time[-1]
            time_delta.append(delta_time)

        else:
            start_balance_eth = current_balance_eth
            start_balance_zil = current_balance_zil
            balance_delta_eth.append(0)
            balance_delta_zil.append(0)

        balance_eth.append(current_balance_eth)
        balance_zil.append(current_balance_zil)
        time.append(current_time)

    del current_time, current_balance_zil, current_worker_in_keys, worker_hashrate, index, worker

    for d_eth, index_temp in zip(balance_delta_eth, range(len(balance_delta_eth))):
        if d_eth != 0:
            delta_eth_range.append(index_temp)

    for worker in workers:
        # if it doesn't have data for balances, it splits it between workers
        if start_balance_zil > 0:
            balance_workers_zil[worker] += start_balance_zil * WORKER_SPLIT
        if start_balance_eth > 0:
            balance_workers_eth[worker] += start_balance_eth * WORKER_SPLIT

        for index in range(len(delta_eth_range)):
            # integral of hashrate
            if index > 0:
                temp_time_delta_list = time_delta[delta_eth_range[index - 1]:delta_eth_range[index]]
                temp_hashrate_list = [hashrate_workers[worker][delta_eth_range[index - 1]:delta_eth_range[index]],
                                      temp_time_delta_list]
                while len(temp_hashrate_list[0]) < len(temp_hashrate_list[1]):
                    temp_hashrate_list[0].append(0)

                temp_hashrate_len = len(temp_hashrate_list[0])
                x = temp_hashrate_list[0]
                y = temp_hashrate_list[1]
                if temp_hashrate_len > 4:
                    # do simpsons integration:
                    # start = (delta x * h[0] + delta x * h[-1])/3
                    # odd = (delta x * h[1] + delta x * h[3]...) * (4/3)
                    # evens = (delta x * h[2] + delta x h[4]...) * (2/3)
                    start = (x[0] * y[0] + x[-1] * y[-1]) * (4 / 3)

                    for i in range(len(temp_hashrate_list)):
                        if ((temp_hashrate_len - 1) > i) and (i > 0):
                            if i % 2:
                                odd += (x[i] * y[i]) * (4 / 3)
                            else:
                                even += (x[i] * y[i]) * (2 / 3)

                    integral = start + even + odd
                    integral_worker[worker].append(integral)
                    even = 0
                    odd = 0

                elif temp_hashrate_len > 1:
                    # do trapezoid integration
                    # delta x/2(h[0] + 2*h[1] + 2*h[2]... + h[-1])
                    trap_integral = ((x[0] * y[0]) + (x[-1] * y[-1]))
                    for i in range(len(temp_hashrate_list)):
                        if ((temp_hashrate_len - 1) > i) and (i > 0):
                            trap_integral += (x[i] * y[i])
                    integral_worker[worker].append(trap_integral)

                elif temp_hashrate_len == 1:
                    # do riemann sum integration
                    # y * delta x
                    riemann_integral = y[0] * x[0]
                    integral_worker[worker].append(riemann_integral)

    del temp_hashrate_list, temp_time_delta_list, temp_hashrate_len, x, y, riemann_integral

    for index in range(len(integral_worker[workers[0]])):
        for worker in integral_worker.keys():
            temp_integral += integral_worker[worker][index]
        total_integral.append(temp_integral)
        temp_integral = 0

    del temp_integral

    for worker in workers:
        for integral_t, worker_integral in zip(total_integral, integral_worker[worker]):
            try:
                worker_percentage[worker].append(worker_integral / integral_t)
            except ZeroDivisionError:
                pass

    for delta in balance_delta_eth:
        if delta != 0:
            balance_eth_delta.append(delta)

    for worker in workers:
        for percentage, delta in zip(worker_percentage[worker], balance_eth_delta):
            balance_workers_eth[worker] += percentage * delta
            b[worker].append(balance_workers_eth[worker])

    def plot():
        import matplotlib.pyplot as plt
        time.sort(reverse=True)
        plt.xlabel = "Delta Balance index"
        plt.ylabel = "ETH Balance"
        plt.title("Index Vs ETH")

        for worker_d in workers:
            temp_x = []
            for index_d in range(len(worker_percentage[worker_d])):
                temp_x.append(index_d + 1)
            x_d = temp_x
            y_d = b[worker_d]
            plt.plot(x_d, y_d, "-", label=f"{worker_d}")

        def plot_ddx():
            d_list = []
            for local_index in range(len(delta_eth_range)):
                if local_index > 0:
                    temp_index = delta_eth_range[local_index]
                    prev_temp_index = delta_eth_range[local_index - 1]

                    delta_eth_temp = balance_eth[temp_index] - balance_eth[prev_temp_index]
                    delta_time_temp = time[temp_index] - time[prev_temp_index]
                    average_hashrate_temp = (sum(hashrate_pool[prev_temp_index:temp_index])) / (
                            temp_index - prev_temp_index)

                    d_list.append(
                        ((delta_eth_temp / delta_time_temp) / average_hashrate_temp) * 1000000 * 60 * 60 * 24 * 10)
                    # magic numbers are as follows:
                    # 1000000, convert to per mh/s,
                    # 60*60*24, convert from seconds to days,

            plt.plot(x_d, d_list, "-", label="ETH per 10 Mh/s per day")

        plt.legend()
        plt.show()

    for keys in balance_workers_eth.keys():
        print(keys, balance_workers_eth[keys])

    plot()


if __name__ == "__main__":
    eval_data()
