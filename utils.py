from pathlib import Path
import yaml

def check_path_validity(path):
    # 检查路径是否为空
    if not path:
        print("路径为空")
        return False

    # 使用pathlib.Path来处理路径
    p = Path(path)

    # 检查路径是否存在且是一个目录
    if p.exists() and p.is_dir():
        print(f"路径有效: {path}")
        return True
    else:
        print(f"路径无效或不是一个目录: {path}")
        return False


def load_yml(path):
    with open(path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data

def save_yml(path, data):
    with open(path, "w", encoding="utf-8") as file:
        yaml.safe_dump(data, file)
