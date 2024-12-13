from disable_hotkey import open_disable_hotkey, close_disable_hotkey
from reward import RewardWindow

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QMainWindow,
    QRadioButton,
    QToolButton,
    QCheckBox,
    QKeySequenceEdit,
    QSystemTrayIcon,
    QMenu,
    QMessageBox,
    QFileDialog,
    QSizePolicy,
)
from PySide6.QtCore import QFile, QIODevice, QTimer, Qt, QSharedMemory
from PySide6.QtNetwork import QLocalSocket, QLocalServer
from PySide6.QtGui import QIcon, QAction
from PySide6.QtUiTools import QUiLoader
from pathlib import Path
import winreg as reg
import subprocess
import yaml
import sys
import os

# 全局常量
app_name = "猿快键-1.0"
app_version = 1.0

ui_path = r"static\main.ui"
logo_path = r"static\logo.png"
config_path = r"static\config.yml"

# 全局变量
# 共享内存，用于判断程序是否已经运行
shared_memory = None

class MainWindow(QMainWindow):
    config = None
    tray_icon = None

    def __init__(self):
        super().__init__()

        # 获取脚本的绝对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))

        global ui_path, logo_path, config_path

        ui_path = os.path.join(script_dir, ui_path)
        logo_path = os.path.join(script_dir, logo_path)
        config_path = os.path.join(script_dir, config_path)

        self.config = load_config()
        if self.config["IsDisableHotkey"]:
            open_disable_hotkey()

        if self.config["IsDisplayIcon"]:
            self.tray_icon = TrayIcon()

        # 从文件中加载UI定义
        self.ui = QUiLoader().load(ui_path)
        self.ui.setWindowTitle(app_name)
        self.setWindowTitle(app_name)
        self.setWindowIcon(QIcon(logo_path))
        # self.setGeometry(500, 200, 500, 500)  # 设置可变窗口大小
        # self.setFixedSize(500, 500) # 设置固定窗口大小
        self.setCentralWidget(self.ui)

        # 按钮点击事件
        self.ui.AddHotkeyButton.clicked.connect(self.add_hotkey)
        self.ui.SelectAllButton.clicked.connect(self.select_all)
        self.ui.InvertButton.clicked.connect(self.invert)
        self.ui.SaveAndRebootButton.clicked.connect(self.save_and_reboot)

        # 复选框点击事件
        self.ui.IsDisableHotkey.stateChanged.connect(self.is_disable_hotkey_changed)
        self.ui.IsSelfStarting.stateChanged.connect(self.is_self_starting_changed)
        self.ui.IsDisplayIcon.stateChanged.connect(self.is_display_icon_changed)

        self.ui.IsDisableHotkey.setChecked(self.config["IsDisableHotkey"])
        self.ui.IsSelfStarting.setChecked(self.config["IsSelfStarting"])
        self.ui.IsDisplayIcon.setChecked(self.config["IsDisplayIcon"])

        # 加载快捷键UI
        self.hotkey_layout = self.ui.findChild(QVBoxLayout, "HotkeyLayout")

        self.hotkey_ui_map = {}

        for key, value in self.config["DisableHotkey"].items():
            self.add_hotkey_item_ui(key)

        # 添加快捷键事件
        for key, value in self.config["DisableHotkey"].items():
            self.add_hotkey_item_event(key)

        self.ui.Reward.clicked.connect(self.reward)

    # 设置事件函数
    def add_hotkey(self):
        new_id = max(self.config["DisableHotkey"].keys(), key=int) + 1
        self.config["DisableHotkey"][new_id] = {"Hotkey": "", "Enable": True}
        self.add_hotkey_item_ui(new_id)
        self.add_hotkey_item_event(new_id)

    def add_hotkey_item_ui(self, index):
        key_sequence_edit = QKeySequenceEdit()
        key_sequence_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        key_sequence_edit.setKeySequence(self.config["DisableHotkey"][index]["Hotkey"])
        self.hotkey_ui_map[f"hotkeyEdit{index}"] = key_sequence_edit

        check_box = QCheckBox()
        check_box.setText("")
        check_box.setChecked(self.config["DisableHotkey"][index]["Enable"])
        self.hotkey_ui_map[f"hotkeyCheckBox{index}"] = check_box

        delete_button = QPushButton("删除")
        delete_button.setStyleSheet(
            "QPushButton {border: none;text-decoration: underline;font-size: 10px;color: blue;}"
        )
        self.hotkey_ui_map[f"delete_button{index}"] = delete_button

        hotkey_item = QHBoxLayout()
        hotkey_item.addWidget(self.hotkey_ui_map[f"hotkeyCheckBox{index}"])
        hotkey_item.addWidget(self.hotkey_ui_map[f"hotkeyEdit{index}"])
        hotkey_item.addWidget(self.hotkey_ui_map[f"delete_button{index}"])

        self.hotkey_layout.addLayout(hotkey_item)

    def add_hotkey_item_event(self, index):
        self.hotkey_ui_map[f"hotkeyEdit{index}"].keySequenceChanged.connect(
            lambda checked, i=index: self.hotkey_edit_changed(i)
        )
        self.hotkey_ui_map[f"hotkeyCheckBox{index}"].stateChanged.connect(
            lambda checked, i=index: self.hotkey_enable_changed(i)
        )
        self.hotkey_ui_map[f"delete_button{index}"].clicked.connect(
            lambda checked, i=index: self.delete_hotkey(i)
        )

    def hotkey_edit_changed(self, index):
        hotkey = self.hotkey_ui_map[f"hotkeyEdit{index}"].keySequence().toString()
        self.config["DisableHotkey"][index]["Hotkey"] = hotkey

    def hotkey_enable_changed(self, index):
        enable = self.hotkey_ui_map[f"hotkeyCheckBox{index}"].isChecked()
        self.config["DisableHotkey"][index]["Enable"] = enable

    def delete_hotkey(self, index):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("删除快捷键")
        msg_box.setText("你确定要删除吗？")
        yes_button = msg_box.addButton("是", QMessageBox.YesRole)
        no_button = msg_box.addButton("否", QMessageBox.NoRole)
        msg_box.setDefaultButton(no_button)
        reply = msg_box.exec_()

        if msg_box.clickedButton() == no_button:
            return

        self.config["DisableHotkey"].pop(index)
        self.hotkey_layout.removeWidget(self.hotkey_ui_map[f"hotkeyCheckBox{index}"])
        self.hotkey_layout.removeWidget(self.hotkey_ui_map[f"hotkeyEdit{index}"])
        self.hotkey_layout.removeWidget(self.hotkey_ui_map[f"delete_button{index}"])
        self.hotkey_ui_map[f"hotkeyCheckBox{index}"].deleteLater()
        self.hotkey_ui_map[f"hotkeyEdit{index}"].deleteLater()
        self.hotkey_ui_map[f"delete_button{index}"].deleteLater()

    def select_all(self):
        for key, value in self.config["DisableHotkey"].items():
            self.config["DisableHotkey"][key]["Enable"] = True
            self.hotkey_ui_map[f"hotkeyCheckBox{key}"].setChecked(True)

    def invert(self):
        for key, value in self.config["DisableHotkey"].items():
            self.config["DisableHotkey"][key]["Enable"] = not self.config[
                "DisableHotkey"
            ][key]["Enable"]
            self.hotkey_ui_map[f"hotkeyCheckBox{key}"].setChecked(
                self.config["DisableHotkey"][key]["Enable"]
            )

    def save_and_reboot(self):
        close_disable_hotkey()
        old_config = load_config()
        if (
            str(sys.argv[0])[-4:] == ".exe"
            and self.config["IsSelfStarting"] != old_config["IsSelfStarting"]
        ):
            print("自启动修改")
            key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "ApeQuickKey"
            # app_path = '"' + os.path.abspath(sys.argv[0]) + '"'
            app_path = '"' + os.path.abspath(sys.argv[0]) + '" --no-show'
            with reg.OpenKey(
                reg.HKEY_CURRENT_USER, key, 0, reg.KEY_ALL_ACCESS
            ) as reg_key:
                if self.config["IsSelfStarting"]:
                    reg.SetValueEx(reg_key, app_name, 0, reg.REG_SZ, app_path)
                else:
                    try:
                        reg.DeleteValue(reg_key, app_name)
                    except FileNotFoundError:
                        pass

        print(self.config)
        open(config_path, "w").write(yaml.dump(self.config))

        if self.tray_icon:
            self.tray_icon.tray_icon_close()

        # 删除共享内存
        if shared_memory.isAttached():
            shared_memory.detach()

        if str(sys.argv[0])[-3:] == ".py":
            subprocess.Popen([sys.executable] + [sys.argv[0]])
            sys.exit()
        else:
            subprocess.Popen([sys.argv[0]])
            sys.exit()

    def is_disable_hotkey_changed(self, state):
        self.config["IsDisableHotkey"] = state

    def is_self_starting_changed(self, state):
        self.config["IsSelfStarting"] = state

    def is_display_icon_changed(self, state):
        self.config["IsDisplayIcon"] = state

    def reward(self):
        self.reward_window = RewardWindow(logo_path)
        self.reward_window.show()

