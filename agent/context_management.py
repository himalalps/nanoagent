import logging

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
        # 保留系统消息
        system_message = None
        for msg in self.messages:
            if msg.get("role") == "system":
                system_message = msg
                break

        # 提取除系统消息外的所有消息
        non_system_messages = [
            msg for msg in self.messages if msg.get("role") != "system"
        ]

        # 构建总结请求，将所有非系统消息完整传递
        summary_prompt = ""
        for msg in non_system_messages:
            role = msg.get("role")
            content = msg.get("content", "")
            summary_prompt += f"{role}: {content}\n"

        # 添加用户指定的总结prompt
        summary_prompt += (
            "\n"
            + """You have been working on the task described above but have not yet completed it. Write a continuation summary that will allow you (or another instance of yourself) to resume work efficiently in a future context window where the conversation history will be replaced with this summary. Your summary should be structured, concise, and actionable. Include: 1. **Task Overview**   - The user's core request and success criteria   - Any clarifications or constraints they specified 2. **Current State**   - What has been completed so far   - Files created, modified, or analyzed (with paths if relevant)   - Key outputs or artifacts produced 3. **Important Discoveries**   - Technical constraints or requirements uncovered   - Decisions made and their rationale   - Errors encountered and how they were resolved   - What approaches were tried that didn't work (and why) 4. **Next Steps**   - Specific actions needed to complete the task   - Any blockers or open questions to resolve   - Priority order if multiple steps remain 5. **Context to Preserve**   - User preferences or style requirements   - Domain-specific details that aren't obvious   - Any promises made to the user Be concise but complete—err on the side of including information that would prevent duplicate work or repeated mistakes. Write in a way that enables immediate resumption of the task. Wrap your summary in <summary></summary> tags."""
        )

        # 调用模型进行总结
        summary_response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个对话总结助手，负责根据对话历史生成结构化的总结",
                },
                {"role": "user", "content": summary_prompt},
            ],
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
        if system_message:
            self.messages.append(system_message)

        # 合并总结和最新用户输入为一个消息
        combined_content = f"对话历史已压缩，以下是总结和最新输入：\n{summary}\n\n<user_input>\n{self.latest_user_input}\n</user_input>"
        logger.info(combined_content)
        self.messages.append({"role": "user", "content": combined_content})

        # 重置 token 计数
        self.current_total_tokens = 0
        logger.info("Messages compacted successfully")
        return summary_response
