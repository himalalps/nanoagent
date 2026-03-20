import logging

from prompts import CompactionPrompt, SystemPrompt

logger = logging.getLogger(__name__)


class ContextManager:
    """上下文管理器，负责对话历史的管理和压缩"""

    def __init__(self, max_tokens, compact_threshold):
        self.max_tokens = max_tokens
        self.compact_threshold = compact_threshold
        self.messages = []
        self.current_total_tokens = 0
        self.latest_user_input = None

    def get_context_usage(self):
        """获取当前上下文使用情况"""
        if self.max_tokens > 0:
            usage_percentage = (self.current_total_tokens / self.max_tokens) * 100
            return {
                "current_tokens": self.current_total_tokens,
                "threshold": self.max_tokens,
                "percentage": round(usage_percentage, 2),
            }
        return {
            "current_tokens": self.current_total_tokens,
            "threshold": self.max_tokens,
            "percentage": 0,
        }

    def update_latest_user_input(self, user_input):
        """更新最新的用户输入"""
        self.latest_user_input = user_input

    def check_compact(self):
        """检查是否需要压缩对话历史"""
        if self.current_total_tokens > self.compact_threshold:
            compact_message = f"Total tokens ({self.current_total_tokens}) exceed threshold ({self.compact_threshold}), performing compact"
            logger.info(compact_message)
            print(f"\n=== Compact Triggered ===")
            print(compact_message)
            print("=======================\n")
            return True
        return False

    def compact_messages(self, client, model):
        """压缩对话历史，保持系统消息并总结之前的对话"""
        # 添加用户指定的总结prompt
        compaction_prompt = CompactionPrompt()
        messages = []
        messages.append({"role": "system", "content": compaction_prompt.system_render()})
        for msg in self.messages:
            if msg.get("role") != "system":
                messages.append(msg)
        messages.append({"role": "user", "content": compaction_prompt.user_render()})

        # 调用模型进行总结
        summary_response = client.chat.completions.create(
            model=model,
            messages=messages,
        )

        # 获取总结结果
        summary = ""
        if hasattr(summary_response, "choices") and len(summary_response.choices) > 0:
            message = summary_response.choices[0].message
            if hasattr(message, "content"):
                summary = message.content

        start_idx = summary.find("<summary>")
        end_idx = summary.find("</summary>")
        if start_idx != -1 and end_idx != -1:
            summary = summary[start_idx : end_idx + len("</summary>")].strip()

        # 重建 messages 列表：系统消息 + 总结 + 最新的用户输入
        self.messages = []
        system_prompt = SystemPrompt()
        self.messages.append({"role": "system", "content": system_prompt.system_render()})

        # 合并总结和最新用户输入为一个消息
        combined_content = system_prompt.continue_prompt(
            summary=summary, latest_user_input=self.latest_user_input
        )
        logger.info(combined_content)
        self.messages.append({"role": "user", "content": combined_content})

        # 重置 token 计数
        self.current_total_tokens = 0
        logger.info("Messages compacted successfully")
        return summary_response
