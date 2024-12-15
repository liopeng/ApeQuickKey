from utils import load_yml
from hotkey_util import hotkey_format

from itertools import product
import subprocess
import atexit
import os

config_path = r"static\config.yml"
disable_keyboard_path = r"tool\disable_keyboard.exe"

config = None

thread_disable_keyboard = None

def open_disable_hotkey():
    global config_path, disable_keyboard_path, config

    script_dir = os.path.dirname(os.path.abspath(__file__))

    config_path = os.path.join(script_dir, config_path)
    config = load_yml(config_path)

    disable_keyboard_command = [os.path.join(script_dir, disable_keyboard_path)]

    if config["page4"]["isDisableHotkey"]:
        for key, value in config["page4"]["disableHotkey"].items():
            if value["enable"] and value["hotkey"] != "":
                disable_keyboard_command += hotkey_format(value["hotkey"])

    if config["page2"]["isHotKeyAbsolute"]:
        if config["page1"]["isEnableConsoleHotKey"] and config["page2"]["consoleHotKeyType"] == 1:
            if config["page2"]["consoleHotKeyEdit"] != "":
                disable_keyboard_command += hotkey_format(config["page2"]["consoleHotKeyEdit"])

        if config["page1"]["isEnableResourceManagerHotKey"] and config["page2"]["resourceManagerHotKeyType"] == 1:
            if config["page2"]["resourceManagerHotKeyEdit"] != "":
                disable_keyboard_command += hotkey_format(config["page2"]["resourceManagerHotKeyEdit"])

    if len(disable_keyboard_command) <= 1:
        return

    print(disable_keyboard_command)

    global thread_disable_keyboard
    thread_disable_keyboard = subprocess.Popen(disable_keyboard_command)

    # 跟随主进程退出
    atexit.register(close_disable_hotkey)


def close_disable_hotkey():
    global thread_disable_keyboard
    if thread_disable_keyboard:
        thread_disable_keyboard.terminate()
