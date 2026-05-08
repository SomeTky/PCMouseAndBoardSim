import time
from pynput import mouse
from pynput.mouse import Button, Controller as MouseController


class AutoClicker:
    def __init__(self, delay=1.0, pre_click_sleep=0.02):
        """
        :param delay: 每次点击之间的间隔时间
        :param pre_click_sleep: 移动鼠标到位置后的短暂停顿
        """
        self.target_positions = []
        self.mouse_controller = MouseController()
        self.delay = delay
        self.sleep_time = pre_click_sleep

    # ---------------------------
    # 录制模块（外部可调用）
    # ---------------------------
    def record_positions(self, num_points: int, show_log=True):
        """
        录制多个鼠标点击位置
        :param num_points: 要录制的点位数量
        :return: list[(x, y)]
        """
        self.target_positions.clear()

        if show_log:
            print(f"开始录制 {num_points} 个点位...")

        for i in range(1, num_points + 1):
            pos = self._record_single_position(i, num_points, show_log)
            if pos is None:
                raise RuntimeError("录制失败")
            self.target_positions.append(pos)

        return self.target_positions


    def _record_single_position(self, index, total, show_log=True):
        """内部：记录单个点位"""
        position = None

        if show_log:
            print(f"\n请点击第 {index}/{total} 个位置...")

        def on_click(x, y, button, pressed):
            nonlocal position
            if pressed:
                position = (x, y)
                if show_log:
                    print(f"✓ 记录点位 {index}: {position}")
                return False
            return True

        with mouse.Listener(on_click=on_click) as listener:
            listener.join()

        return position

    # ---------------------------
    # 执行参数
    # ---------------------------
    def set_config(self, rounds: int = 1, delay: float = None):
        """
        :param rounds: 轮数（0 = 无限循环）
        :param delay: 点击间隔
        """
        self.rounds = rounds
        if delay is not None:
            self.delay = delay

    # ---------------------------
    # 核心执行逻辑
    # ---------------------------
    def start(self, stop_on_keyboard=True, show_log=True):
        """
        开始自动点击
        """
        if not self.target_positions:
            raise ValueError("没有录制任何点位")

        if show_log:
            print("=== 自动点击启动 ===")
            print(f"点位数量: {len(self.target_positions)}")
            print(f"轮数: {'无限' if self.rounds == 0 else self.rounds}")
            print(f"间隔: {self.delay}s")

            print("3秒后开始...")
            for i in range(3, 0, -1):
                print(i)
                time.sleep(1)

        total_clicks = 0

        try:
            round_idx = 0

            while self.rounds == 0 or round_idx < self.rounds:
                round_idx += 1

                if show_log:
                    print(f"\n--- 第 {round_idx} 轮 ---")

                for idx, pos in enumerate(self.target_positions, 1):
                    self.mouse_controller.position = pos
                    time.sleep(self.sleep_time)

                    self.mouse_controller.click(Button.left)
                    total_clicks += 1

                    if show_log:
                        print(f"[{total_clicks}] 点击 {idx}: {pos}")

                    time.sleep(self.delay)

        except KeyboardInterrupt:
            print("\n⛔ 用户中断")

        if show_log:
            print(f"\n完成点击次数: {total_clicks}")


# ---------------------------
# 示例：外部调用方式
# ---------------------------
if __name__ == "__main__":
    clicker = AutoClicker(delay=0.5)

    # 录制 3 个点
    clicker.record_positions(num_points=3)

    # 设置 5 轮点击（0 = 无限循环）
    clicker.set_config(rounds=2)

    # 开始执行
    clicker.start()