import numpy as np
from typing import List, Tuple
import pandas as pd
import random
import json


class MobileToken:
    """
    高速道路においてサービスを受ける移動体端末
    """

    def __init__(self, belonging_cell_idx: int, cell_length: float, service_time: float, v: float = 10.0):
        """
        Params
        ------------------------------
        belonging_cell_idx : int
            端末が所属している初期のセル
        cell_length : float
            各セルの長さ
        """
        # 端末の移動速度
        self._v: float = v

        # 端末のサービス利用残り時間
        self._remain_service_time: float = service_time

        # 端末が所属しているセルの番号
        self.belonging_cell_idx: int = belonging_cell_idx

        # 1つのセルの長さ. 各セルにおいて固定長.
        self._cell_length: float = cell_length

        # ハンドオフまでの時間, 初期値は [0.0, 最大時間) の範囲で値をとる
        self._time_to_handoff: float = random.random() * self._cell_length / self._v

    def handoff(self, cell_num: int):
        """
        ハンドオフ時の処理を行います.
            1. ハンドオフまでの時間のリセット
            2. 次のセルへ移動

        Params
        ------------------------------
        cell_num : int
            サービスエリアにおける総セル数
        """
        self._time_to_handoff = self._cell_length / self._v
        self.belonging_cell_idx = (self.belonging_cell_idx + 1) % cell_num

    def get_next_event(self) -> Tuple[str, float]:
        """
        この端末における次に発生するイベントの情報を取得します.

        Returns
        ------------------------------
        event_name : str
            次に発生するイベント名
        time_to_next_event : float
            次に発生するイベントまでの時間
        """
        if self._time_to_handoff >= self._remain_service_time:
            return "close", self._remain_service_time
        else:
            return "handoff", self._time_to_handoff

    def passage(self, passage_time: float):
        """
        時間経過に対して, 内部パラメータの適用を行います.

        Params
        ------------------------------
        passage_time: float
            経過時間
        """
        self._remain_service_time -= passage_time
        self._time_to_handoff -= passage_time


class ServiceAreaManager:
    """
    リング状サービスエリアの管理を行うクラス
    """

    def __init__(self, cap_size: int, cell_num: int, cell_length: float):
        """
        Params
        ------------------------------
        cap_size : int
            各セルにおける許容量
        cell_num : int
            サービスエリアの全体のセル総数
        cell_length : float
            サービスエリアの1つ1つのセルの長さ
        """
        # サービスエリアの空き具合
        self._usage_conditions: List[int] = [cap_size] * cell_num

        # サービスエリアの全体のセル総数
        self._cell_num = cell_num

        # サービスを受けている端末を格納する配列
        self._in_service: List[MobileToken] = []

        # 各セルの長さ(距離)
        self._cell_length = cell_length

    def _sort(self):
        """
        イベントが来る順に配列をソートする
        """
        self._in_service.sort(key=lambda x: x.get_next_event()[1])

    def get_first_token(self) -> MobileToken:
        """
        サービス享受中のトークンの内, もっともイベント発生が速いトークンを取得します
        (提供中のサービスが無い場合はValueErrorが発生)

        Return
        ------------------------------------
        first_token : MobileToken
            サービス内でもっとも直近にイベントが発生するMobileTokenインスタンス
        """
        if len(self._in_service) == 0:
            raise ValueError("提供中のサービスが存在しません")
        return self._in_service[0]

    def get_next_event(self) -> Tuple[str, float]:
        """
        サービス中のトークン群において, 一番先に発生するイベントの情報を返します.

        Returns
        ---------------------------------
        event_name : str
            発生するイベント名
        time_to_event_occurrence : float
            そのイベントが発生するまでの時間
        """
        if len(self._in_service) == 0:
            return "NO_TOKEN", np.inf
        return self._in_service[0].get_next_event()

    def call(self, service_time: float) -> bool:
        """
        サービスエリアにおける呼の生起に対する処理を行います.

        Param
        ------------------------------------
        service_time : float
            その呼のサービス享受時間

        Return
        ---------------------------------
        is_successfull : bool
            呼損ならFalse
        """
        target_cell_idx = self._get_random_cell_idx()
        if self._allocation(target_cell_idx):
            self._in_service.append(MobileToken(target_cell_idx, self._cell_length, service_time))
            self._sort()
            return True
        else:
            return False

    def close(self):
        """
        サービスエリアにおける呼の終了に対する処理を行います.
        """
        self._release(self._in_service[0].belonging_cell_idx)
        self._in_service.pop(0)

    def handoff(self) -> bool:
        """
        サービスエリアにおけるハンドオフに対する処理を行います.

        Return
        ---------------------------------
        is_successfull : bool
            呼損ならFalse
        """
        target_cell_idx = self._in_service[0].belonging_cell_idx
        self._release(target_cell_idx)

        target_cell_idx = (target_cell_idx + 1) % self._cell_num
        if self._allocation(target_cell_idx):  # handoff成功
            self._in_service[0].handoff(self._cell_num)
            self._sort()
            return True
        else:  # handoff失敗
            self._in_service.pop(0)
            return False

    def advance_time(self, time: float) -> None:
        """
        サービスエリア全体の時間を進めます.

        Param
        ---------------------------------
        time : float
            経過する時間
        """
        for idx in range(len(self._in_service)):
            self._in_service[idx].passage(time)

    def _get_random_cell_idx(self) -> int:
        """
        一様にランダムで, セル番号を返します.

        Return
        -----------------------------------
        cell_idx : int
            ランダムなセル番号
        """
        return random.randint(0, self._cell_num-1)

    def _allocation(self, target_cell_idx: int) -> bool:
        """
        Param
        ------------------------------
        target_cell_idx : int
            割り当て対象セルのインデックス

        Return
        ------------------------------
        succeed : bool
            対象セルにおけるサービスの割当が成功した場合->True
        """
        if self._usage_conditions[target_cell_idx] > 0:
            self._usage_conditions[target_cell_idx] -= 1
            return True
        else:
            return False

    def _release(self, target_cell_idx: int):
        """
        Param
        ------------------------------
        target_cell_idx : int
            解放対象セルのインデックス
        """
        self._usage_conditions[target_cell_idx] += 1


