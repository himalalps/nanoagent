#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from agent import CodeAgent


def get_user_input():
    """获取用户输入"""
    try:
        user_input = input("User: ")
        return user_input
    except UnicodeDecodeError:
        print("Error: Unicode decoding error. Please try again with valid UTF-8 input.")
        return None
    except KeyboardInterrupt:
        print("\nGoodbye!")
        return "/exit"


def process_command(user_input):
    """处理命令"""
    if user_input == "/exit":
        print("Goodbye!")
        return True
    return False


def process_user_input(agent, user_input):
    """处理用户输入并调用模型"""
    response = agent.run(user_input)
    print("Assistant: " + response.strip())
    print("\n=================")
    # 显示当前上下文使用情况
    context_usage = agent.get_context_usage()
    print(
        "Context usage: {0}/{1} tokens ({2}%)".format(
            context_usage["current_tokens"],
            context_usage["threshold"],
            context_usage["percentage"],
        )
    )


def main():
    agent = CodeAgent()

    while True:
        user_input = get_user_input()
        if user_input is None:
            continue

        if process_command(user_input):
            break

        process_user_input(agent, user_input)


if __name__ == "__main__":
    main()
