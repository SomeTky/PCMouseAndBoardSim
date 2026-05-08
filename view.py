import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QLineEdit, QGroupBox, QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt
from touch import AutoClicker
from board import replay_keys, load_config


# =========================
# 首页
# =========================
class HomePage(QWidget):

    def __init__(self, stack):
        super().__init__()

        # 保存页面栈引用
        self.stack = stack

        # 页面布局
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 顶部标签
        top_label = QLabel("PC操作器")
        top_label.setAlignment(Qt.AlignCenter)

        top_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            margin: 10px;
        """)

        layout.addWidget(top_label)

        # 模拟鼠标按钮
        self.mouse_button = QPushButton("模拟鼠标")

        self.mouse_button.setFixedHeight(50)

        self.mouse_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                border-radius: 10px;
                background-color: #4CAF50;
                color: white;
            }

            QPushButton:hover {
                background-color: #45a049;
            }

            QPushButton:pressed {
                background-color: #3e8e41;
            }
        """)

        # 点击切换页面
        self.mouse_button.clicked.connect(self.goto_mouse_page)

        layout.addWidget(self.mouse_button)

        self.keyboard_button = QPushButton("模拟键盘")
        self.keyboard_button.setFixedHeight(50)
        self.keyboard_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                border-radius: 10px;
                background-color: #2196F3;
                color: white;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        self.keyboard_button.clicked.connect(self.goto_keyboard_page)
        layout.addWidget(self.keyboard_button)

        # 中间弹性空间
        layout.addStretch()

        # 底部标签
        bottom_label = QLabel("@nottky")

        bottom_label.setAlignment(Qt.AlignCenter)

        bottom_label.setStyleSheet("""
            margin: 10px;
            font-size: 14px;
        """)

        layout.addWidget(bottom_label)

    # 切换到模拟鼠标页面
    def goto_mouse_page(self):

        self.stack.setCurrentIndex(1)

    def goto_keyboard_page(self):
        self.stack.setCurrentIndex(2)   # 键盘页面索引设为 2


# =========================
# 模拟鼠标页面
# =========================
class MousePage(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        # 创建 AutoClicker 实例，默认延迟 0.5 秒
        self.clicker = AutoClicker(delay=0.5)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # ---------- 页面标题 ----------
        title = QLabel("模拟鼠标页面")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # ---------- 录制设置 ----------
        record_group = QGroupBox("录制设置")
        record_layout = QHBoxLayout()
        record_group.setLayout(record_layout)

        record_layout.addWidget(QLabel("录制点个数:"))
        self.record_num_edit = QLineEdit()
        self.record_num_edit.setPlaceholderText("例如 5")
        record_layout.addWidget(self.record_num_edit)

        self.record_btn = QPushButton("开始录制")
        self.record_btn.clicked.connect(self.start_recording)
        record_layout.addWidget(self.record_btn)

        layout.addWidget(record_group)

        # ---------- 执行设置 ----------
        play_group = QGroupBox("执行设置")
        play_layout = QVBoxLayout()
        play_group.setLayout(play_layout)

        # 重复次数行
        rounds_layout = QHBoxLayout()
        rounds_layout.addWidget(QLabel("重复次数:"))
        self.rounds_edit = QLineEdit()
        self.rounds_edit.setPlaceholderText("例如 10")
        rounds_layout.addWidget(self.rounds_edit)
        play_layout.addLayout(rounds_layout)

        # 延迟时间行
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("延迟(秒):"))
        self.delay_edit = QLineEdit()
        self.delay_edit.setPlaceholderText("例如 0.5")
        delay_layout.addWidget(self.delay_edit)
        play_layout.addLayout(delay_layout)

        self.start_btn = QPushButton("开始执行")
        self.start_btn.clicked.connect(self.start_execution)
        self.start_btn.setToolTip("点击开始执行后，请在三秒内切换到目标窗口")
        play_layout.addWidget(self.start_btn)

        layout.addWidget(play_group)

        # 弹性空间和返回按钮
        layout.addStretch()
        back_button = QPushButton("返回主页")
        back_button.setFixedHeight(50)
        back_button.clicked.connect(self.go_home)
        layout.addWidget(back_button)

    def start_recording(self):
        """开始录制鼠标位置"""
        try:
            num = int(self.record_num_edit.text())
        except ValueError:
            QMessageBox.warning(self, "输入错误", "录制点个数必须为整数")
            return

        # 调用 AutoClicker 的录制方法（可能会阻塞UI，实际项目中建议放入线程处理）
        self.record_btn.setEnabled(False)
        self.record_btn.setText("录制中...")
        QApplication.processEvents()  # 立即更新按钮状态

        # 在此调用录制（假设录制过程会监听鼠标点击直到收集够 num 个点）
        self.clicker.record_positions(num_points=num)

        self.record_btn.setText("开始录制")
        self.record_btn.setEnabled(True)
        QMessageBox.information(self, "录制完成", f"已成功录制 {num} 个位置")

    def start_execution(self):
        """开始执行鼠标操作"""
        try:
            repeat_count = int(self.rounds_edit.text())
        except ValueError:
            QMessageBox.warning(self, "输入错误", "重复次数必须为整数")
            return

        try:
            delay = float(self.delay_edit.text())
        except ValueError:
            QMessageBox.warning(self, "输入错误", "延迟时间必须为数字")
            return

        # 配置并开始执行
        self.clicker.set_config(rounds=repeat_count, delay=delay)
        # 如果 start() 是阻塞的，也建议放入线程
        self.start_btn.setEnabled(False)
        self.start_btn.setText("执行中...")
        QApplication.processEvents()

        self.clicker.start()

        self.start_btn.setText("开始执行")
        self.start_btn.setEnabled(True)
        QMessageBox.information(self, "执行完成", "操作已执行完毕")

    def go_home(self):
        self.stack.setCurrentIndex(0)

