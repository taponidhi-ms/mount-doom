---
paths:
  - "frontend/**/*.{ts,tsx,js,jsx}"
---

# Frontend Architecture

## Structure

```
frontend/
├── app/                        # Next.js App Router pages
│   ├── agents/                 # Nested routes for agents
│   │   ├── download/           # Multi-agent download page
│   │   │   └── page.tsx
│   │   └── [agentId]/          # Dynamic route for any agent
│   │       ├── layout.tsx      # Agent layout (loads info, provides context)
│   │       ├── page.tsx        # Generate page (default)
│   │       ├── batch/
│   │       │   └── page.tsx    # Batch processing page
│   │       └── history/
│   │           └── page.tsx    # History page
│   └── workflows/              # Workflow pages
│       └── conversation_simulation/
│           └── page.tsx
├── components/                 # React components
│   ├── PageLayout.tsx          # Reusable page layout with navigation
│   └── agents/                 # Modular agent components
│       ├── shared/
│       │   ├── AgentContext.tsx    # React Context for agent info
│       │   └── AgentTabs.tsx       # Tab navigation
│       ├── result/
│       │   ├── AgentResultModal.tsx # Modal for viewing results
│       │   └── AgentResultCard.tsx  # Inline result display
│       ├── instructions/
│       │   └── AgentInstructionsCard.tsx # Collapsible instructions
│       ├── batch/
│       │   └── BatchProcessingSection.tsx # Complete batch UI
│       └── history/
│           └── AgentHistoryTable.tsx # Full-featured history table
└── lib/                        # Utilities and API client
    ├── api-client.ts           # Backend API client (includes agents and workflows APIs)
    ├── types.ts                # Shared TypeScript types
    └── timezone-context.tsx    # Global timezone context (UTC/IST)
```

## Key Principles

- **Modular component architecture**: Reusable components extracted from monolithic pages
- **Nested routes with layouts**: Agent info loaded once in layout, shared via React Context
- **URL-based navigation**: Each tab is a separate route with browser back/forward support
- **Global timezone support**: User can toggle between UTC and IST (default: IST)
- **Dynamic routing**: Agents pages use dynamic [agentId] routing
- **Instructions display**: All agent pages show the agent's instruction set
- Component reusability across features
- Type safety with TypeScript
- Responsive design with Ant Design
- Accessible UI with Ant Design components

## Navigation Structure

The navigation sidebar organizes pages into two main sections:
- **Agents** - Individual agents that operate independently
  - Persona Distribution Generator
  - Persona Generator
  - Transcript Parser
  - C2 Message Generator
  - Downloads (multi-agent download page)
- **Workflows** - Multi-agent orchestration with custom logic
  - Conversation Simulation

## Agent Pages Architecture

### Nested Routes Structure

Agent pages use Next.js nested routes:
- `/agents/[agentId]` - Generate page (default)
- `/agents/[agentId]/batch` - Batch processing page
- `/agents/[agentId]/history` - History page
- `/agents/download` - Multi-agent download page

### Layout Component

The `layout.tsx` file:
- Loads agent info once via API on mount
- Provides agent info to all child pages via `AgentContext`
- Renders tab navigation via `AgentTabs` component
- Handles loading and error states

### Reusable Components

- **AgentContext** - React Context for sharing agent info
- **AgentTabs** - Tab-like navigation using Next.js Link
- **AgentResultModal** - Result viewing modal with JSON/Plain Text toggle
- **AgentResultCard** - Inline result display
- **AgentInstructionsCard** - Collapsible instructions display
- **BatchProcessingSection** - Complete batch processing UI with progress tracking
- **AgentHistoryTable** - Full-featured history table with sorting, filtering, bulk operations, column visibility controls

## Workflow Pages

Workflows that orchestrate multiple agents have custom implementations:
- Each workflow has unique UI requirements and orchestration logic
- No shared template - each page implements its own three-tab structure
- Tab structure: Simulate, Batch Processing, History
- Custom conversation rendering and history columns
- Expandable rows in history table for viewing multi-turn conversation details
- Workflows manage stateful interactions between multiple agents

## Timezone Context

Global timezone management via React Context:
- Provider: `TimezoneProvider` wraps the app in layout.tsx
- Hook: `useTimezone()` returns `{ timezone, setTimezone, formatTimestamp, formatTime }`
- Supported timezones: UTC, IST (Asia/Kolkata)
- Default: IST
- Persisted to localStorage

## Routing

Agent pages use URL-based navigation:
- `/agents/persona_generator` - Persona Generator (Generate tab)
- `/agents/persona_generator/batch` - Batch Processing tab
- `/agents/persona_generator/history` - History tab
- `/agents/download` - Multi-agent download page
- Browser back/forward navigation works
- URLs are shareable

## UI Components (Ant Design)

Standard components used across pages:
- `Button` - Primary actions (with loading states)
- `Card` - Content containers
- `Tabs` - Generate/History navigation
- `Table` - Display history with pagination
- `Input` - Form inputs (Input, TextArea)
- `Space` - Layout spacing
- `Typography` - Text elements (Title, Paragraph, Text)
- `Alert` - Error and info messages
- `message` - Toast notifications
- `Tag` - Status and label indicators

## Page Structure Pattern

All feature pages follow this structure:
1. **Header**: Title and description (via PageLayout component)
2. **Tabs**: Generate/Validate/Simulate tab, Batch Processing tab, and History tab
3. **Generate/Validate/Simulate Tab**: Configuration form, Submit button, Result display
4. **Batch Processing Tab**: JSON input, configurable delay, progress display, results table
5. **History Tab**: Table with past results, pagination controls

## Performance Considerations

- Lazy load components
- Optimize images
- Minimize bundle size
- Use Next.js optimization features
