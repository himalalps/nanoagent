class BasePrompt:
    """基础 Prompt 类"""

    def __init__(self, system_template: str = None, user_template: str = None):
        self.system_template = system_template
        self.user_template = user_template

    def system_render(self, **kwargs) -> str:
        """渲染系统 prompt 模板"""
        if self.system_template:
            return self.system_template.format(**kwargs)
        return ""

    def user_render(self, **kwargs) -> str:
        """渲染用户 prompt 模板"""
        if self.user_template:
            return self.user_template.format(**kwargs)
        return ""
