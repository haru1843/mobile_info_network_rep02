import matplotlib.pyplot as plt
from matplotlib import rcParams
import pandas as pd
import numpy as np
import json


def main():
    rcParams["font.family"] = "sans-serif"
    rcParams["font.sans-serif"] = ["HackGen"]

    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    # 移動ありでの結果をプロット
    cell_len_list = [0.01, 0.1, 1, 10, 100, 1000]
    color_list = [f"C{i}" for i in range(len(cell_len_list))]

    for cell_len, color in zip(cell_len_list, color_list):
        with open(f"./output/sim_ave=1_cap=3_cell-len={cell_len}.json") as f:
            d = json.load(f)

        segment_time = d["segment_time"]
        sim_result = pd.DataFrame(d["output"])

        handoff_block_rate = sim_result["handoff_block_num"] / sim_result["handoff_num"]

        sim_traffic_intensity = sim_result["prob_of_reach"] * sim_result["ave_service_time"]

        ax.plot(sim_traffic_intensity, handoff_block_rate,
                color=color, alpha=0.9, label=f"$T_c={segment_time}$", lw=1.2)

    ax.set_xlim([np.min(sim_traffic_intensity), np.max(sim_traffic_intensity)])

    ax.set_xlabel("呼量")
    ax.set_ylabel("ハンドオフ呼に対する呼損率")

    ax.legend()

    ax.grid()

    plt.savefig("./img/handoff_block_rate.png")

    plt.show()


if __name__ == "__main__":
    main()
