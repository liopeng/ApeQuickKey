from utils import load_yml
from hotkey_util import hotkey_format_tuple

import os
import sys
import pythoncom
import win32gui
import win32api
import win32process
import win32com.client
import threading
import urllib.parse
import subprocess
from queue import Queue, Empty
from pynput import mouse, keyboard

config_path = r"static\config.yml"

event_queue = None

pressed_keys = []

config = None

console_path = None
resource_manager_path = None

mouse_event = {}

hotkey_event = {}


def get_explorer_window_path():
    try:
        pythoncom.CoInitialize()
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        hndl = win32api.OpenProcess(0x400 | 0x10, False, pid)
        path = win32process.GetModuleFileNameEx(hndl, 0)

        if "explorer.exe" in path.lower():
            shell = win32com.client.Dispatch("Shell.Application")
            windows = shell.Windows()
            for window in windows:
                if window.HWND == hwnd:
                    location_url = window.LocationURL.replace("file:///", "")
                    decoded_path = urllib.parse.unquote(location_url)
                    return decoded_path
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        pythoncom.CoUninitialize()


def open_console(path):
    formatted_path = os.path.normpath(path)
    os.system(rf'start cmd.exe /K cd /d "{formatted_path}"')


def open_explorer(path):
    formatted_path = os.path.normpath(path)
    subprocess.Popen(f"start explorer {formatted_path}", shell=True)


def process_event_queue():
    while True:
        try:
            event = event_queue.get(timeout=0.1)
            if event == "open_console":
                path = get_explorer_window_path()
                if path is None:
                    path = console_path

                open_console(path)

            elif event == "open_explorer":
                path = get_explorer_window_path()
                if path is None:
                    path = resource_manager_path

                open_explorer(path)

        except Empty:
            continue


def on_click(x, y, button, pressed):
    if button.name in mouse_event and pressed:
        if mouse_event[button.name] == "open_console":      
            if config["page3"]["isEnableCurrentConsolePath"]:
                event_queue.put("open_console")
            else:
                path = console_path
                open_console(console_path)

        elif mouse_event[button.name] == "open_explorer":
            if config["page3"]["isEnableCurrentResourceManagerPath"]:
                event_queue.put("open_explorer")
            else:
                path = resource_manager_path
                open_explorer(path)

# 设置鼠标监听器
def start_mouse_listener():
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()


def get_key_code(key):
    try:
        # 如果是字母、数字或符号键，可以通过 vk 属性获取虚拟键码
        # print("alphanumeric key {0} pressed, vk: {1}".format(key.char, key.vk))
        return key.vk

    except AttributeError:
        # 如果是特殊键（如功能键、方向键等），直接通过 value 获取虚拟键码
        # print("special key {0} pressed, vk: {1}".format(key, key.value.vk))
        return key.value.vk


def on_press(key):
    global pressed_keys

    pressed_keys.append(get_key_code(key))
    pressed_keys = list(dict.fromkeys(pressed_keys))

    # print("当前按下的按键组合是：{}".format(pressed_keys))


def on_release(key):
    try:
        for hotkey, value in hotkey_event.items():
            if tuple(pressed_keys) == hotkey:
                # print("匹配快捷键成功")
                if value == "open_console":
                    if config["page3"]["isEnableCurrentConsolePath"]:
                        event_queue.put("open_console")
                    else:
                        path = console_path
                        open_console(console_path)

                elif value == "open_explorer":
                    if config["page3"]["isEnableCurrentResourceManagerPath"]:
                        event_queue.put("open_explorer")
                    else:
                        path = resource_manager_path
                        open_explorer(path)
    finally:
        pressed_keys.remove(get_key_code(key))
        # print("当前松开后的按键组合是：{}".format(pressed_keys))

# 设置键盘监听器
def start_keyboard_listener():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


def open_quick_key():
    # 初始化操作
    global event_queue, console_path, resource_manager_path, config_path, config ,mouse_event, hotkey_event

    script_dir = os.path.dirname(os.path.abspath(__file__))

    config_path = os.path.join(script_dir, config_path)
    config = load_yml(config_path)

    # 加载点击事件
    if config["page1"]["isEnableConsoleHotKey"]:
        console_path = config["page3"]["consolePathEdit"]

        if config["page2"]["consoleHotKeyType"] == 1:
            if config["page2"]["consoleHotKeyEdit"] != "":
                hotket_code_list = hotkey_format_tuple(config["page2"]["consoleHotKeyEdit"])
                for hotkey in hotket_code_list:
                    hotkey_event[hotkey] = "open_console"

        elif config["page2"]["consoleHotKeyType"] == 2:
            mouse_event["x1"] = "open_console"
        elif config["page2"]["consoleHotKeyType"] == 3:
            mouse_event["x2"] = "open_console"

    if config["page1"]["isEnableResourceManagerHotKey"]:
        resource_manager_path = config["page3"]["resourceManagerPathEdit"]

        if config["page2"]["resourceManagerHotKeyType"] == 1:
            if config["page2"]["resourceManagerHotKeyEdit"] != "":
                hotket_code_list = hotkey_format_tuple(config["page2"]["resourceManagerHotKeyEdit"])
                for hotkey in hotket_code_list:
                    hotkey_event[hotkey] = "open_explorer"

        elif config["page2"]["resourceManagerHotKeyType"] == 2:
            mouse_event["x1"] = "open_explorer"
        elif config["page2"]["resourceManagerHotKeyType"] == 3:
            mouse_event["x2"] = "open_explorer"

    # print(mouse_event)
    # print(hotkey_event)

    # 加载线程
    event_queue = Queue()

    # 处理线程事件
    threading.Thread(target=process_event_queue, daemon=True).start()

    # 监控鼠标事件
    if len(mouse_event.keys()) > 0:
        mouse_listener_thread = threading.Thread(target=start_mouse_listener, daemon=True)
        mouse_listener_thread.start()

    # 监控键盘事件
    if len(hotkey_event.keys()) > 0:
        keyboard_listener_thread = threading.Thread(target=start_keyboard_listener, daemon=True)
        keyboard_listener_thread.start()

# open_quick_key()

def close_quick_key():
    # 线程跟随主进程退出，不用手动关闭
    pass
