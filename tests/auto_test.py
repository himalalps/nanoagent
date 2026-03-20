#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time

# 测试命令列表
test_commands = [
    "列出当前目录的内容",
    "执行 ls -la 命令",
    "执行 echo 'Hello, Agent!' 命令",
]

# 运行测试
for command in test_commands:
    print(f"\n=== 测试命令: {command} ===")

    # 启动 Agent 进程
    process = subprocess.Popen(
        "source .venv/bin/activate && python main.py",
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # 等待进程启动
    time.sleep(2)

    # 发送测试命令
    process.stdin.write(command + "\n")
    process.stdin.flush()
    
    # 等待模型响应
    time.sleep(8)
    
    # 读取输出
    try:
        output, error = process.communicate(timeout=2)
        print("输出:")
        print(output)
        if error:
            print("错误:")
            print(error)
    except subprocess.TimeoutExpired:
        process.kill()
        print("测试超时")
    
    # 终止进程
    process.terminate()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        process.kill()

print("\n=== 测试完成 ===")