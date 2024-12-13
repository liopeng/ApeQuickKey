from itertools import product
import subprocess
import threading
import atexit
import yaml
import time
import os

config_path = r"static\config.yml"
keycode_path = r"static\keycode.yml"
disable_keyboard_path = r"tool\disable_keyboard.exe"

config = None
keycode = None

thread_disable_keyboard = None
thread_disable_mouse = None


def load_config():
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config


def load_keycode():
    with open(keycode_path, "r") as file:
        config = yaml.safe_load(file)
    return config


def HotKey_Format(HotKeyText):
    # 分割键名字符串
    keys = HotKeyText.split("+")

    # 查找每个键名对应的键码
    codes = []

    for key in keys:
        found_codes = [k for k, v in keycode.items() if str(v).lower() == key.lower()]
        codes.append(found_codes)

    print("codes: ", codes)

    all_combinations = product(*codes)

    formatted_codes_list = []
    for combination in all_combinations:
        formatted_codes = "-" + "-".join(map(str, combination))
        formatted_codes_list.append(formatted_codes)

    print("formatted_codes_list: ", formatted_codes_list)

    return formatted_codes_list

def open_disable_hotkey():
    global config_path ,keycode_path, disable_keyboard_path, keycode, config

    script_dir = os.path.dirname(os.path.abspath(__file__))

    config_path = os.path.join(script_dir, config_path)

    keycode_path = os.path.join(script_dir, keycode_path)

    keycode = load_keycode()
    config = load_config()
    
    disable_keyboard_command = [os.path.join(script_dir, disable_keyboard_path)]

    for key, value in config["DisableHotkey"].items():
        if value["Enable"]:
            disable_keyboard_command += HotKey_Format(value["Hotkey"])

    print(disable_keyboard_command)

    global thread_disable_keyboard
    thread_disable_keyboard = subprocess.Popen(disable_keyboard_command)
    
    # 跟随主进程退出
    atexit.register(close_disable_hotkey)

def close_disable_hotkey():
    global thread_disable_keyboard
    if thread_disable_keyboard:
        thread_disable_keyboard.terminate()