# =========================
# 模拟键盘页面
# =========================
class KeyboardPage(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 固定高度的滚动提示区
        scroll_area = QScrollArea()
        scroll_area.setFixedHeight(200)          # 高度固定
        scroll_area.setWidgetResizable(True)     # 内部控件自适应宽度

        # 提示语标签（多行文本，超出高度出现滚动条）
        self.hint_label = QLabel('''
《键盘模拟配置文件 config.json 编写说明》

config.json 应放在程序运行目录下，格式如下：
{
    "key_count": 按键个数（整数）,
    "key_sequence": [ "按键1", "按键2", ... ],
    "repeat_count": 重复执行整个序列的次数（整数）
}

■ 字段含义
- key_count：该轮序列中包含的按键数量，建议与 key_sequence 数组长度一致；
- key_sequence：需要依次按下的按键列表，顺序从左到右执行；
- repeat_count：整个按键序列自动重复执行的次数。

■ 支持的按键写法（不区分大小写）
1. 普通字符（字母、数字、符号）
  直接写单个字符即可，例如："a"、"1"、"!"、"B"、"enter"（见下面的功能键）

2. 方向键（自定义缩写）
  la  → 左箭头 (Left)
  lw  → 上箭头 (Up)
  ls  → 下箭头 (Down)
  ld  → 右箭头 (Right)

3. 删除/退格键
  del      → 退格键 (Backspace)
  backspace → 同上（也支持）

4. 常用功能键（英文名称）
  enter   → 回车键
  space   → 空格键
  tab     → Tab 键
  esc     → Esc 键
  shift   → Shift 键（单次按下即松开）
  ctrl    → Ctrl 键
  alt     → Alt 键
  up      → 上箭头
  down    → 下箭头
  left    → 左箭头
  right   → 右箭头

■ 注意事项
- 按键序列中的每个键会被顺序按下并立即释放，按键之间间隔 0.05 秒，序列重复间隔 0.2 秒；
- 开始执行前会有 3 秒倒计时，请提前切换到目标窗口；
- 如果 key_count 与实际序列长度不一致，程序会按实际序列长度继续执行；
- 配置文件首次缺失时会自动生成默认模板，请修改后重新运行。

■ 示例
{
    "key_count": 12,
    "key_sequence": ["enter", "la", "ld", "ld", "ld", "ld", "ld", "ld", "del", "1", "enter", "lw"],
    "repeat_count": 80
}
此配置表示：先按回车，然后左箭头1次、右箭头6次、退格、数字1、回车，最后上箭头，整套动作重复 80 次。
'''
        )
        self.hint_label.setWordWrap(True)
        self.hint_label.setAlignment(Qt.AlignTop)  # 文本顶部对齐
        scroll_area.setWidget(self.hint_label)
        layout.addWidget(scroll_area)

        # 开始执行按钮
        self.start_btn = QPushButton("开始执行")
        self.start_btn.clicked.connect(self.on_start)
        self.start_btn.setToolTip("点击开始执行后，请在三秒内切换到目标窗口")
        layout.addWidget(self.start_btn)

        # 弹性空间 + 返回按钮
        layout.addStretch()
        back_btn = QPushButton("返回主页")
        back_btn.clicked.connect(lambda: stack.setCurrentIndex(0))
        layout.addWidget(back_btn)

    def on_start(self):
        key_sequence, repeat_count = load_config("config.json")
        replay_keys(key_sequence, repeat_count)


# =========================
# 主窗口
# =========================
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PC操作器")

        self.setGeometry(100, 100, 400, 300)

        # 创建页面栈
        self.stack = QStackedWidget()

        # 创建页面
        self.home_page = HomePage(self.stack)

        self.mouse_page = MousePage(self.stack)

        self.keyboard_page = KeyboardPage(self.stack)

        # 添加页面到栈
        self.stack.addWidget(self.home_page)

        self.stack.addWidget(self.mouse_page)

        self.stack.addWidget(self.keyboard_page)


        # 设置中央控件
        self.setCentralWidget(self.stack)


# =========================
# 程序入口
# =========================
if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()

    window.show()

    sys.exit(app.exec_())