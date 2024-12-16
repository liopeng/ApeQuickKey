from disable_hotkey import open_disable_hotkey, close_disable_hotkey
from disable_mouse import open_disable_mouse, close_disable_mouse
from quick_key import open_quick_key, close_quick_key
from utils import check_path_validity, load_yml, save_yml
from reward import RewardWindow

from pathlib import Path

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
import winreg as reg
import subprocess
import sys
import os

# 全局常量
app_name = "猿快键-2.0"
app_version = 2.0

ui_path = r"static\main.ui"
logo_path = r"static\logo.png"
config_path = r"static\config.yml"
reset_config_path = r"static\reset_config.yml"


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

        global ui_path, logo_path, config_path, reset_config_path

        ui_path = os.path.join(script_dir, ui_path)
        logo_path = os.path.join(script_dir, logo_path)
        config_path = os.path.join(script_dir, config_path)
        reset_config_path = os.path.join(script_dir, reset_config_path)

        self.config = load_yml(config_path)

        if self.config["page1"]["isDisplayIcon"]:
            self.tray_icon = TrayIcon()

        # 从文件中加载UI定义
        self.ui = QUiLoader().load(ui_path)
        self.ui.setWindowTitle(app_name)
        self.setWindowTitle(app_name)
        self.setWindowIcon(QIcon(logo_path))
        # self.setGeometry(500, 200, 500, 500)  # 设置可变窗口大小
        # self.setFixedSize(500, 500) # 设置固定窗口大小
        self.setCentralWidget(self.ui)

        # 设置窗口置顶
        # self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.init_UI()

    def init_UI(self):
        # 加载页面UI
        # global
        self.ui.reward.clicked.connect(self.open_reward)

        # page1
        self.ui.isSelfStarting.stateChanged.connect(self.change_self_starting)
        self.ui.isSelfStarting.setChecked(self.config["page1"]["isSelfStarting"])

        self.ui.isDisplayIcon.stateChanged.connect(self.is_display_icon)
        self.ui.isDisplayIcon.setChecked(self.config["page1"]["isDisplayIcon"])

        self.ui.isEnableConsoleHotKey.stateChanged.connect(
            self.enable_console_hotkey_state
        )
        self.ui.isEnableConsoleHotKey.setChecked(
            self.config["page1"]["isEnableConsoleHotKey"]
        )

        self.ui.isEnableResourceManagerHotKey.stateChanged.connect(
            self.enable_resource_manager_hotkey_state
        )
        self.ui.isEnableResourceManagerHotKey.setChecked(
            self.config["page1"]["isEnableResourceManagerHotKey"]
        )

        self.ui.resetButton_1.clicked.connect(lambda checked, h=1: self.reset_config(h))
        self.ui.saveAndRebootButton_1.clicked.connect(self.save_and_reboot)

        # page2
        self.ui.consoleRecordTip.setVisible(False)
        self.ui.resourceManagerRecordTip.setVisible(False)

        self.ui.editConsoleHotkeyButton.clicked.connect(self.record_console_hotkey)
        self.ui.editResourceManagerHotkeyButton.clicked.connect(
            self.record_resource_manager_hotkey
        )

        self.ui.consoleHotKeyEdit.keySequenceChanged.connect(self.edit_console_hotkey)
        self.ui.consoleHotKeyEdit.setKeySequence(
            self.config["page2"]["consoleHotKeyEdit"]
        )

        self.ui.resourceManagerHotKeyEdit.keySequenceChanged.connect(
            self.edit_resource_manager_hotkey
        )
        self.ui.resourceManagerHotKeyEdit.setKeySequence(
            self.config["page2"]["resourceManagerHotKeyEdit"]
        )

        self.ui.consoleHotKeyType_1.clicked.connect(
            lambda checked, h=1: self.change_console_hotkey_type(h)
        )
        self.ui.consoleHotKeyType_2.clicked.connect(
            lambda checked, h=2: self.change_console_hotkey_type(h)
        )
        self.ui.consoleHotKeyType_3.clicked.connect(
            lambda checked, h=3: self.change_console_hotkey_type(h)
        )

        self.ui.resourceManagerHotKeyType_1.clicked.connect(
            lambda checked, h=1: self.change_resource_manager_hotkey_type(h)
        )
        self.ui.resourceManagerHotKeyType_2.clicked.connect(
            lambda checked, h=2: self.change_resource_manager_hotkey_type(h)
        )
        self.ui.resourceManagerHotKeyType_3.clicked.connect(
            lambda checked, h=3: self.change_resource_manager_hotkey_type(h)
        )

        # 热键类型
        console_hot_key_type = self.config["page2"]["consoleHotKeyType"]
        resource_manager_hot_key_type = self.config["page2"][
            "resourceManagerHotKeyType"
        ]

        # 设置热键类型的单选按钮
        getattr(self.ui, f"consoleHotKeyType_{console_hot_key_type}").setChecked(True)
        getattr(
            self.ui, f"resourceManagerHotKeyType_{resource_manager_hot_key_type}"
        ).setChecked(True)

        self.ui.isHotKeyAbsolute.stateChanged.connect(self.change_is_hotkey_absolute)
        self.ui.isHotKeyAbsolute.setChecked(self.config["page2"]["isHotKeyAbsolute"])

        self.ui.resetButton_2.clicked.connect(lambda checked, h=2: self.reset_config(h))
        self.ui.saveAndRebootButton_2.clicked.connect(self.save_and_reboot)

        # page3
        self.ui.consolePathEdit.editingFinished.connect(self.edit_console_path)
        self.ui.consolePathEdit.setText(self.config["page3"]["consolePathEdit"])

        self.ui.resourceManagerPathEdit.editingFinished.connect(
            self.edit_resource_manager_path
        )
        self.ui.resourceManagerPathEdit.setText(
            self.config["page3"]["resourceManagerPathEdit"]
        )

        self.ui.selectConsolePath.clicked.connect(self.select_console_path)
        self.ui.selectResourceManagerPath.clicked.connect(
            self.select_resource_manager_path
        )

        self.ui.isEnableCurrentConsolePath.stateChanged.connect(
            self.change_is_enable_current_console_path
        )
        self.ui.isEnableCurrentConsolePath.setChecked(self.config["page3"]["isEnableCurrentConsolePath"])

        self.ui.isEnableCurrentResourceManagerPath.stateChanged.connect(
            self.change_is_enable_current_resource_manager_path
        )
        self.ui.isEnableCurrentResourceManagerPath.setChecked(self.config["page3"]["isEnableCurrentResourceManagerPath"])

        self.ui.resetButton_3.clicked.connect(lambda checked, h=3: self.reset_config(h))
        self.ui.saveAndRebootButton_3.clicked.connect(self.save_and_reboot)

        # page4
        self.ui.addHotkeyButton.clicked.connect(self.add_hotkey)

        self.ui.isDisableHotkey.stateChanged.connect(self.is_disable_hotkey)
        self.ui.isDisableHotkey.setChecked(self.config["page4"]["isDisableHotkey"])

        self.ui.selectAllButton.clicked.connect(self.select_all)
        self.ui.invertButton.clicked.connect(self.invert)

        self.ui.resetButton_4.clicked.connect(lambda checked, h=4: self.reset_config(h))
        self.ui.saveAndRebootButton_4.clicked.connect(self.save_and_reboot)

        # 加载快捷键UI
        self.disable_hotkey_ui_map = {}

        for key, value in self.config["page4"]["disableHotkey"].items():
            self.add_hotkey_item_ui(key)

        # 添加快捷键事件
        for key, value in self.config["page4"]["disableHotkey"].items():
            self.add_hotkey_item_event(key)

        # page5
        self.ui.isDisableLeftClick.clicked.connect(self.change_is_disable_left)
        self.ui.isDisableLeftClick.setChecked(self.config["page5"]["isDisableLeftClick"])

        self.ui.isDisableRightClick.clicked.connect(self.change_is_disable_right)
        self.ui.isDisableRightClick.setChecked(self.config["page5"]["isDisableRightClick"])

        self.ui.isDisableMiddleClick.clicked.connect(self.change_is_disable_middle)
        self.ui.isDisableMiddleClick.setChecked(self.config["page5"]["isDisableMiddleClick"])

        self.ui.isDisableWheel.clicked.connect(self.change_is_disable_wheel)
        self.ui.isDisableWheel.setChecked(self.config["page5"]["isDisableWheel"])

        self.ui.isDisableX1Click.clicked.connect(self.change_is_disable_x1)
        self.ui.isDisableX1Click.setChecked(self.config["page5"]["isDisableX1Click"])

        self.ui.isDisableX2Click.clicked.connect(self.change_is_disable_x2)
        self.ui.isDisableX2Click.setChecked(self.config["page5"]["isDisableX2Click"])

        self.ui.isDisableMouse.clicked.connect(self.change_is_disable_mouse)
        self.ui.isDisableMouse.setChecked(self.config["page5"]["isDisableMouse"])

        self.ui.resetButton_5.clicked.connect(lambda checked, h=5: self.reset_config(h))
        self.ui.saveAndRebootButton_5.clicked.connect(self.save_and_reboot)

    # global
    def save_and_reboot(self):
        close_disable_hotkey()
        close_disable_mouse()
        close_quick_key()

        old_config = load_yml(config_path)
        if (
            str(sys.argv[0])[-4:] == ".exe"
            and self.config["page1"]["isSelfStarting"] != old_config["page1"]["isSelfStarting"]
        ):
            print("自启动修改")
            key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "ApeQuickKey"
            # app_path = '"' + os.path.abspath(sys.argv[0]) + '"'
            app_path = '"' + os.path.abspath(sys.argv[0]) + '" --no-show'
            with reg.OpenKey(
                reg.HKEY_CURRENT_USER, key, 0, reg.KEY_ALL_ACCESS
            ) as reg_key:
                if self.config["page1"]["isSelfStarting"]:
                    reg.SetValueEx(reg_key, app_name, 0, reg.REG_SZ, app_path)
                else:
                    try:
                        reg.DeleteValue(reg_key, app_name)
                    except FileNotFoundError:
                        pass

        print(self.config)
        save_yml(config_path, self.config)

        if self.tray_icon:
            self.tray_icon.tray_icon_close()

        # 重新启动
        # python = sys.executable
        # os.execl(python, python,'"' + str(sys.argv[0]) + '"')

        # subprocess.Popen([sys.executable] + sys.argv)
        # sys.exit()

        # 删除共享内存
        if shared_memory.isAttached():
            shared_memory.detach()

        if str(sys.argv[0])[-3:] == ".py":
            subprocess.Popen([sys.executable] + [sys.argv[0]])
            sys.exit()
        else:
            subprocess.Popen([sys.argv[0]])
            sys.exit()

    def reset_config(self, type):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("确认重置")
        msg_box.setText("你确定要重置配置吗？")
        yes_button = msg_box.addButton("是", QMessageBox.YesRole)
        no_button = msg_box.addButton("否", QMessageBox.NoRole)
        msg_box.setDefaultButton(no_button)
        reply = msg_box.exec()

        if msg_box.clickedButton() == no_button:
            return

        reset_config = load_yml(reset_config_path)

        if type == 1:
            self.config["page1"] = reset_config["page1"]

            self.ui.isSelfStarting.setChecked(reset_config["page1"]["isSelfStarting"])

            self.ui.isDisplayIcon.setChecked(reset_config["page1"]["isDisplayIcon"])

            self.ui.isEnableConsoleHotKey.setChecked(
                reset_config["page1"]["isEnableConsoleHotKey"]
            )

            self.ui.isEnableResourceManagerHotKey.setChecked(
                reset_config["page1"]["isEnableResourceManagerHotKey"]
            )

        elif type == 2:
            self.config["page2"] = reset_config["page2"]

            self.ui.consoleHotKeyEdit.setKeySequence(
                reset_config["page2"]["consoleHotKeyEdit"]
            )

            self.ui.resourceManagerHotKeyEdit.setKeySequence(
                reset_config["page2"]["resourceManagerHotKeyEdit"]
            )

            # 热键类型
            console_hot_key_type = reset_config["page2"]["consoleHotKeyType"]
            resource_manager_hot_key_type = reset_config["page2"][
                "resourceManagerHotKeyType"
            ]

            # 设置热键类型的单选按钮
            getattr(self.ui, f"consoleHotKeyType_{console_hot_key_type}").setChecked(True)
            getattr(
                self.ui, f"resourceManagerHotKeyType_{resource_manager_hot_key_type}"
            ).setChecked(True)

            self.ui.isHotKeyAbsolute.setChecked(reset_config["page2"]["isHotKeyAbsolute"])

        elif type == 3:
            self.config["page3"] = reset_config["page3"]

            self.ui.consolePathEdit.setText(reset_config["page3"]["consolePathEdit"])

            self.ui.resourceManagerPathEdit.setText(
                reset_config["page3"]["resourceManagerPathEdit"]
            )

            self.ui.isEnableCurrentConsolePath.setChecked(reset_config["page3"]["isEnableCurrentConsolePath"])

            self.ui.isEnableCurrentResourceManagerPath.setChecked(reset_config["page3"]["isEnableCurrentResourceManagerPath"])

        elif type == 4:
            # 删除快捷键UI
            for index in self.config["page4"]["disableHotkey"].keys():
                self.delete_disable_hotkey(index, "reset")

            self.config["page4"] = reset_config["page4"]

            self.ui.isDisableHotkey.setChecked(reset_config["page4"]["isDisableHotkey"])

            # 加载快捷键UI
            self.disable_hotkey_ui_map = {}

            for key, value in self.config["page4"]["disableHotkey"].items():
                self.add_hotkey_item_ui(key)

            # 添加快捷键事件
            for key, value in reset_config["page4"]["disableHotkey"].items():
                self.add_hotkey_item_event(key)

        elif type == 5:
            self.config["page5"] = reset_config["page5"]

            self.ui.isDisableLeftClick.setChecked(
                reset_config["page5"]["isDisableLeftClick"]
            )

            self.ui.isDisableRightClick.setChecked(
                reset_config["page5"]["isDisableRightClick"]
            )

            self.ui.isDisableMiddleClick.setChecked(
                reset_config["page5"]["isDisableMiddleClick"]
            )

            self.ui.isDisableWheel.setChecked(reset_config["page5"]["isDisableWheel"])

            self.ui.isDisableX1Click.setChecked(reset_config["page5"]["isDisableX1Click"])

            self.ui.isDisableX2Click.setChecked(reset_config["page5"]["isDisableX2Click"])

            self.ui.isDisableMouse.setChecked(reset_config["page5"]["isDisableMouse"])

        # save_yml(config_path, reset_config)

        self.message_box("重置成功", "     重置成功     ")

    def open_reward(self):
        self.reward_window = RewardWindow(logo_path)
        self.reward_window.show()

    def message_box(self, title, text):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        ok_button = msg.button(QMessageBox.Ok)
        ok_button.setText("确定")  # 修改按钮文字
        ok_button.clicked.connect(msg.close)
        QTimer.singleShot(3000, msg.close)
        msg.exec()

    # page1
    def change_self_starting(self, state):
        self.config["page1"]["isSelfStarting"] = state

    def is_display_icon(self, state):
        self.config["page1"]["isDisplayIcon"] = state

    def enable_console_hotkey_state(self, state):
        self.config["page1"]["isEnableConsoleHotKey"] = state

    def enable_resource_manager_hotkey_state(self, state):
        self.config["page1"]["isEnableResourceManagerHotKey"] = state

    # page2
    def record_console_hotkey(self):
        self.ui.consoleRecordTip.setVisible(True)
        self.ui.consoleHotKeyEdit.setFocus()

    def record_resource_manager_hotkey(self):
        self.ui.resourceManagerRecordTip.setVisible(True)
        self.ui.resourceManagerHotKeyEdit.setFocus()

    def edit_console_hotkey(self, keySequence):
        key_value = keySequence.toString()
        self.config["page2"]["consoleHotKeyEdit"] = keySequence.toString()
        self.ui.consoleRecordTip.setVisible(False)

    def edit_resource_manager_hotkey(self, keySequence):
        key_value = keySequence.toString()
        self.config["page2"]["resourceManagerHotKeyEdit"] = keySequence.toString()
        self.ui.resourceManagerRecordTip.setVisible(False)

    def change_console_hotkey_type(self, hotkey_type):
        self.config["page2"]["consoleHotKeyType"] = hotkey_type

    def change_resource_manager_hotkey_type(self, hotkey_type):
        self.config["page2"]["resourceManagerHotKeyType"] = hotkey_type

    def change_is_hotkey_absolute(self, state):
        self.config["page2"]["isHotKeyAbsolute"] = state

    # page3
    def edit_console_path(self):
        path = self.ui.consolePathEdit.text()
        res = check_path_validity(path)
        if not res:
            self.ui.consolePathEdit.setText(self.config["page3"]["consolePathEdit"])
            self.message_box("路径无效", "     路径无效     ")
            return
        self.config["page3"]["consolePathEdit"] = path

    def edit_resource_manager_path(self):
        path = self.ui.resourceManagerPathEdit.text()
        res = check_path_validity(path)
        if not res:
            self.ui.resourceManagerPathEdit.setText(
                self.config["page3"]["resourceManagerPathEdit"]
            )
            self.message_box("路径无效", "     路径无效     ")
            return
        self.config["page3"]["resourceManagerPathEdit"] = path

    def select_console_path(self):
        path = QFileDialog.getExistingDirectory(self, "请选择控制台打开的路径")
        if path:
            self.ui.consolePathEdit.setText(path)
            self.config["page3"]["consolePathEdit"] = path

    def select_resource_manager_path(self):
        path = QFileDialog.getExistingDirectory(self, "请选择资源管理器打开的路径")
        if path:
            self.ui.resourceManagerPathEdit.setText(path)
            self.config["page3"]["resourceManagerPathEdit"] = path

    def change_is_enable_current_console_path(self, state):
        self.config["page3"]["isEnableCurrentConsolePath"] = state

    def change_is_enable_current_resource_manager_path(self, state):
        self.config["page3"]["isEnableCurrentResourceManagerPath"] = state

    # page4
    def add_hotkey(self):
        new_id = max(self.config["page4"]["disableHotkey"].keys(), key=int) + 1
        self.config["page4"]["disableHotkey"][new_id] = {"hotkey": "", "enable": True}
        self.add_hotkey_item_ui(new_id)
        self.add_hotkey_item_event(new_id)

    def is_disable_hotkey(self, state):
        self.config["page4"]["isDisableHotkey"] = state

    def select_all(self):
        for key, value in self.config["page4"]["disableHotkey"].items():
            self.config["page4"]["disableHotkey"][key]["enable"] = True
            self.disable_hotkey_ui_map[f"hotkeyCheckBox{key}"].setChecked(True)

    def invert(self):
        for key, value in self.config["page4"]["disableHotkey"].items():
            self.config["page4"]["disableHotkey"][key]["enable"] = not self.config[
                "page4"
            ]["disableHotkey"][key]["enable"]
            self.disable_hotkey_ui_map[f"hotkeyCheckBox{key}"].setChecked(
                self.config["page4"]["disableHotkey"][key]["enable"]
            )

    def add_hotkey_item_ui(self, index):
        key_sequence = QKeySequenceEdit()
        key_sequence.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        key_sequence.setKeySequence(self.config["page4"]["disableHotkey"][index]["hotkey"])
        self.disable_hotkey_ui_map[f"hotkeyEdit{index}"] = key_sequence

        check_box = QCheckBox()
        check_box.setText("")
        check_box.setChecked(self.config["page4"]["disableHotkey"][index]["enable"])
        self.disable_hotkey_ui_map[f"hotkeyCheckBox{index}"] = check_box

        delete_button = QPushButton("删除")
        delete_button.setStyleSheet(
            "QPushButton {border: none;text-decoration: underline;font-size: 10px;color: blue;}"
        )
        self.disable_hotkey_ui_map[f"delete_button{index}"] = delete_button

        hotkey_item = QHBoxLayout()
        hotkey_item.addWidget(self.disable_hotkey_ui_map[f"hotkeyCheckBox{index}"])
        hotkey_item.addWidget(self.disable_hotkey_ui_map[f"hotkeyEdit{index}"])
        hotkey_item.addWidget(self.disable_hotkey_ui_map[f"delete_button{index}"])

        self.ui.hotkeyLayout.addLayout(hotkey_item)

    def add_hotkey_item_event(self, index):
        self.disable_hotkey_ui_map[f"hotkeyEdit{index}"].keySequenceChanged.connect(
            lambda checked, i=index: self.edit_disable_hotkey(i)
        )
        self.disable_hotkey_ui_map[f"hotkeyCheckBox{index}"].stateChanged.connect(
            lambda checked, i=index: self.change_is_enable_disable_hotkey(i)
        )
        self.disable_hotkey_ui_map[f"delete_button{index}"].clicked.connect(
            lambda checked, i=index: self.delete_disable_hotkey(i)
        )

    def edit_disable_hotkey(self, index):
        hotkey = self.disable_hotkey_ui_map[f"hotkeyEdit{index}"].keySequence().toString()
        self.config["page4"]["disableHotkey"][index]["hotkey"] = hotkey

    def change_is_enable_disable_hotkey(self, index):
        enable = self.disable_hotkey_ui_map[f"hotkeyCheckBox{index}"].isChecked()
        self.config["page4"]["disableHotkey"][index]["enable"] = enable

    def delete_disable_hotkey(self, index, type="normal"):
        if type != "reset":
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("删除快捷键")
            msg_box.setText("你确定要删除吗？")
            yes_button = msg_box.addButton("是", QMessageBox.YesRole)
            no_button = msg_box.addButton("否", QMessageBox.NoRole)
            msg_box.setDefaultButton(no_button)
            reply = msg_box.exec()

            if msg_box.clickedButton() == no_button:
                return

            self.config["page4"]["disableHotkey"].pop(index)

        self.ui.hotkeyLayout.removeWidget(self.disable_hotkey_ui_map[f"hotkeyCheckBox{index}"])
        self.ui.hotkeyLayout.removeWidget(self.disable_hotkey_ui_map[f"hotkeyEdit{index}"])
        self.ui.hotkeyLayout.removeWidget(self.disable_hotkey_ui_map[f"delete_button{index}"])

        self.disable_hotkey_ui_map[f"hotkeyCheckBox{index}"].deleteLater()
        self.disable_hotkey_ui_map[f"hotkeyEdit{index}"].deleteLater()
        self.disable_hotkey_ui_map[f"delete_button{index}"].deleteLater()

        self.disable_hotkey_ui_map.pop(f"hotkeyCheckBox{index}")
        self.disable_hotkey_ui_map.pop(f"hotkeyEdit{index}")
        self.disable_hotkey_ui_map.pop(f"delete_button{index}")

    # page5
    def change_is_disable_left(self, state):
        self.config["page5"]["isDisableLeftClick"] = state

    def change_is_disable_right(self, state):
        self.config["page5"]["isDisableRightClick"] = state

    def change_is_disable_middle(self, state):
        self.config["page5"]["isDisableMiddleClick"] = state

    def change_is_disable_wheel(self, state):
        self.config["page5"]["isDisableWheel"] = state

    def change_is_disable_x1(self, state):
        self.config["page5"]["isDisableX1Click"] = state

    def change_is_disable_x2(self, state):
        self.config["page5"]["isDisableX2Click"] = state

    def change_is_disable_mouse(self, state):
        self.config["page5"]["isDisableMouse"] = state


class TrayIcon:
    def __init__(self):
        self._create_tray_icon()

    def _create_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(QIcon(logo_path), parent=app)

        # 创建托盘菜单
        menu = QMenu()

        # is_disable_hotkey_action = QAction("打开主界面", app)

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

    open_disable_hotkey()
    open_disable_mouse()
    open_quick_key()

    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow()
    # 判断是否显示窗口
    if "--no-show" not in sys.argv:
        window.show()

        # 窗口置顶
        # window.raise_()

        # 窗口激活
        window.activateWindow()

    sys.exit(app.exec())