class Simulator:
    """
    シミュレーションを行うためのクラス
    """

    def __init__(self, prob_of_reach: float, ave_service_time: float, capacity: int = 5, cell_num: int = 5, cell_length: int = 10):
        """
        Params
        --------------------------------
        prob_of_reach: float
            シミュレーションにおける到着率
        ave_service_time: float
            シミュレーションにおける平均サービス時間
        capacity: int (default=5)
            システムの容量
        cell_num: int (default=5)
            サービスエリアにおけるセル数
        """
        self._lam: float = prob_of_reach
        self._mu: float = 1.0 / ave_service_time
        self._traffic_intensity: float = self._lam / self._mu

        self.capacity: int = capacity

        self._in_service: List[MobileToken] = []

        self.sa_manager: ServiceAreaManager = ServiceAreaManager(
            cap_size=capacity,
            cell_num=cell_num,
            cell_length=cell_length
        )

    def _get_service_time(self) -> float:
        """
        サービス適用時間を計算し取得します
        """
        return float(np.random.exponential(1.0 / self._mu, size=1))

    def _get_start_time_remaining(self) -> float:
        """
        サービス開始までの時間を算出し取得します
        """
        return float(np.random.exponential(1.0 / self._lam, size=1))

    def run(self, stop_all_call: int) -> Tuple[int, int, int, int]:
        call_block_num: int = 0
        call_num: int = 0

        handoff_block_num: int = 0
        handoff_num: int = 0

        time_to_call: float = self._get_start_time_remaining()

        while True:
            if call_num >= stop_all_call:
                break

            event_name, time_to_next_event = self.sa_manager.get_next_event()

            if time_to_call < time_to_next_event:
                event_name = "call"
                time_to_next_event = time_to_call
            elif time_to_next_event < time_to_call:
                pass
            else:
                raise NotImplementedError("生起と終了が同時に発生しました")

            self.sa_manager.advance_time(time_to_next_event)
            time_to_call -= time_to_next_event

            if event_name == "call":
                call_num += 1
                if not self.sa_manager.call(self._get_service_time()):
                    call_block_num += 1
                time_to_call = self._get_start_time_remaining()
            elif event_name == "close":
                self.sa_manager.close()
            elif event_name == "handoff":
                call_num += 1  # ハンドオフの流入時に呼の生起をカウントするかどうか
                handoff_num += 1
                if not self.sa_manager.handoff():
                    call_block_num += 1
                    handoff_block_num += 1
            else:
                raise ValueError(f"予期せぬイベント'{event_name}'が発生しました")

        return call_num, call_block_num, handoff_num, handoff_block_num

    def get_traffic_intensity(self):
        return self._traffic_intensity


def main(cell_length):
    prob_of_reach_list = np.logspace(0.1, 9, 100, base=2)
    ave_service_time = 1
    capacity = 3
    cell_num = 5
    stop_all_call = 100000

    # cell_length = 9

    output_list = [{}] * len(prob_of_reach_list)

    for i, prob_of_reach in enumerate(prob_of_reach_list):
        print(f"@ {i:04d} : {prob_of_reach}")

        sim = Simulator(
            prob_of_reach=prob_of_reach,
            ave_service_time=ave_service_time,
            capacity=capacity,
            cell_num=cell_num,
            cell_length=cell_length
        )

        traffic_intensity = sim.get_traffic_intensity()
        print("---- "*3, "params", "---- "*3)
        print(f"到着率(λ) = {prob_of_reach}")
        print(f"保留時間(1/μ) = {ave_service_time}")
        print(f"呼量(a) = {traffic_intensity}")
        print()

        call_num, call_block_num, handoff_num, handoff_block_num = sim.run(
            stop_all_call=stop_all_call)
        print("---- "*3, "result", "---- "*3)
        print(f"全呼 = {call_num}")
        print(f"呼損 = {call_block_num}")
        print(call_block_num)
        print(call_num)
        print(f"呼損率 = {call_block_num / call_num}")
        print("\n\n")

        output_list[i] = {
            "prob_of_reach": prob_of_reach,
            "ave_service_time": ave_service_time,
            "traffic_intensity": traffic_intensity,
            "capacity": capacity,
            "call_num": call_num,
            "call_block_num": call_block_num,
            "handoff_num": handoff_num,
            "handoff_block_num": handoff_block_num,
            "block_rate": call_block_num / call_num
        }

    with open(f"./output/sim_ave={ave_service_time}_cap={capacity}_cell-len={cell_length}.json",
              mode="w") as f:
        json.dump({
            "segment_time": cell_length / 10.0,
            "output": output_list
        }, f, indent=2)


if __name__ == "__main__":
    for cell_length in [0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000]:
        main(cell_length)
