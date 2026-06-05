# QIYAM (قيام) - Sovereign Offline AI Operating System

QIYAM is a production-grade, offline-first multi-agent AI operating system designed for Arabic-native intelligence, data analysis, and WhatsApp-based interaction. It operates entirely on local infrastructure without any external API dependencies, ensuring complete data sovereignty.

## Features

- **100% Offline Capability**: Runs entirely locally using `llama.cpp`/`Ollama`.
- **Multi-Agent Architecture**: Includes specialized agents for Data Analysis, Business Intelligence, Research, Task Automation, and Security.
- **Arabic-Native**: First-class support for Modern Standard Arabic and dialects.
- **WhatsApp Integration**: Native interaction via WhatsApp Cloud API webhook.
- **Hybrid Memory**: SQLite for short-term session state, ChromaDB for long-term semantic context.
- **Secure Sandboxing**: Isolated Python execution environment for tools.

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- At least 8GB RAM (16GB recommended for LLM inference)
- Optional: NVIDIA GPU with 6GB+ VRAM

## Quickstart

1. **Clone the repository**
2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your specific configurations
   ```
3. **Start the System**
   ```bash
   make docker-up
   # Or using docker-compose directly:
   # docker-compose -f docker/docker-compose.yml up -d
   ```
4. **Pull the LLM Models**
   ```bash
   docker exec -it qiyam-ollama ollama run llama3.2:3b
   docker exec -it qiyam-ollama ollama run nomic-embed-text
   ```

## Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install

# Run formatting and linting
make format
make lint

# Run tests
make test
```

## Architecture

The system follows Clean Architecture principles:
- `api/`: FastAPI web server and routes.
- `core/`: Orchestration, Intent Classification, LLM integration.
- `agents/`: Agent implementations.
- `memory/`: SQLite and ChromaDB integrations.
- `tools/`: Sandboxed tools (Python executor, Analytics, File parsers).
- `whatsapp/`: Webhook processing and response generation.
- `security/`: Input sanitization and execution guards.

## License

MIT License
