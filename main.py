from agent import CodeAgent


def main():
    agent = CodeAgent()

    while True:
        user_input = input("User: ")
        if user_input == "/exit":
            print("Goodbye!")
            break
        response = agent.run(user_input)
        print("Assistant: " + response)
        print("\n=================")
        print()


if __name__ == "__main__":
    main()
