---
paths:
  - "frontend/**/*.{ts,tsx,js,jsx}"
---

# Frontend Development Conventions (TypeScript/Next.js)

## Code Style

- Use TypeScript for all files
- Use 'use client' directive for client components
- Server components by default
- Proper error boundaries

## Modular Component Pattern

Agent pages use a modular architecture with nested routes and reusable components.

### Agent Pages Structure

Agent pages use Next.js nested routes with a shared layout:

**Layout** (`/agents/[agentId]/layout.tsx`):
- Loads agent info once via `apiClient.getAgent(agentId)`
- Provides agent info to children via `AgentContext`
- Renders `AgentTabs` navigation
- Handles loading and error states

**Generate Page** (`/agents/[agentId]/page.tsx`):
```typescript
'use client'

import { useState } from 'react'
import { useParams } from 'next/navigation'
import { useAgentContext } from '@/components/agents/shared/AgentContext'
import AgentInstructionsCard from '@/components/agents/instructions/AgentInstructionsCard'
import AgentResultCard from '@/components/agents/result/AgentResultCard'
import { apiClient } from '@/lib/api-client'

export default function AgentGeneratePage() {
  const params = useParams()
  const agentId = params.agentId as string
  const { agentInfo } = useAgentContext()

  // State and handlers...

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <AgentInstructionsCard instructions={agentInfo.instructions} />
      {/* Form and input fields */}
      {result && <AgentResultCard result={result} />}
    </Space>
  )
}
```

**Reusable Components**:
- **AgentContext** - Share agent info across pages
- **AgentInstructionsCard** - Collapsible instructions display
- **AgentResultCard** - Inline result display with JSON/Plain Text toggle
- **AgentResultModal** - Modal for viewing result details
- **BatchProcessingSection** - Complete batch processing UI
- **AgentHistoryTable** - Full-featured history table with auto-load
- **AgentTabs** - Tab-like navigation

### Workflow Pages Pattern

For workflows that orchestrate multiple agents, implement custom pages with:
- Three tabs: Simulate, Batch Processing, History
- All state management within the page component
- Custom rendering for conversation display
- Custom history columns specific to workflow needs

## Timezone Handling

- Always use `useTimezone()` hook to access `formatTimestamp()` and `formatTime()` functions
- Never use raw `toLocaleString()` or `toISOString()` for user-facing timestamps
- Timezone state is global and persisted to localStorage
- Default timezone is IST (Asia/Kolkata)

## Naming Conventions

- Components: PascalCase (e.g., `ResultDisplay`)
- Files: kebab-case (e.g., `api-client.ts`)
- Functions: camelCase (e.g., `handleSubmit`)
- Constants: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)

## Component Structure

- Props interfaces defined inline or separately
- State management with useState
- Side effects with useEffect
- Form handling with controlled components
- Tab-based navigation for generate/history views

## Styling

- Ant Design components with default styling
- Inline styles for custom layouts
- Responsive design with Ant Design grid system
- Proper accessibility with ARIA labels and semantic HTML

## Batch Processing Pattern

When adding batch support to a page:

**State Management**:
```typescript
const [batchItems, setBatchItems] = useState<BatchItem[]>([])
const [batchLoading, setBatchLoading] = useState(false)
const [batchProgress, setBatchProgress] = useState(0)
const [currentBatchIndex, setCurrentBatchIndex] = useState(-1)
const [batchJsonInput, setBatchJsonInput] = useState('')
const [stopBatchRequested, setStopBatchRequested] = useState(false)
const [batchDelay, setBatchDelay] = useState(5)
```

**BatchItem Interface**:
- For agents: `{ key, prompt, status, result?, error? }`
- For workflows: `{ key, customerIntent, customerSentiment, conversationSubject, status, result?, error? }`

**Core Functions**:
1. `loadBatchItemsFromText()` - Parse JSON (array or object with items array)
2. `runBatchProcessing()` - Main loop with delays and stop handling
3. `handleStopBatch()` - Set stop flag to gracefully exit

**UI Components**:
- TextArea for JSON input
- Select component for delay selection (5-60 seconds)
- Buttons: "Load Items", "Start Batch", "Stop Batch"
- Progress bar with current item indicator
- Table with Status column and expandable rows

## Environment Configuration

- Use NEXT_PUBLIC_ prefix for public variables
- Provide .env.local.example template
- Keep API URL configurable
- Never expose backend secrets

Example:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Feature Change Validation

When making changes to any feature, **ALWAYS validate compatibility between backend and frontend**:

### 1. API Contract Validation
- Verify request schemas match between `backend/app/modules/[feature]/models.py` and `frontend/lib/api-client.ts`
- Verify response schemas match between backend Pydantic models and frontend TypeScript types
- Check that field names, types, and optional/required status are consistent

### 2. Endpoint Validation
- Confirm route paths in `backend/app/modules/[feature]/routes.py` match API calls in `frontend/lib/api-client.ts`
- Verify HTTP methods (GET, POST, etc.) are consistent
- Check query parameters and request body structures

### 3. Type Alignment Checklist
- Backend Pydantic `BaseModel` ↔ Frontend TypeScript `interface`
- Backend `Optional[X]` ↔ Frontend `X | null` or `X?`
- Backend `datetime` ↔ Frontend `string` (ISO format)
- Backend `List[X]` ↔ Frontend `X[]`
- Backend `Dict[str, Any]` ↔ Frontend `Record<string, any>`

### 4. Test After Changes
- Run the backend server and verify endpoints respond correctly
- Test frontend API calls to ensure no type mismatches or 422 errors
- Check browser console for any parsing or type errors
