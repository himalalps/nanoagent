from agent import CodeAgent


def main():
    agent = CodeAgent()

    while True:
        user_input = input("User: ")
        if user_input == "/exit":
            print("Goodbye!")
            break
        response = agent.run(user_input)
        print("Assistant: " + response.strip())
        print("\n=================")
        # 显示当前上下文使用情况
        context_usage = agent.get_context_usage()
        print(
            f"Context usage: {context_usage['current_tokens']}/{context_usage['threshold']} tokens ({context_usage['percentage']}%)"
        )


if __name__ == "__main__":
    main()
