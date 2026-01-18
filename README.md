# Mount Doom - AI Agent Simulation Platform

A fullstack application for multi-agent conversation simulation and prompt generation using Azure AI Projects and Cosmos DB.

## Overview

Mount Doom is an enterprise-grade simulation platform that enables:
- Multi-agent conversation simulations between customer service representatives and customers
- Persona distribution generation from simulation prompts (structured JSON with intents, sentiments, and proportions)
- Persona generation from natural language descriptions
- General-purpose AI assistance via direct model access
- Prompt validation for quality assurance
- Transcript parsing to extract intent, subject, and sentiment from customer-representative conversations
- Comprehensive tracking of tokens, timing, and conversation history
- Persistent storage in Azure Cosmos DB

## Architecture

```
mount-doom/
├── backend/          # FastAPI backend with Azure AI integration
├── frontend/         # Next.js frontend with TypeScript and Ant Design
├── .memory-banks/    # Project context and conventions
└── README.md         # This file
```

### Technology Stack

**Backend:**
- Python 3.9+
- FastAPI for REST API
- Azure AI Projects for agent management
- Azure Cosmos DB for data persistence
- DefaultAzureCredential for authentication

**Frontend:**
- Next.js 15 with App Router
- TypeScript for type safety
- Ant Design (antd) for UI components
- React 19

## Features

### 1. Persona Distribution Generator
Generate persona distributions from simulation prompts using specialized AI agents. Outputs structured JSON with conversation counts, intents, sentiments, and proportions.

### 2. Persona Generator
Generate exact customer personas with specific intents, sentiments, subjects, and metadata for use in conversation simulations.

### 3. General Prompt
Get responses for any general prompt using LLM models directly (GPT-4, GPT-3.5 Turbo).

### 4. Prompt Validator
Validate simulation prompts to ensure they meet quality standards.

### 5. Transcript Parser
Parse customer-representative transcripts to extract intent, subject, and sentiment.

### 6. Conversation Simulation
Simulate complex multi-turn conversations between customer service representatives and customers with intelligent orchestration.

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- Azure AI Projects subscription
- Azure Cosmos DB account
- Azure credentials configured

### Backend Setup

```bash
cd backend
python -m venv .venv

# Activate virtual environment:
# Linux/Mac:
source .venv/bin/activate

# Windows PowerShell (requires execution policy):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser  # One-time setup
.\.venv\Scripts\Activate.ps1

# Windows CMD:
.\.venv\Scripts\activate.bat

# Windows Git Bash:
source .venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Azure credentials
python app/main.py
```

Backend: http://localhost:8000

### Frontend Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local with your API URL
npm run dev
```

Frontend: http://localhost:3000

## Documentation

- [Backend README](backend/README.md) - Detailed backend documentation
- [Frontend README](frontend/README.md) - Detailed frontend documentation
- [Local Evals Runner](LocalEvalsRunner/README.md) - Run CXA AI evals locally
- API Docs: http://localhost:8000/docs (when backend is running)

## License

Copyright (c) 2025. All rights reserved.
