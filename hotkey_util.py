from itertools import product
from utils import load_yml
import os

keycode_path = r"static\keycode.yml"
keycode = None

def _load_keycode():
    global keycode_path, keycode

    script_dir = os.path.dirname(os.path.abspath(__file__))

    keycode_path = os.path.join(script_dir, keycode_path)
    keycode = load_yml(keycode_path)

def hotkey_format(hotkey):
    _load_keycode()

    # 分割键名字符串
    keys = hotkey.split("+")

    # 查找每个键名对应的键码
    codes = []

    for key in keys:
        found_codes = [k for k, v in keycode.items() if str(v).lower() == key.lower()]
        codes.append(found_codes)

    # print("codes: ", codes)

    all_combinations = product(*codes)

    formatted_codes_list = []
    for combination in all_combinations:
        formatted_codes = "-" + "-".join(map(str, combination))
        formatted_codes_list.append(formatted_codes)

    # print("formatted_codes_list: ", formatted_codes_list)

    return formatted_codes_list

# hotkey_format("Ctrl+C")


def hotkey_format_tuple(hotkey):
    _load_keycode()

    # 分割键名字符串
    keys = hotkey.split("+")

    # 查找每个键名对应的键码
    codes = []

    for key in keys:
        found_codes = [k for k, v in keycode.items() if str(v).lower() == key.lower()]
        codes.append(found_codes)

    # print("codes: ", codes)

    all_combinations = product(*codes)

    formatted_codes_list = []
    for combination in all_combinations:
        formatted_codes_list.append(combination)

    # print("formatted_codes_list: ", formatted_codes_list)

    return formatted_codes_list


# hotkey_format_tuple("Ctrl+C")
