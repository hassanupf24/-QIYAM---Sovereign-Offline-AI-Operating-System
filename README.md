<div align="center">
  <img src="https://img.shields.io/badge/Status-Active-success.svg" alt="Status" />
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License" />
  <img src="https://img.shields.io/badge/Version-2.0.0-orange.svg" alt="Version" />
  <img src="https://img.shields.io/badge/Language-Python_3.11+-blue.svg" alt="Python" />
  <img src="https://img.shields.io/badge/Framework-FastAPI-009688.svg" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Frontend-Next.js-black.svg" alt="Next.js" />
</div>

<br />

<div align="center">
  <h1>قيام (QIYAM)</h1>
  <p><strong>Sovereign Offline Multi-Agent AI Operating System</strong></p>
  <p>An enterprise-grade, Arabic-native autonomous AI ecosystem designed for complete data sovereignty, robust analytics, Graph RAG, and federated learning.</p>
</div>

---

## 👨‍💻 Author

**Hassan Gasim**  
*Role:* Data Analyst  

📧 **Email:** [Hassan.gasim.data@gmail.com](mailto:Hassan.gasim.data@gmail.com) | [hassanupf2@gmail.com](mailto:hassanupf2@gmail.com)  
💼 **LinkedIn:** [Hassan Gasim](https://www.linkedin.com/in/hassan-gasim-b05377108?utm_source=share_via&utm_content=profile&utm_medium=member_android)  
🐙 **GitHub:** [hassanupf24](https://github.com/hassanupf24)  
📊 **Kaggle:** [hassangasem](https://kaggle.com/hassangasem)  

---

## 📖 Overview

**QIYAM** is a state-of-the-art, offline-first multi-agent operating system. Engineered to operate entirely on local infrastructure without external API dependencies, QIYAM guarantees **100% data privacy and security**. 

It is tailored specifically for the Arabic-speaking enterprise, providing first-class support for Modern Standard Arabic and regional dialects, while utilizing powerful local LLMs (via `llama.cpp` and `Ollama`) to orchestrate a suite of specialized autonomous agents.

## ✨ Core Capabilities & Recent Updates

* 🔒 **Absolute Data Sovereignty**: Operates completely offline. No data ever leaves your servers.
* 👥 **Secure Multi-Tenancy**: Built-in tenant isolation using PostgreSQL and isolated Celery workers for true enterprise multi-organization deployments.
* 🕸️ **Knowledge Extraction (Graph RAG)**: Automatically translates user conversations into semantic knowledge graphs stored in `Neo4j`, complete with automated deduplication and confidence decay.
* 🎙️ **Voice-to-Voice Real-Time Agents**: Natively intercepts WhatsApp audio notes and utilizes `faster-whisper` for air-gapped, GPU-accelerated Arabic speech-to-text.
* 📈 **Continuous Learning (RLHF)**: Learns from user feedback (WhatsApp emojis 👍/👎) and automatically filters local QLoRA fine-tuning datasets to prevent catastrophic forgetting.
* 🌐 **Federated Learning & Edge Sync**: Securely export, AES-256 encrypt, and synchronize LoRA adapter weights across isolated sovereign nodes (e.g., between different ministries) without sharing plain-text data.
* 📱 **Seamless WhatsApp Integration**: Interact naturally with the ecosystem through a fully integrated WhatsApp Cloud API webhook.
* 🛡️ **Zero-Trust Architecture**: Complete isolation using Docker sandboxing, prompt injection prevention, and strict payload validation.

## 🛠️ Technology Stack

* **Backend API**: Python 3.11+, FastAPI, Celery, Redis
* **AI Engine**: LlamaCPP, Transformers, PEFT (QLoRA), Faster-Whisper
* **Memory & Storage**: PostgreSQL (Relational & Auth), Neo4j (Graph RAG), ChromaDB (Vector Search)
* **Frontend**: Next.js 14, React, Tailwind CSS
* **Observability**: OpenTelemetry, Jaeger

## 🚀 Quickstart Guide

### Prerequisites

Ensure the following dependencies are installed on your host system:
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- At least **16GB RAM** (32GB+ recommended for optimal local LLM + Neo4j inference)
- NVIDIA GPU with 8GB+ VRAM for hardware acceleration (CUDA).

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/hassanupf24/-QIYAM---Sovereign-Offline-AI-Operating-System.git
   cd -QIYAM---Sovereign-Offline-AI-Operating-System
   ```

2. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Update the .env file with your specific PostgreSQL, Neo4j, and AES encryption keys
   ```

3. **Deploy the Infrastructure:**
   ```bash
   docker-compose up -d
   ```

## 🏗️ Architecture

QIYAM follows strict Clean Architecture and SOLID principles, ensuring maintainability and scalability:

```text
├── api/          # FastAPI web server, routes, and federated sync endpoints
├── core/         # Central Orchestrator, LLM engine, background Celery workers
├── agents/       # Specialized autonomous agent implementations (Data Analyst, Graph Maintenance)
├── memory/       # Cognitive storage interfaces (PostgreSQL, Neo4j, ChromaDB)
├── security/     # Sandbox guards, input sanitization, JWT auth
├── scripts/      # Data export, QLoRA fine-tuning (trainer.py), federated export/merge
├── whatsapp/     # WhatsApp webhook processing and response generation
└── frontend/     # Next.js Enterprise Dashboard (RTL supported)
```

## 📜 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more details.

---
<div align="center">
  <i>Built for privacy. Engineered for intelligence.</i>
</div>
