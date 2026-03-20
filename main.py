#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from agent import CodeAgent


def main():
    agent = CodeAgent()

    while True:
        try:
            user_input = input("User: ")
        except UnicodeDecodeError:
            print(
                "Error: Unicode decoding error. Please try again with valid UTF-8 input."
            )
            continue
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

        if user_input == "/exit":
            print("Goodbye!")
            break
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


if __name__ == "__main__":
    main()
