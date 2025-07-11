# Codynflux Agent

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
 ![Alpha]( https://img.shields.io/badge/Status-Alpha-red)
 [![Pre-commit](https://github.com/bytedance/trae-agent/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/bytedance/trae-agent/actions/workflows/pre-commit.yml)
 [![Unit Tests](https://github.com/bytedance/trae-agent/actions/workflows/unit-test.yml/badge.svg)](https://github.com/bytedance/trae-agent/actions/workflows/unit-test.yml)

**Codynflux Agent** is an LLM-based agent for general purpose software engineering tasks. It provides a powerful CLI interface that can understand natural language instructions and execute complex software engineering workflows using various tools and LLM providers.

**Project Status:** The project is still being actively developed. Please refer to [docs/roadmap.md](docs/roadmap.md) and [CONTRIBUTING](CONTRIBUTING.md) if you are willing to help us improve Codynflux Agent.

**Difference with Other CLI Agents:** Codynflux Agent offers a transparent, modular architecture that researchers and developers can easily modify, extend, and analyze, making it an ideal platform for **studying AI agent architectures, conducting ablation studies, and developing novel agent capabilities**. This ***research-friendly design*** enables the academic and open-source communities to contribute to and build upon the foundational agent framework, fostering innovation in the rapidly evolving field of AI agents.

## ✨ Features

- 🌊 **Lakeview**: Provides short and concise summarisation for agent steps
- 🤖 **Multi-LLM Support**: Works with OpenAI, Anthropic, Doubao, Azure, OpenRouter, Ollama and Google Gemini APIs
- 🛠️ **Rich Tool Ecosystem**: File editing, bash execution, sequential thinking, and more
- 🎯 **Interactive Mode**: Conversational interface for iterative development
- 📊 **Trajectory Recording**: Detailed logging of all agent actions for debugging and analysis
- ⚙️ **Flexible Configuration**: JSON-based configuration with environment variable support
- 🚀 **Easy Installation**: Simple pip-based installation
- 📋 **DTDD Workflow**: Document-Driven Development methodology for systematic software engineering
- 🔄 **Six-Agent Coordination System**: Advanced multi-agent architecture for complex task processing

## 🚀 Quick Start

### Installation

We strongly recommend using [uv](https://docs.astral.sh/uv/) to setup the project.

```bash
git clone https://github.com/win10ogod/codynflux-agent.git
cd codynflux-agent
make install
```

### Setup API Keys

We recommend to configure Codynflux Agent using the config file.

You can also set your API keys as environment variables:

```bash
# For OpenAI
export OPENAI_API_KEY="your-openai-api-key"

# For Anthropic
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# For Doubao (also works with other OpenAI-compatible model providers)
export DOUBAO_API_KEY="your-doubao-api-key"
export DOUBAO_BASE_URL="your-model-provider-base-url"

# For OpenRouter
export OPENROUTER_API_KEY="your-openrouter-api-key"

# For Google Gemini
export GOOGLE_API_KEY="your-google-api-key"

# Optional: For OpenRouter rankings
export OPENROUTER_SITE_URL="https://your-site.com"
export OPENROUTER_SITE_NAME="Your App Name"

# Optional: If you want to use a specific openai compatible api provider, you can set the base url here
export OPENAI_BASE_URL="your-openai-compatible-api-base-url"
```

Although you can pass your API key directly using the `api_key` argument, we suggest utilizing [python-dotenv](https://pypi.org/project/python-dotenv/) to add `MODEL_API_KEY="My API Key"` to your `.env` file. This approach helps prevent your API key from being exposed in source control.

### Basic Usage

```bash
# Run a simple task
codynflux-cli run "Create a hello world Python script"

# Run with Doubao
codynflux-cli run "Create a hello world Python script" --provider doubao --model doubao-seed-1.6

# Run with Google Gemini
codynflux-cli run "Create a hello world Python script" --provider google --model gemini-2.5-flash

# Run with DTDD (Document-Driven Development) workflow
codynflux-cli run "Implement user authentication system" --dtdd-mode
```

## 📋 DTDD (Document-Driven Development) Workflow

Codynflux Agent features a comprehensive DTDD methodology that emphasizes systematic documentation before implementation. This approach ensures higher quality, reduced risks, and better maintainability.

### DTDD 4-Phase Approach

#### Phase 1: PRD (Product Requirements Document)
- Detailed product functional requirements
- Technical architecture planning
- System design concepts
- Technology selection decisions

#### Phase 2: Sequence Diagrams
- System component interactions and sequence
- Data flow and processing steps
- Timing relationships and dependencies
- Error handling flows

#### Phase 3: Class Diagrams
- Class structure design
- Object relationships and associations
- Inheritance and composition relationships
- Interface definitions and implementations

#### Phase 4: Test Planning
- Unit test planning and structure
- Integration test design
- Acceptance test standards
- Performance test scenarios

### Using DTDD Mode

```bash
# Enable DTDD workflow for systematic development
codynflux-cli run "Build a REST API for user management" --dtdd-mode

# DTDD mode with specific configuration
codynflux-cli run "Create a microservice architecture" --dtdd-mode --provider anthropic --model claude-sonnet-4-20250514
```

When DTDD mode is enabled, the agent will:
1. Generate comprehensive documentation first
2. Create visual diagrams for system design
3. Plan detailed test strategies
4. Only then proceed with implementation

## 🔄 Six-Agent Coordination System

Codynflux Agent features an advanced multi-agent architecture that coordinates six specialized agents for complex task processing. This system follows a systematic workflow pattern that ensures thorough analysis, reliable reproduction, effective execution, and continuous improvement.

### Six-Agent Architecture

The system consists of six specialized agents, each with distinct responsibilities:

#### 1. Commander (指揮官)
- **Role**: System coordination and overall workflow management
- **Responsibilities**: 
  - Receives user input and interprets requirements
  - Coordinates communication between agents
  - Provides final results to users
  - Manages feedback loops and system state

#### 2. Observer (觀察者)
- **Role**: Information gathering and system state monitoring
- **Responsibilities**:
  - Gathers relevant information from the environment
  - Monitors system states and conditions
  - Provides observational data to analysts
  - Tracks changes and system behavior

#### 3. Analyst (分析者)
- **Role**: Data analysis and pattern recognition
- **Responsibilities**:
  - Analyzes observational data and identifies patterns
  - Performs root cause analysis
  - Generates insights and recommendations
  - Feeds analysis results to reproducers

#### 4. Reproducer (再現者)
- **Role**: Problem reproduction and verification
- **Responsibilities**:
  - Reproduces identified issues and scenarios
  - Creates test cases and validation scenarios
  - Verifies problem conditions
  - Ensures consistent reproduction for executors

#### 5. Executor (執行者)
- **Role**: Solution implementation and execution
- **Responsibilities**:
  - Implements solutions based on analysis and reproduction
  - Executes fixes and improvements
  - Provides implementation feedback
  - Handles actual code/system changes

#### 6. Designer (設計者)
- **Role**: System design and optimization
- **Responsibilities**:
  - Designs improvements and optimizations
  - Provides architectural guidance
  - Suggests best practices and patterns
  - Validates design decisions

### Agent Workflow Pattern

The agents follow a systematic workflow with feedback loops:

```
User Input → Commander → Observer → Analyst → Reproducer → Executor
                ↑                                              ↓
                ← Designer ← (Improvement Feedback) ← ← ← ← ← ←
```

1. **Initial Processing**: Commander receives user input and initiates the workflow
2. **Observation Phase**: Observer gathers relevant information and system state
3. **Analysis Phase**: Analyst processes observations and identifies patterns
4. **Reproduction Phase**: Reproducer creates test cases and verifies conditions
5. **Execution Phase**: Executor implements solutions and executes changes
6. **Feedback Loop**: If improvements are needed, Designer provides optimization guidance
7. **Final Results**: Commander synthesizes results and provides final output

### Using Multi-Agent Mode

```bash
# Enable multi-agent coordination for complex tasks
codynflux-cli run "Analyze and optimize the entire codebase" --multi-agent-mode

# Multi-agent mode with specific configuration
codynflux-cli run "Debug complex system issues" --multi-agent-mode --provider anthropic --model claude-sonnet-4-20250514

# Combine with DTDD for comprehensive development
codynflux-cli run "Design and implement microservices" --multi-agent-mode --dtdd-mode
```

### Six-Agent System Benefits

- **Systematic Approach**: Each agent specializes in specific aspects of problem-solving
- **Thorough Analysis**: Multi-perspective analysis ensures comprehensive understanding
- **Reliable Reproduction**: Dedicated reproduction phase ensures consistent issue identification
- **Quality Execution**: Specialized execution with feedback loops ensures high-quality implementations
- **Continuous Improvement**: Designer feedback loop enables ongoing optimization
- **Complex Problem Solving**: Coordinated agents can tackle problems requiring diverse expertise
- **Fault Tolerance**: Multi-agent redundancy provides robustness against individual agent failures

### DTDD Benefits

- **Risk Reduction**: Identify potential issues early through detailed planning
- **Improved Efficiency**: Clear roadmap reduces rework and confusion
- **Quality Assurance**: Comprehensive testing strategy ensures reliable software
- **Team Collaboration**: Standardized documentation facilitates communication
- **Maintainability**: Detailed documentation aids future development

## 📖 Usage

### Command Line Interface

The main entry point is the `codynflux` command with several subcommands:

#### `codynflux run` - Execute a Task

```bash
# Basic task execution
codynflux-cli run "Create a Python script that calculates fibonacci numbers"

# With specific provider and model
codynflux-cli run "Fix the bug in main.py" --provider anthropic --model claude-sonnet-4-20250514

# Using OpenRouter with any supported model
codynflux-cli run "Optimize this code" --provider openrouter --model "openai/gpt-4o"
codynflux-cli run "Add documentation" --provider openrouter --model "anthropic/claude-3-5-sonnet"

# Using Google Gemini
codynflux-cli run "Implement a data parsing function" --provider google --model gemini-2.5-pro

# With custom working directory
codynflux-cli run "Add unit tests for the utils module" --working-dir /path/to/project

# Save trajectory for debugging
codynflux-cli run "Refactor the database module" --trajectory-file debug_session.json

# Force to generate patches
codynflux-cli run "Update the API endpoints" --must-patch

# Enable DTDD workflow for comprehensive development
codynflux-cli run "Design and implement authentication system" --dtdd-mode

# Use Multi-Agent Coordination System for complex tasks
codynflux-cli run "Analyze and fix performance issues" --multi-agent-mode

# Combine DTDD with specific configuration
codynflux-cli run "Build microservices architecture" --dtdd-mode --provider anthropic --working-dir /path/to/project
```

#### `codynflux interactive` - Interactive Mode

```bash
# Start interactive session
trae-cli interactive

# With custom configuration
trae-cli interactive --provider openai --model gpt-4o --max-steps 30
```

In interactive mode, you can:

- Type any task description to execute it
- Use `status` to see agent information
- Use `help` for available commands
- Use `clear` to clear the screen
- Use `exit` or `quit` to end the session

#### `codynflux show-config` - Configuration Status

```bash
trae-cli show-config

# With custom config file
trae-cli show-config --config-file my_config.json
```

### Configuration

Codynflux Agent uses a JSON configuration file for settings. Please refer to the `codynflux_config.json` file in the root directory for the detailed configuration structure.

**WARNING:**
For Doubao users, please use the following base_url.
```
base_url=https://ark.cn-beijing.volces.com/api/v3/
```

**Configuration Priority:**

1. Command-line arguments (highest)
2. Configuration file values
3. Environment variables
4. Default values (lowest)

```bash
# Use GPT-4 through OpenRouter
codynflux-cli run "Write a Python script" --provider openrouter --model "openai/gpt-4o"

# Use Claude through OpenRouter
codynflux-cli run "Review this code" --provider openrouter --model "anthropic/claude-3-5-sonnet"

# Use Gemini through OpenRouter
codynflux-cli run "Generate docs" --provider openrouter --model "google/gemini-pro"

# Use Gemini directly
codynflux-cli run "Analyze this dataset" --provider google --model gemini-2.5-flash

# Use Qwen through Ollama
codynflux-cli run "Comment this code" --provider ollama --model "qwen3"
```

**Popular OpenRouter Models:**

- `openai/gpt-4o` - Latest GPT-4 model
- `anthropic/claude-3-5-sonnet` - Excellent for coding tasks
- `google/gemini-pro` - Strong reasoning capabilities
- `meta-llama/llama-3.1-405b` - Open source alternative
- `openai/gpt-4o-mini` - Fast and cost-effective

### Environment Variables

- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `GOOGLE_API_KEY` - Google API key
- `OPENROUTER_API_KEY` - OpenRouter API key
- `GOOGLE_API_KEY` - Google Gemini API key
- `OPENROUTER_SITE_URL` - (Optional) Your site URL for OpenRouter rankings
- `OPENROUTER_SITE_NAME` - (Optional) Your site name for OpenRouter rankings

## 🛠️ Available Tools

Codynflux Agent provides a comprehensive toolkit for file editing, bash execution, structured thinking, task completion, and JSON manipulation, with new tools actively being developed and existing ones continuously enhanced.

For detailed information about all available tools and their capabilities, see [docs/tools.md](docs/tools.md).

## 📊 Trajectory Recording

Codynflux Agent automatically records detailed execution trajectories for debugging and analysis:

```bash
# Auto-generated trajectory file
codynflux-cli run "Debug the authentication module"
# Saves to: trajectory_20250612_220546.json

# Custom trajectory file
codynflux-cli run "Optimize the database queries" --trajectory-file optimization_debug.json
```

Trajectory files contain:

- **LLM Interactions**: All messages, responses, and tool calls
- **Agent Steps**: State transitions and decision points
- **Tool Usage**: Which tools were called and their results
- **Metadata**: Timestamps, token usage, and execution metrics

For more details, see [docs/TRAJECTORY_RECORDING.md](docs/TRAJECTORY_RECORDING.md).

## 🤝 Contributing

For detailed contribution guidelines, please refer to [CONTRIBUTING.md](CONTRIBUTING.md).

1. Fork the repository
2. Set up a development install(`make install-dev pre-commit-install`)
3. Create a feature branch (`git checkout -b feature/amazing-feature`)
4. Make your changes
5. Add tests for new functionality
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Use type hints where appropriate
- Ensure all tests pass before submitting

## 📋 Requirements

- Python 3.12+
- API key for your chosen provider:
  - OpenAI API key (for OpenAI models)
  - Anthropic API key (for Anthropic models)
  - OpenRouter API key (for OpenRouter models)
  - Google API key (for Google Gemini models)

## 🔧 Troubleshooting

### Common Issues

**Import Errors:**

```bash
# Try setting PYTHONPATH
PYTHONPATH=. codynflux-cli run "your task"
```

**API Key Issues:**

```bash
# Verify your API keys are set
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
echo $GOOGLE_API_KEY
echo $OPENROUTER_API_KEY
echo $GOOGLE_API_KEY

# Check configuration
trae-cli show-config
```

**Permission Errors:**

```bash
# Ensure proper permissions for file operations
chmod +x /path/to/your/project
```

**Command not found Errors:**

```bash
# you can try
uv run trae-cli `xxxxx`
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

We extend our heartfelt gratitude to the original **Trae Agent** project and its contributors for creating this foundational framework. This project builds upon their excellent work and innovative agent architecture.

Special thanks to:
- The Trae Agent development team for their pioneering work in LLM-based software engineering agents
- Anthropic for building the [anthropic-quickstart](https://github.com/anthropics/anthropic-quickstarts) project that served as a valuable reference for the tool ecosystem
- All contributors who helped shape the original Trae Agent into a powerful, research-friendly platform
