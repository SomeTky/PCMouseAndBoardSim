#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import os
from pynput.keyboard import Key, KeyCode, Controller

# 自定义缩写到 pynput Key 对象的映射
CUSTOM_KEY_MAP = {
    "la": Key.left,
    "lw": Key.up,
    "ls": Key.down,
    "ld": Key.right,
    "del": Key.backspace,
}

# 额外常用功能键映射（便于扩展）
EXTRA_KEY_MAP = {
    "enter": Key.enter,
    "space": Key.space,
    "tab": Key.tab,
    "esc": Key.esc,
    "shift": Key.shift,
    "ctrl": Key.ctrl,
    "alt": Key.alt,
    "backspace": Key.backspace,
    "up": Key.up,
    "down": Key.down,
    "left": Key.left,
    "right": Key.right,
}


def parse_key(key_str: str):
    """
    将配置中的按键字符串转换为 pynput 可识别的 Key 或 KeyCode 对象。
    支持自定义缩写、常用功能键名及普通字符。
    """
    # 统一转小写，方便匹配
    lower_key = key_str.lower()

    # 1. 自定义缩写映射
    if lower_key in CUSTOM_KEY_MAP:
        return CUSTOM_KEY_MAP[lower_key]

    # 2. 扩展常用功能键映射
    if lower_key in EXTRA_KEY_MAP:
        return EXTRA_KEY_MAP[lower_key]

    # 3. 单字符（普通字母、数字、符号）
    if len(key_str) == 1:
        # 注意：某些符号可能需要特殊处理，但 KeyCode.from_char 对可打印字符有效
        try:
            return KeyCode.from_char(key_str)
        except ValueError:
            raise ValueError(f"不支持的字符: {key_str}")

    # 4. 无法识别
    raise ValueError(f"无法识别的按键名称: {key_str}")


def load_config(config_path="config.json"):
    """加载并验证 JSON 配置文件"""
    if not os.path.exists(config_path):
        # 自动生成默认模板
        default_config = {
            "key_count": 5,
            "key_sequence": ["la", "lw", "ls", "ld", "del"],
            "repeat_count": 3,
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        print(f"已创建配置文件模板：{config_path}")
        print("请根据需要修改后重新运行本程序。")
        exit(0)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # 检查必要字段
    required_fields = ["key_count", "key_sequence", "repeat_count"]
    for field in required_fields:
        if field not in config:
            raise KeyError(f"配置文件缺少必要字段: {field}")

    key_count = config["key_count"]
    key_sequence = config["key_sequence"]
    repeat_count = config["repeat_count"]

    # 校验数据类型
    if not isinstance(key_count, int) or key_count <= 0:
        raise ValueError("key_count 必须为正整数")
    if not isinstance(repeat_count, int) or repeat_count <= 0:
        raise ValueError("repeat_count 必须为正整数")
    if not isinstance(key_sequence, list) or len(key_sequence) == 0:
        raise ValueError("key_sequence 必须为非空列表")

    # 校验按键个数是否匹配
    if len(key_sequence) != key_count:
        print(
            f"警告：配置文件中的 key_count({key_count}) 与实际按键序列长度({len(key_sequence)})不一致，将使用实际序列长度继续。"
        )

    return key_sequence, repeat_count


def replay_keys(key_sequence, repeat_count):
    """回放按键序列，每个按键按下后立即释放，序列之间稍有延迟"""
    controller = Controller()
    # 将字符串序列解析为 Key/KeyCode 对象列表
    try:
        parsed_keys = [parse_key(k) for k in key_sequence]
    except ValueError as e:
        print(f"按键解析错误: {e}")
        return

    print(f"即将回放 {len(parsed_keys)} 个按键，共重复 {repeat_count} 次...")
    print("3 秒后开始，请将焦点置于目标窗口。")
    time.sleep(3)

    for i in range(repeat_count):
        print(f"第 {i+1} 次回放开始")
        for key in parsed_keys:
            controller.press(key)
            controller.release(key)
            time.sleep(0.05)  # 按键间延迟，避免输入丢失
        print(f"第 {i+1} 次回放完成")
        if i != repeat_count - 1:
            time.sleep(0.2)  # 重复间隔


def main():
    print("===== 按键序列回放工具（基于配置文件） =====")
    try:
        key_sequence, repeat_count = load_config("config.json")
        print(f"读取配置文件成功：共 {len(key_sequence)} 个按键，重复次数 {repeat_count}")
        replay_keys(key_sequence, repeat_count)
    except FileNotFoundError:
        print("未找到配置文件，请确保 config.json 存在。")
    except json.JSONDecodeError:
        print("配置文件 JSON 格式错误，请检查。")
    except (KeyError, ValueError) as e:
        print(f"配置文件错误: {e}")
    except KeyboardInterrupt:
        print("\n用户中断执行")
    except Exception as e:
        print(f"发生未知错误: {e}")
    finally:
        print("程序结束")


if __name__ == "__main__":
    main()