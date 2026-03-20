# nanoagent

An interactive agent project that allows users to run and interact with an AI agent in the terminal. main.py creates a CodeAgent and provides a command-line interface for user interaction.

## Directory Structure
- agent.py — Implementation of CodeAgent
- main.py — Program entry point, command-line interactive interface
- tests/ — Unit tests
- tools/ — Helper tools
- logs/ — Runtime logs

## Requirements
- Python 3.12+
- (Optional) Virtual environment

## Installation and Running
1. Clone the repository and navigate to the directory:
   ```bash
      git clone git@github.com:himalalps/nanoagent.git
      cd nanoagent
   ```

2. Install dependencies using uv:
   ```bash  
      uv sync
   ```

3. Configure environment variables:
   ```bash
      cp .env.example .env
   ```
   Then edit the `.env` file to add your configuration details.

4. Run the project:
   ```bash   
   uv run main.py
   ```

   After running, enter user messages for interaction. Type `/exit` to quit.

## Testing
Run tests (if configured):
   ```bash
      pytest
   ```

## Logs
Runtime logs are written to the `logs/` directory (if the agent implements logging functionality).

## Contributing
Welcome to submit issues or pull requests.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.