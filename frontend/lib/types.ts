/**
 * Shared types for agents and workflows.
 *
 * Naming conventions:
 * - Agent types: For individual agent operations (invoke, browse, delete)
 * - Workflow types: For multi-agent workflows with custom logic
 */

import { ReactNode } from 'react'

// ============================================================================
// Common Types
// ============================================================================

// Agent details type (shared across responses)
export interface AgentDetails {
  agent_name: string
  agent_version?: string
  instructions: string
  model_deployment_name: string
  created_at: string
}

export interface ApiResponse<T> {
  data?: T
  error?: string
}

export interface BrowseResponse<T = any> {
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

// ============================================================================
// Agent Types (for individual agent operations)
// ============================================================================

/**
 * Response from agent invoke operation
 * Matches backend: SingleAgentResponse
 */
export interface AgentInvokeResponse {
  response_text: string
  tokens_used?: number
  time_taken_ms: number
  start_time: string
  end_time: string
  agent_details: AgentDetails
  conversation_id: string
  parsed_output?: Record<string, unknown>
  from_cache?: boolean
}

/**
 * History item for agent operations (from Cosmos DB)
 * Matches backend: SingleAgentDocument with additional fields
 */
export interface AgentHistoryItem {
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
  agent_version?: string
  agent_instructions?: string
  prompt_category?: string  // Category of the prompt
  prompt_tags?: string[]    // Tags associated with the prompt
  from_cache?: boolean      // Whether response was from cache
}

/**
 * Agent info returned from get/list agents endpoint
 * Matches backend agent registry configuration
 */
export interface AgentInfo {
  agent_id: string
  agent_name: string
  display_name: string
  description: string
  instructions: string
  input_field: string
  input_label: string
  input_placeholder: string
  sample_inputs: SampleInput[]
}

export interface SampleInput {
  label?: string
  value: string
  category?: string  // Optional category like "Valid", "Invalid", "Edge Case"
  tags?: string[]    // Optional tags for organization
}

export interface HistoryColumnConfig<T = AgentHistoryItem> {
  title: string
  dataIndex: string | string[]
  key: string
  width?: number
  ellipsis?: boolean | { showTitle: boolean }
  render?: (value: unknown, record: T) => ReactNode
  visible?: boolean
}

/**
 * Agent version info for multi-agent download
 * Matches backend: AgentVersionInfo (eval format specific)
 */
export interface AgentVersionInfo {
  agent_id: string
  agent_name: string
  version: string
  conversation_count: number
  scenario_name: string
}

/**
 * Agent version selection for multi-agent download
 * Matches backend: AgentVersionSelection (eval format specific)
 */
export interface AgentVersionSelection {
  agent_id: string
  version: string
  limit?: number  // Optional limit on number of conversations to download
}

// ============================================================================
// Workflow Types (for multi-agent workflows)
// ============================================================================

/**
 * A single message in a conversation workflow
 * Matches backend: ConversationMessage
 */
export interface ConversationMessage {
  role: string  // "agent" or "customer"
  content: string
  tokens_used?: number  // Populated for both agent and customer messages
  timestamp: string
  conversation_id?: string  // Azure AI conversation_id for the message
}

/**
 * Response from conversation simulation workflow
 * Matches backend: ConversationSimulationResponse
 */
export interface ConversationSimulationResponse {
  conversation_history: ConversationMessage[]
  conversation_status: string
  total_time_taken_ms: number
  start_time: string
  end_time: string
  conversation_id: string
  agent_details?: AgentDetails // Primary agent (C1) details
  [key: string]: unknown // Allow additional workflow-specific fields
}

/**
 * History item for workflow operations (from Cosmos DB)
 * Matches backend: ConversationSimulationDocument with additional fields
 */
export interface WorkflowHistoryItem {
  id: string
  timestamp: string
  conversation_id: string
  conversation_history: ConversationMessage[]
  conversation_status: string
  conversation_properties?: Record<string, unknown>
  total_tokens_used?: number
  total_time_taken_ms?: number
}

// ============================================================================
// Legacy Type Aliases (for backward compatibility during migration)
// ============================================================================

/** @deprecated Use AgentInvokeResponse instead */
export type SingleAgentResponse = AgentInvokeResponse

/** @deprecated Use AgentHistoryItem instead */
export type SingleAgentHistoryItem = AgentHistoryItem

/** @deprecated Use ConversationSimulationResponse instead */
export type MultiAgentResponse = ConversationSimulationResponse

/** @deprecated Use WorkflowHistoryItem instead */
export type MultiAgentHistoryItem = WorkflowHistoryItem