class TrayIcon:
    def __init__(self):
        self._create_tray_icon()

    def _create_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(QIcon(logo_path), parent=app)

        # 创建托盘菜单
        menu = QMenu()

        open_action = QAction("打开主界面", app)
        open_action.triggered.connect(show_main_window)
        menu.addAction(open_action)

        exit_action = QAction("退出", app)
        exit_action.triggered.connect(app.quit)
        menu.addAction(exit_action)

        self.tray_icon.setContextMenu(menu)

        # 连接左键点击信号到打开主界面槽
        self.tray_icon.activated.connect(
            lambda reason: (
                show_main_window() if reason == QSystemTrayIcon.Trigger else None
            )
        )

        self.tray_icon.show()

    def tray_icon_open(self):
        self._create_tray_icon()

    def tray_icon_close(self):
        self.tray_icon.hide()
        self.tray_icon.deleteLater()


def load_config():
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config


def show_main_window():
    window.show()
    window.raise_()
    window.activateWindow()


def handle_local_socket_connection():
    socket = server.nextPendingConnection()
    if socket.waitForReadyRead(3000):
        message = socket.readAll().data().decode()
        if message == "show":
            show_main_window()
    socket.disconnectFromServer()


if __name__ == "__main__":
    shared_memory = QSharedMemory("ApeQuickKeyApplication")
    if not shared_memory.create(1):
        # 如果共享内存已经存在，说明程序已经在运行
        # 尝试连接到本地服务器并发送 'show' 消息
        socket = QLocalSocket()
        socket.connectToServer("ApeQuickKeyApplicationServer")
        if socket.waitForConnected(3000):
            socket.write(b"show")
            socket.waitForBytesWritten(3000)
            socket.disconnectFromServer()

        sys.exit(0)

    # 创建本地服务器
    server = QLocalServer()
    if not server.listen("ApeQuickKeyApplicationServer"):
        QMessageBox.warning(None, "错误", "无法启动软件。")
        print("无法启动软件。")
        sys.exit(1)
    server.newConnection.connect(handle_local_socket_connection)

    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow()
    # 判断是否显示窗口
    if "--no-show" not in sys.argv:
        window.show()

    sys.exit(app.exec())
