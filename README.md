# Mount Doom - AI Agent Simulation Platform

A fullstack application for multi-agent conversation simulation and prompt generation using Azure AI Projects and Cosmos DB.

## Overview

Mount Doom is an enterprise-grade simulation platform that enables:
- Multi-agent conversation simulations between customer service representatives (C1) and customers (C2)
- Persona distribution generation from simulation prompts (structured JSON with intents, sentiments, and proportions)
- Persona generation from natural language descriptions
- C2 customer message generation for simulations
- Transcript parsing to extract intent, subject, and sentiment from customer-representative conversations
- Comprehensive tracking of tokens, timing, and conversation history
- Persistent storage in Azure Cosmos DB

## Architecture

```
mount-doom/
├── backend/          # FastAPI backend with Azure AI integration
├── frontend/         # Next.js frontend with TypeScript and Ant Design
├── CLAUDE.md         # Comprehensive project documentation for Claude Code
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

### Single Agents

#### 1. Persona Distribution Generator
Generate persona distributions from simulation prompts using specialized AI agents. Outputs structured JSON with conversation counts, intents, sentiments, and proportions.

#### 2. Persona Generator
Generate exact customer personas with specific intents, sentiments, subjects, and metadata for use in conversation simulations.

#### 3. Transcript Parser
Parse customer-representative transcripts to extract intent, subject, and sentiment.

#### 4. C2 Message Generator
Generate customer (C2) messages for use in conversation simulations. Simulates realistic customer responses.

### Multi-Agent Workflows

#### 5. Conversation Simulation
Simulate complex multi-turn conversations between customer service representatives (C1) and customers (C2) with intelligent orchestration.

### Download for Evals

All single-agent features support downloading conversations in a standardized evaluation format:

**Download Format**:
```json
{
  "conversations": [
    {
      "Id": "document-uuid",
      "instructions": "Full agent instruction set",
      "prompt": "User's input prompt",
      "agent_prompt": "[SYSTEM]\n{instructions}\n\n[USER]\n{prompt}",
      "agent_response": "Agent's generated response",
      "scenario_name": "AgentName"
    }
  ]
}
```

**How to Use**:
1. Navigate to any single-agent feature (Persona Distribution, Persona Generator, Transcript Parser, C2 Message Generator)
2. Go to the History tab
3. Select conversations using checkboxes
4. Click the "Download" button
5. Save the JSON file for evaluation purposes

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- Azure AI Projects subscription
- Azure Cosmos DB account
- Azure credentials configured

### Backend Setup

1. Create and activate virtual environment:
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
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your Azure credentials
```

4. Run development server:
```bash
# Recommended (with hot reload):
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Alternative:
python app/main.py
```

Backend API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Configure environment:
```bash
cp .env.local.example .env.local
# Edit .env.local with your API URL (default: http://localhost:8000)
```

3. Run development server:
```bash
npm run dev
```

Frontend: http://localhost:3000

4. Build for production (optional):
```bash
npm run build
npm start
```

## Documentation

- [Backend README](backend/README.md) - Detailed backend documentation
- [Frontend README](frontend/README.md) - Detailed frontend documentation
- [CXA Evals Runner](cxa_evals/README.md) - Run CXA AI evals locally
- API Docs: http://localhost:8000/docs (when backend is running)

## License

Copyright (c) 2025. All rights reserved.
