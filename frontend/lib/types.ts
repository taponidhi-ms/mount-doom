/**
 * Shared types for single agent and multi-agent templates
 */

import { ReactNode } from 'react'

// Agent details type (shared across responses)
export interface AgentDetails {
  agent_name: string
  agent_version?: string
  instructions: string
  model_deployment_name: string
  created_at: string
}

// Base response for single agent operations
export interface SingleAgentResponse {
  response_text: string
  tokens_used?: number
  time_taken_ms: number
  start_time: string
  end_time: string
  agent_details: AgentDetails
  conversation_id: string
  parsed_output?: Record<string, unknown>
}

// History item for single agent (from Cosmos DB)
export interface SingleAgentHistoryItem {
  id: string
  conversation_id?: string
  timestamp: string
  prompt?: string
  transcript?: string
  response?: string
  response_text?: string
  tokens_used?: number
  time_taken_ms?: number
  parsed_output?: Record<string, unknown>
  agent_details?: {
    agent_name: string
    agent_version?: string
    model_deployment_name: string
  }
}

// Configuration for a single agent page
export interface SingleAgentConfig {
  // Page metadata
  title: string
  description: string
  pageKey: string
  
  // Input configuration
  inputLabel: string
  inputPlaceholder: string
  inputFieldName: 'prompt' | 'transcript' // What field name is sent to API
  
  // Sample prompts/inputs
  sampleInputs: SampleInput[]
  
  // API functions
  generateFn: (input: string) => Promise<ApiResponse<SingleAgentResponse>>
  browseFn: (page: number, pageSize: number, orderBy: string, orderDirection: 'ASC' | 'DESC') => Promise<ApiResponse<BrowseResponse>>
  deleteFn: (ids: string[]) => Promise<ApiResponse<DeleteResponse>>
  downloadFn: (ids: string[]) => Promise<ApiResponse<Blob>>
  
  // History table column customization
  historyColumns?: HistoryColumnConfig[]
  
  // Result display customization
  renderParsedOutput?: (parsedOutput: Record<string, unknown>) => ReactNode
}

export interface SampleInput {
  label?: string
  value: string
}

export interface HistoryColumnConfig<T = SingleAgentHistoryItem> {
  title: string
  dataIndex: string | string[]
  key: string
  width?: number
  ellipsis?: boolean
  render?: (value: unknown, record: T) => ReactNode
}

// Alias for multi-agent history columns
export type MultiAgentHistoryColumnConfig = HistoryColumnConfig<MultiAgentHistoryItem>

export interface BrowseResponse<T = SingleAgentHistoryItem> {
  items: T[]
  total_count: number
  page: number
  page_size: number
  total_pages: number
  has_next: boolean
  has_previous: boolean
}

export interface DeleteResponse {
  deleted_count: number
  failed_count: number
  errors: string[]
}

export interface ApiResponse<T> {
  data?: T
  error?: string
}

// Batch processing types
export interface BatchItem<TResult = SingleAgentResponse> {
  key: string
  input: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  result?: TResult
  error?: string
}

// Multi-agent types
export interface ConversationMessage {
  role: string  // "agent" or "customer"
  content: string
  tokens_used?: number  // Populated for both agent and customer messages
  timestamp: string
  conversation_id?: string  // Azure AI conversation_id for the message
}

export interface MultiAgentResponse {
  conversation_history: ConversationMessage[]
  conversation_status: string
  total_time_taken_ms: number
  start_time: string
  end_time: string
  conversation_id: string
  agent_details?: AgentDetails // Primary agent (C1) details
  [key: string]: unknown // Allow additional agent-specific fields
}

export interface MultiAgentHistoryItem {
  id: string
  timestamp: string
  conversation_id: string
  conversation_history: ConversationMessage[]
  conversation_status: string
  conversation_properties?: Record<string, unknown>
  total_tokens_used?: number
  total_time_taken_ms?: number
}

export interface MultiAgentConfig {
  title: string
  description: string
  pageKey: string
  
  // Input fields configuration
  inputFields: InputFieldConfig[]
  
  // Sample configurations
  sampleConfigs: Record<string, string>[]
  
  // API functions
  simulateFn: (inputs: Record<string, string>) => Promise<ApiResponse<MultiAgentResponse>>
  browseFn: (page: number, pageSize: number, orderBy: string, orderDirection: 'ASC' | 'DESC') => Promise<ApiResponse<BrowseResponse<MultiAgentHistoryItem>>>
  deleteFn: (ids: string[]) => Promise<ApiResponse<DeleteResponse>>
  downloadFn: (ids: string[]) => Promise<ApiResponse<Blob>>
  
  // History table columns
  historyColumns?: MultiAgentHistoryColumnConfig[]
  
  // Conversation display customization
  renderConversation?: (history: ConversationMessage[]) => ReactNode
}

export interface InputFieldConfig {
  name: string
  label: string
  placeholder: string
  type?: 'text' | 'textarea'
  required?: boolean
}
