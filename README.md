<div align="center">
  <img src="https://img.shields.io/badge/Status-Active-success.svg" alt="Status" />
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License" />
  <img src="https://img.shields.io/badge/Version-1.0.0-orange.svg" alt="Version" />
  <img src="https://img.shields.io/badge/Language-Python_3.11+-blue.svg" alt="Python" />
  <img src="https://img.shields.io/badge/Framework-FastAPI-009688.svg" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Frontend-Next.js-black.svg" alt="Next.js" />
</div>

<br />

<div align="center">
  <h1>قيام (QIYAM)</h1>
  <p><strong>Sovereign Offline Multi-Agent AI Operating System</strong></p>
  <p>An enterprise-grade, Arabic-native autonomous AI ecosystem designed for complete data sovereignty, robust analytics, and seamless WhatsApp integration.</p>
</div>

---

## 📖 Overview

**QIYAM** is a state-of-the-art, offline-first multi-agent operating system. Engineered to operate entirely on local infrastructure without external API dependencies, QIYAM guarantees **100% data privacy and security**. 

It is tailored specifically for the Arabic-speaking enterprise, providing first-class support for Modern Standard Arabic and regional dialects, while utilizing powerful local LLMs (via `Ollama` and `llama.cpp`) to orchestrate a suite of specialized autonomous agents.

## ✨ Core Capabilities

* 🔒 **Absolute Data Sovereignty**: Operates completely offline. No data ever leaves your servers.
* 🤖 **Multi-Agent Orchestration**: A dynamic routing engine coordinating specialized agents (Data Analyst, Researcher, Critic, Security, and more).
* 🌍 **Arabic-Native Intelligence**: Deep semantic understanding and generation optimized for Arabic languages and regional nuances.
* 📱 **Seamless WhatsApp Integration**: Interact naturally with the ecosystem through a fully integrated WhatsApp Cloud API webhook.
* 🧠 **Hybrid Memory Architecture**: Combines `SQLite` for high-speed short-term session state with `ChromaDB` for persistent, semantic long-term context retrieval.
* 🛡️ **Zero-Trust Sandboxing**: All tools and dynamic code execution run in an isolated, monitored Python sandbox environment to prevent unauthorized access.
* 📊 **Enterprise Dashboard**: A modern, RTL-supported Next.js frontend built with Tailwind CSS for monitoring agents, metrics, and security logs.

## 🛠️ Technology Stack

* **Backend API**: Python 3.11+, FastAPI
* **Frontend**: Next.js 14, React, Tailwind CSS, Playwright
* **AI Engine**: Ollama, LLaMA 3.2 (3B), Nomic Embed Text
* **Databases**: ChromaDB (Vector Storage), SQLite, Neo4j (Graph - optional)
* **Testing & QA**: Pytest, Jest, Playwright, Bandit, Flake8

## 🚀 Quickstart Guide

### Prerequisites

Ensure the following dependencies are installed on your host system:
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- At least **8GB RAM** (16GB+ recommended for optimal LLM inference)
- *Optional but recommended:* NVIDIA GPU with 6GB+ VRAM for hardware acceleration.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/hassanupf24/-QIYAM---Sovereign-Offline-AI-Operating-System.git
   cd -QIYAM---Sovereign-Offline-AI-Operating-System
   ```

2. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Update the .env file with your specific secrets and paths
   ```

3. **Deploy the Infrastructure:**
   ```bash
   make docker-up
   # Alternatively: docker-compose -f docker/docker-compose.yml up -d
   ```

4. **Initialize AI Models:**
   ```bash
   # Pull the required language and embedding models into Ollama
   docker exec -it qiyam-ollama ollama run llama3.2:3b
   docker exec -it qiyam-ollama ollama run nomic-embed-text
   ```

## 💻 Development Setup

To contribute to QIYAM or run it locally outside of Docker:

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install core and development dependencies
make install

# 3. Format and lint the codebase
make lint

# 4. Run the test suite and security checks
make test-all
```

## 🏗️ Architecture

QIYAM follows strict Clean Architecture and SOLID principles, ensuring maintainability and scalability:

```text
├── api/          # FastAPI web server, routes, and API layer
├── core/         # Central Orchestrator, LLM engine, intent routing
├── agents/       # Specialized autonomous agent implementations
├── tools/        # Sandboxed execution environments and utility parsers
├── memory/       # Cognitive storage (SQLite, ChromaDB)
├── security/     # Sandbox guards, input sanitization, threat detection
├── whatsapp/     # WhatsApp webhook processing and response generation
├── telegram/     # Telegram integration handlers
├── frontend/     # Next.js Enterprise Dashboard (RTL supported)
└── tests/        # Comprehensive unit, integration, and E2E tests
```

## 📜 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more details.

---
<div align="center">
  <i>Built for privacy. Engineered for intelligence.</i>
</div>
