# nanoagent

一个用于交互式运行 nanoagent 的示例项目。main.py 会创建一个 CodeAgent 并在终端中与用户交互。

## 目录结构
- agent.py — CodeAgent 的实现
- main.py — 程序入口，命令行交互界面
- tests/ — 单元测试
- tools/ — 辅助工具
- logs/ — 运行产生的日志

## 需求
- Python 3.12+
- (可选) 虚拟环境

## 安装与运行
1. 克隆仓库并进入目录：
   ```bash
      git clone git@github.com:himalalps/nanoagent.git
      cd nanoagent
   ```

2. 使用 uv 安装依赖：
   ```bash  
      uv sync
   ```

3. 配置环境变量：
   ```bash
      cp .env.example .env
   ```
   然后编辑 `.env` 文件添加您的配置详情。

4. 运行项目：
   ```bash   
   uv run main.py
   ```

   在运行后，输入用户消息进行交互。输入 `/exit` 退出。

## 测试
运行测试（如果已配置）：
   ```bash
      pytest
   ```

## 日志
运行时日志会写入 `logs/` 目录（如果 agent 实现了日志功能）。

## 贡献
欢迎提交 issue 或 pull request。

## 许可证
本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。