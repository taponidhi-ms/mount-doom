'use client'

import { createContext, useContext, ReactNode } from 'react'
import type { AgentInfo } from '@/lib/api-client'

interface AgentContextValue {
  agentInfo: AgentInfo | null
  loadingAgent: boolean
  agentError: string
}

const AgentContext = createContext<AgentContextValue | undefined>(undefined)

export function useAgentContext() {
  const context = useContext(AgentContext)
  if (!context) {
    throw new Error('useAgentContext must be used within AgentProvider')
  }
  return context
}

interface AgentProviderProps {
  children: ReactNode
  value: AgentContextValue
}

export function AgentProvider({ children, value }: AgentProviderProps) {
  return (
    <AgentContext.Provider value={value}>
      {children}
    </AgentContext.Provider>
  )
}
