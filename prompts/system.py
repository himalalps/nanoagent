from .base import BasePrompt


class SystemPrompt(BasePrompt):
    """系统 Prompt 类"""

    def __init__(self, system_template: str = None):
        if system_template is None:
            system_template = (
                "You are a helpful assistant that can use tools to complete tasks."
            )
        super().__init__(system_template=system_template)

    def continue_prompt(self, summary: str, latest_user_input: str) -> str:
        """获取继续对话的系统提示"""
        return f"对话历史已压缩，以下是总结和最新输入：\n{summary}\n\n<user_input>\n{latest_user_input}\n</user_input>"

    def compaction_prompt(self) -> str:
        """获取压缩对话的系统提示"""
        return "你是一个对话总结助手，负责根据对话历史生成结构化的总结"
