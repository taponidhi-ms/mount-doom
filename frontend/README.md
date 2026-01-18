# Mount Doom Frontend

Next.js frontend for the Mount Doom AI Agent Simulation platform. Built with TypeScript and Ant Design components.

## Features

### Single Agents
- **Persona Distribution Generator** - Generate persona distributions from simulation prompts
- **Persona Generator** - Generate exact customer personas with metadata
- **Transcript Parser** - Parse transcripts to extract intent, subject, and sentiment
- **C2 Message Generator** - Generate customer messages for conversation simulations

### Multi-Agent Workflows
- **Conversation Simulation** - Complex multi-agent conversation simulation with real-time tracking

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
│   ├── agents/                              # Dynamic agent pages
│   │   └── [agentId]/                       # Dynamic route for any agent
│   ├── workflows/                           # Workflow pages
│   │   └── conversation_simulation/         # Conversation simulation workflow
│   ├── c2-message-generation/               # C2 message generation page
│   ├── conversation-simulation/             # Conversation simulation page
│   ├── persona-distribution/                # Persona distribution page
│   ├── persona-generator/                   # Persona generator page
│   ├── transcript-parser/                   # Transcript parser page
│   ├── layout.tsx                           # Root layout with timezone provider
│   ├── page.tsx                             # Home page
│   └── globals.css                          # Global styles
├── components/                               # React components
│   ├── PageLayout.tsx                       # Shared page layout with navigation
│   ├── SingleAgentTemplate.tsx              # Template for single-agent pages
│   └── MultiAgentTemplate.tsx               # Template for multi-agent workflows
├── lib/                                     # Utility libraries
│   ├── api-client.ts                        # Type-safe API client
│   ├── types.ts                             # Shared TypeScript types
│   └── timezone-context.tsx                 # Global timezone context (UTC/IST)
└── public/                                  # Static assets
```

## Features Detail

### Template-Based Pages

The application uses reusable templates for consistency:

**SingleAgentTemplate**: Used for single-agent features
- Three tabs: Generate, Batch Processing, History
- Form input with sample prompts
- Real-time results display
- Batch processing with configurable delays
- Paginated history with filtering and sorting

**MultiAgentTemplate**: Used for multi-agent workflows
- Three tabs: Simulate, Batch Processing, History
- Multi-field configuration forms
- Conversation history with expandable turns
- Batch simulation support
- Paginated results with detailed metrics

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
