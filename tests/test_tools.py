#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tools import execute_tool

# 测试 ls 工具
print("=== 测试 ls 工具 ===")
result = execute_tool("ls", {"path": "."})
print(result)

# 测试 bash 工具
print("\n=== 测试 bash 工具 ===")
result = execute_tool("bash", {"command": "ls -la"})
print(result)

# 测试 bash 工具 - echo 命令
print("\n=== 测试 bash 工具 - echo 命令 ===")
result = execute_tool("bash", {"command": "echo 'Hello, Agent!'"})
print(result)

# 测试 edit 工具
print("\n=== 测试 edit 工具 ===")
# 创建一个测试文件
test_file = "test_edit.txt"
with open(test_file, 'w', encoding='utf-8') as f:
    f.write("原始内容\n")

# 测试编辑文件
result = execute_tool("edit", {
    "file_path": test_file,
    "old_content": "原始内容",
    "new_content": "修改后的内容"
})
print(result)

# 验证文件内容
with open(test_file, 'r', encoding='utf-8') as f:
    content = f.read()
print(f"文件内容: {content.strip()}")

# 测试 read 工具
print("\n=== 测试 read 工具 ===")
# 先创建一个测试文件
read_test_file = "test_read.txt"
with open(read_test_file, 'w', encoding='utf-8') as f:
    f.write("测试文件内容\n这是第二行\n")

# 测试读取文件
result = execute_tool("read", {"file_path": read_test_file})
print(result)

# 清理测试文件
import os
os.remove(test_file)
os.remove(read_test_file)
print(f"\n=== 测试完成 ===")