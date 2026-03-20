# CodeAgent

一个用于交互式运行 CodeAgent 的示例项目。main.py 会创建一个 CodeAgent 并在终端中与用户交互。

## 目录结构
- agent.py — CodeAgent 的实现
- main.py — 程序入口，命令行交互界面
- tests/ — 单元测试
- tools/ — 辅助工具
- logs/ — 运行产生的日志

## 需求
- Python 3.8+
- (可选) 虚拟环境

## 安装与运行
1. 克隆仓库并进入目录：
   git clone <repo-url>
   cd <repo-dir>

2. 创建并激活虚拟环境（可选）：
   python -m venv .venv
   source .venv/bin/activate  # macOS / Linux
   .venv\Scripts\activate     # Windows

3. 安装依赖（如果有）：
   pip install -r requirements.txt

4. 运行项目：
   python main.py

   在运行后，输入用户消息进行交互。输入 `/exit` 退出。

## 测试
运行测试（如果已配置）：
   pytest

## 日志
运行时日志会写入 logs/ 目录（如果 agent 实现了日志功能）。

## 贡献
欢迎提交 issue 或 pull request。

## 许可证
请在此处添加许可证信息（例如 MIT）。
