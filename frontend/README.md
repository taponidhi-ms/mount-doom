# Mount Doom Frontend

Next.js frontend for the Mount Doom AI Agent Simulation platform. Built with TypeScript, Tailwind CSS, and shadcn/ui components.

## Features

- **Persona Generation** - Interactive interface for generating personas from simulation prompts
- **General Prompt** - Direct interaction with LLM models for general-purpose responses
- **Prompt Validator** - Validation interface for simulation prompts
- **Conversation Simulation** - Complex multi-agent conversation simulation with real-time tracking

## Tech Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **UI Components**: shadcn/ui (manually configured)
- **Icons**: Lucide React
- **API Client**: Custom fetch-based client

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
├── app/                              # Next.js App Router pages
│   ├── persona-generation/          # Persona generation page
│   ├── general-prompt/              # General prompt page
│   ├── prompt-validator/            # Prompt validator page
│   ├── conversation-simulation/     # Conversation simulation page
│   ├── layout.tsx                   # Root layout
│   ├── page.tsx                     # Home page
│   └── globals.css                  # Global styles
├── components/                       # React components
│   ├── ui/                          # shadcn/ui components
│   └── result-display.tsx           # Shared result display component
├── lib/                             # Utility libraries
│   ├── api-client.ts                # API client for backend communication
│   └── utils.ts                     # Utility functions
└── public/                          # Static assets
```

## Features Detail

### Result Display Component

All use case pages use a shared `ResultDisplay` component that shows:
- Response text or conversation history
- Token usage metrics
- Time taken for each request
- Start and end timestamps
- Copy-to-clipboard functionality for JSON
- Expandable full JSON view

### API Client

The `api-client.ts` provides a type-safe interface for all backend endpoints:
- Automatic error handling
- TypeScript types for all requests/responses
- Promise-based async/await API

### Responsive Design

- Mobile-first design approach
- Responsive grid layouts
- Adaptive navigation
- Touch-friendly interfaces

## Environment Variables

Create a `.env.local` file with:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, set this to your deployed backend URL.

## License

Copyright (c) 2025. All rights reserved.
