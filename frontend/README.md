# Mount Doom Frontend

Next.js frontend for the Mount Doom AI Agent Simulation platform. Built with TypeScript and Ant Design components.

## Features

### Agents
Individual agents that operate independently and return results immediately:
- **Persona Distribution Generator** - Generate persona distributions from simulation prompts
- **Persona Generator** - Generate exact customer personas with metadata
- **Transcript Parser** - Parse transcripts to extract intent, subject, and sentiment
- **C2 Message Generator** - Generate customer messages for conversation simulations
- **Multi-Agent Downloads** - Download conversations from multiple agents with version filtering and conversation count limits

### Workflows
Multi-agent orchestration with custom logic and stateful conversations:
- **Conversation Simulation** - Orchestrates multiple agents (C1/C2) for realistic conversation simulations with real-time tracking

## Tech Stack

- **Framework**: Next.js 16 with App Router
- **Language**: TypeScript
- **UI Components**: Ant Design (antd) v6
- **Icons**: Ant Design Icons
- **State Management**: React hooks
- **API Client**: Custom type-safe API client

## Getting Started

### Prerequisites

- Node.js 18 or higher
- npm or yarn
- Backend API running (see backend README)

### Installation

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Configure environment variables:
```bash
cp .env.local.example .env.local
# Edit .env.local with your API URL
```

### Development

Run the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser.

### Build

Build for production:
```bash
npm run build
```

### Run Production Build

```bash
npm start
```

## Project Structure

```
frontend/
├── app/                                     # Next.js App Router pages
│   ├── agents/                              # Nested routes for agents
│   │   ├── download/                        # Multi-agent download page
│   │   │   └── page.tsx                     # Download with conversation limits
│   │   └── [agentId]/                       # Dynamic agent routes
│   │       ├── layout.tsx                   # Agent layout (loads info, provides context)
│   │       ├── page.tsx                     # Generate page (default)
│   │       ├── batch/
│   │       │   └── page.tsx                 # Batch processing page
│   │       └── history/
│   │           └── page.tsx                 # History page
│   ├── conversation-simulation/             # Conversation simulation workflow
│   │   └── page.tsx                         # Custom workflow page
│   ├── layout.tsx                           # Root layout with timezone provider
│   ├── page.tsx                             # Home page
│   └── globals.css                          # Global styles
├── components/                               # React components
│   ├── PageLayout.tsx                       # Shared page layout with navigation
│   └── agents/                              # Modular agent components
│       ├── shared/
│       │   ├── AgentContext.tsx             # React Context for agent info
│       │   └── AgentTabs.tsx                # Tab navigation
│       ├── result/
│       │   ├── AgentResultModal.tsx         # Modal for viewing results
│       │   └── AgentResultCard.tsx          # Inline result display
│       ├── instructions/
│       │   └── AgentInstructionsCard.tsx    # Collapsible instructions
│       ├── batch/
│       │   └── BatchProcessingSection.tsx   # Complete batch UI
│       └── history/
│           └── AgentHistoryTable.tsx        # Full-featured history table
├── lib/                                     # Utility libraries
│   ├── api-client.ts                        # Type-safe API client
│   ├── types.ts                             # Shared TypeScript types
│   └── timezone-context.tsx                 # Global timezone context (UTC/IST)
└── public/                                  # Static assets
```

## Features Detail

### Modular Agent Pages

Agent pages use nested routes with reusable components:

**Nested Route Structure:**
- `/agents/[agentId]` - Generate page (default)
- `/agents/[agentId]/batch` - Batch processing page
- `/agents/[agentId]/history` - History page
- Agent info loaded once in layout, shared via React Context
- URL-based navigation with browser back/forward support

**Reusable Components:**
- **AgentContext** - Share agent info across pages
- **AgentTabs** - Tab-like navigation using Next.js Link
- **AgentResultModal** - View result details with JSON/Plain Text toggle
- **AgentResultCard** - Inline result display
- **AgentInstructionsCard** - Collapsible instructions display
- **BatchProcessingSection** - Complete batch processing UI with View button for detailed results
- **AgentHistoryTable** - Full-featured history table

**Workflow Pages:**
- Custom implementations for each workflow (e.g., conversation simulation)
- Three tabs: Simulate, Batch Processing, History
- Custom conversation rendering and history columns
- Expandable rows for viewing conversation details

### Global Timezone Support

- Context provider: `TimezoneProvider` in layout.tsx
- Hook: `useTimezone()` for timezone management
- Supported: UTC, IST (default: IST)
- Persisted to localStorage
- Consistent timestamp formatting across all pages

### API Client

The `api-client.ts` provides a type-safe interface for all backend endpoints:
- Unified agents API integration
- Workflows API integration
- Automatic error handling
- TypeScript types for all requests/responses
- Promise-based async/await API

### UI Components (Ant Design)

Consistent components used across pages:
- Button, Card, Tabs, Table
- Input, TextArea, Select
- Space, Typography, Alert
- message (toast notifications)
- Tag, Progress, Collapse

### Responsive Design

- Responsive grid layouts with Ant Design
- Adaptive navigation sidebar
- Mobile-friendly tables
- Touch-friendly interfaces

## Environment Variables

Create a `.env.local` file with:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, set this to your deployed backend URL.

## License

Copyright (c) 2025. All rights reserved.
