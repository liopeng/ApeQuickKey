from utils import load_yml

import subprocess
import atexit
import os

config_path = r"static\config.yml"
disable_mouse_path = r"tool\disable_mouse.exe"

config = None

thread_disable_mouse = None

def open_disable_mouse():
    global disable_mouse_path, config_path, config

    script_dir = os.path.dirname(os.path.abspath(__file__))

    config_path = os.path.join(script_dir, config_path)
    config = load_yml(config_path)

    disable_mouse_command = [os.path.join(script_dir, disable_mouse_path)]

    if config["page2"]["isHotKeyAbsolute"]:
        if config["page1"]["isEnableConsoleHotKey"]:    
            if config["page2"]["consoleHotKeyType"] == 2:
                disable_mouse_command.append("--disableXButton1")
            elif config["page2"]["consoleHotKeyType"] == 3:
                disable_mouse_command.append("--disableXButton2")

        if config["page1"]["isEnableResourceManagerHotKey"]:
            if config["page2"]["resourceManagerHotKeyType"] == 2:
                disable_mouse_command.append("--disableXButton1")
            elif config["page2"]["resourceManagerHotKeyType"] == 3:
                disable_mouse_command.append("--disableXButton2")

    if config["page5"]["isDisableMouse"]:
        if config["page5"]["isDisableLeftClick"]:
            disable_mouse_command.append("--disableLeftButton")
        if config["page5"]["isDisableRightClick"]:
            disable_mouse_command.append("--disableRightButton")
        if config["page5"]["isDisableMiddleClick"]:
            disable_mouse_command.append("--disableMiddleButton")
        if config["page5"]["isDisableWheel"]:
            disable_mouse_command.append("--disableWheel")
        if config["page5"]["isDisableX1Click"]:
            disable_mouse_command.append("--disableXButton1")
        if config["page5"]["isDisableX2Click"]:
            disable_mouse_command.append("--disableXButton2")

    if len(disable_mouse_command) <= 1:
        return

    print(disable_mouse_command)

    global thread_disable_mouse
    thread_disable_mouse = subprocess.Popen(disable_mouse_command)

    # 跟随主进程退出
    atexit.register(close_disable_mouse)

def close_disable_mouse():
    global thread_disable_mouse
    if thread_disable_mouse:
        thread_disable_mouse.terminate()

# open_disable_mouse()
# import time
# time.sleep(5)
# close_disable_mouse()
