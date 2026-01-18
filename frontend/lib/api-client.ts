/**
 * API Client for Mount Doom Backend
 * 
 * This module provides a typed interface for interacting with the backend API.
 */

import type {
  ApiResponse,
  BrowseResponse,
  DeleteResponse,
  ConversationMessage,
  MultiAgentHistoryItem,
} from './types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Re-export types from the types module
export type {
  SingleAgentResponse,
  SingleAgentHistoryItem,
  BrowseResponse,
  DeleteResponse,
  ApiResponse,
  ConversationMessage,
  MultiAgentResponse,
  MultiAgentHistoryItem,
} from './types'

// Shared types
export interface AgentDetails {
  agent_name: string;
  agent_version?: string;
  instructions: string;
  model_deployment_name: string;
  created_at: string;
}

export interface BaseResponse {
  response_text: string;
  tokens_used?: number;
  time_taken_ms: number;
  start_time: string;
  end_time: string;
  agent_details: AgentDetails;
}

export interface ModelInfo {
  model_deployment_name: string;
  display_name: string;
  description?: string;
}

export interface AvailableModelsResponse {
  models: ModelInfo[];
}

// Persona Distribution
export interface PersonaDistributionRequest {
  prompt: string;
  model?: string;
  stream?: boolean;
}

export interface PersonaDistributionResponse extends BaseResponse {
  parsed_output?: Record<string, unknown>;
}

// Persona Generator
export interface PersonaGeneratorRequest {
  prompt: string;
}

export interface PersonaGeneratorResponse extends BaseResponse {
  parsed_output?: Record<string, unknown>;
}

// Transcript Parser
export interface TranscriptParserRequest {
  transcript: string;
}

export interface TranscriptParserResponse extends BaseResponse {
  parsed_output?: Record<string, unknown>;
}

// Conversation Simulation
export interface ConversationSimulationRequest {
  customer_intent: string;
  customer_sentiment: string;
  conversation_subject: string;
  stream?: boolean;
}

// Use ConversationMessage from ./types (re-exported above)

export interface ConversationSimulationResponse {
  conversation_history: import('./types').ConversationMessage[];
  conversation_status: string;
  total_time_taken_ms: number;
  start_time: string;
  end_time: string;
  c1_agent_details: AgentDetails;
  c2_agent_details: AgentDetails;
  conversation_id: string;
}

// C2 Message Generation
export interface C2MessageGenerationRequest {
  prompt: string;
}

export interface C2MessageGenerationResponse extends BaseResponse {}

// ========================================
// Unified Agents API Types
// ========================================

export interface AgentInfo {
  agent_id: string;
  agent_name: string;
  display_name: string;
  description: string;
  instructions: string;
  input_field: string;
  input_label: string;
  input_placeholder: string;
}

export interface AgentListResponse {
  agents: AgentInfo[];
}

export interface AgentInvokeResponse {
  response_text: string;
  tokens_used?: number;
  time_taken_ms: number;
  start_time: string;
  end_time: string;
  agent_details: Record<string, unknown>;
  parsed_output?: Record<string, unknown>;
}

// ========================================
// Workflows API Types
// ========================================

export interface WorkflowAgentInfo {
  agent_id: string;
  agent_name: string;
  display_name: string;
  role: string;
  instructions: string;
}

export interface WorkflowInfo {
  workflow_id: string;
  display_name: string;
  description: string;
  agents: WorkflowAgentInfo[];
  route_prefix: string;
}

export interface WorkflowListResponse {
  workflows: WorkflowInfo[];
}

// API Response wrapper (internal)
interface InternalApiResponse<T> {
  data?: T;
  error?: string;
}

// API Client Class
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<InternalApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return {
          error: errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
        };
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'An unknown error occurred',
      };
    }
  }

  private async requestBlob(
    endpoint: string,
    options?: RequestInit
  ): Promise<InternalApiResponse<Blob>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers: {
          ...options?.headers,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return {
          error: errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
        };
      }

      const data = await response.blob();
      return { data };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'An unknown error occurred',
      };
    }
  }

  // Models API - Removed (GPT-4 is hardcoded in backend)

  // Persona Distribution APIs (calls unified agents API)
  async generatePersonaDistribution(
    prompt: string
  ): Promise<ApiResponse<PersonaDistributionResponse>> {
    return this.invokeAgent('persona_distribution', prompt) as Promise<ApiResponse<PersonaDistributionResponse>>;
  }

  async browsePersonaDistributions(
    page: number = 1,
    pageSize: number = 10,
    orderBy: string = 'timestamp',
    orderDirection: 'ASC' | 'DESC' = 'DESC'
  ): Promise<ApiResponse<BrowseResponse>> {
    return this.browseAgentHistory('persona_distribution', page, pageSize, orderBy, orderDirection);
  }

  async deletePersonaDistributions(ids: string[]): Promise<ApiResponse<{ deleted_count: number; failed_count: number; errors: string[] }>> {
    return this.deleteAgentRecords('persona_distribution', ids);
  }

  async downloadPersonaDistributions(ids: string[]): Promise<ApiResponse<Blob>> {
    return this.downloadAgentRecords('persona_distribution', ids);
  }

  // Persona Generator APIs (calls unified agents API)
  async generatePersonas(
    prompt: string
  ): Promise<ApiResponse<PersonaGeneratorResponse>> {
    return this.invokeAgent('persona_generator', prompt) as Promise<ApiResponse<PersonaGeneratorResponse>>;
  }

  async browsePersonaGenerations(
    page: number = 1,
    pageSize: number = 10,
    orderBy: string = 'timestamp',
    orderDirection: 'ASC' | 'DESC' = 'DESC'
  ): Promise<ApiResponse<BrowseResponse>> {
    return this.browseAgentHistory('persona_generator', page, pageSize, orderBy, orderDirection);
  }

  async deletePersonaGenerations(ids: string[]): Promise<ApiResponse<{ deleted_count: number; failed_count: number; errors: string[] }>> {
    return this.deleteAgentRecords('persona_generator', ids);
  }

  // Transcript Parser APIs (calls unified agents API)
  async parseTranscript(
    transcript: string
  ): Promise<ApiResponse<TranscriptParserResponse>> {
    return this.invokeAgent('transcript_parser', transcript) as Promise<ApiResponse<TranscriptParserResponse>>;
  }

  async browseTranscripts(
    page: number = 1,
    pageSize: number = 10,
    orderBy: string = 'timestamp',
    orderDirection: 'ASC' | 'DESC' = 'DESC'
  ): Promise<ApiResponse<BrowseResponse>> {
    return this.browseAgentHistory('transcript_parser', page, pageSize, orderBy, orderDirection);
  }

  async deleteTranscripts(ids: string[]): Promise<ApiResponse<{ deleted_count: number; failed_count: number; errors: string[] }>> {
    return this.deleteAgentRecords('transcript_parser', ids);
  }

  // Conversation Simulation APIs
  async simulateConversation(
    customer_intent: string,
    customer_sentiment: string,
    conversation_subject: string
  ): Promise<ApiResponse<ConversationSimulationResponse>> {
    return this.request<ConversationSimulationResponse>('/api/v1/conversation-simulation/simulate', {
      method: 'POST',
      body: JSON.stringify({
        customer_intent,
        customer_sentiment,
        conversation_subject,
      }),
    });
  }

  async browseConversationSimulations(
    page: number = 1,
    pageSize: number = 10,
    orderBy: string = 'timestamp',
    orderDirection: 'ASC' | 'DESC' = 'DESC'
  ): Promise<ApiResponse<BrowseResponse<MultiAgentHistoryItem>>> {
    return this.request<BrowseResponse<MultiAgentHistoryItem>>(
      `/api/v1/conversation-simulation/browse?page=${page}&page_size=${pageSize}&order_by=${orderBy}&order_direction=${orderDirection}`
    );
  }

  async deleteConversationSimulations(
    conversationIds: string[]
  ): Promise<ApiResponse<{ deleted_count: number; failed_count: number; errors: string[] }>> {
    return this.request<{ deleted_count: number; failed_count: number; errors: string[] }>(
      '/api/v1/conversation-simulation/delete',
      {
        method: 'POST',
        body: JSON.stringify(conversationIds),
      }
    );
  }


  async downloadConversationSimulations(conversationIds: string[]): Promise<ApiResponse<Blob>> {
    return this.requestBlob(`/api/v1/conversation-simulation/download`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(conversationIds),
    });
  }

  // C2 Message Generation APIs (calls unified agents API)
  async generateC2Message(
    prompt: string
  ): Promise<ApiResponse<C2MessageGenerationResponse>> {
    return this.invokeAgent('c2_message_generation', prompt) as Promise<ApiResponse<C2MessageGenerationResponse>>;
  }

  async browseC2MessageGenerations(
    page: number = 1,
    pageSize: number = 10,
    orderBy: string = 'timestamp',
    orderDirection: 'ASC' | 'DESC' = 'DESC'
  ): Promise<ApiResponse<BrowseResponse>> {
    return this.browseAgentHistory('c2_message_generation', page, pageSize, orderBy, orderDirection);
  }

  async deleteC2MessageGenerations(ids: string[]): Promise<ApiResponse<{ deleted_count: number; failed_count: number; errors: string[] }>> {
    return this.deleteAgentRecords('c2_message_generation', ids);
  }

  async downloadC2MessageGenerations(ids: string[]): Promise<ApiResponse<Blob>> {
    return this.downloadAgentRecords('c2_message_generation', ids);
  }

  // ========================================
  // Unified Agents APIs
  // ========================================

  async listAgents(): Promise<ApiResponse<AgentListResponse>> {
    return this.request<AgentListResponse>('/api/v1/agents/list');
  }

  async getAgent(agentId: string): Promise<ApiResponse<AgentInfo>> {
    return this.request<AgentInfo>(`/api/v1/agents/${agentId}`);
  }

  async invokeAgent(
    agentId: string,
    input: string
  ): Promise<ApiResponse<AgentInvokeResponse>> {
    return this.request<AgentInvokeResponse>(`/api/v1/agents/${agentId}/invoke`, {
      method: 'POST',
      body: JSON.stringify({ input }),
    });
  }

  async browseAgentHistory(
    agentId: string,
    page: number = 1,
    pageSize: number = 10,
    orderBy: string = 'timestamp',
    orderDirection: 'ASC' | 'DESC' = 'DESC'
  ): Promise<ApiResponse<BrowseResponse>> {
    return this.request<BrowseResponse>(
      `/api/v1/agents/${agentId}/browse?page=${page}&page_size=${pageSize}&order_by=${orderBy}&order_direction=${orderDirection}`
    );
  }

  async deleteAgentRecords(agentId: string, ids: string[]): Promise<ApiResponse<{ deleted_count: number; failed_count: number; errors: string[] }>> {
    return this.request(`/api/v1/agents/${agentId}/delete`, {
      method: 'POST',
      body: JSON.stringify(ids),
    });
  }

  async downloadAgentRecords(agentId: string, ids: string[]): Promise<ApiResponse<Blob>> {
    return this.requestBlob(`/api/v1/agents/${agentId}/download`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(ids),
    });
  }

  // ========================================
  // Workflows APIs
  // ========================================

  async listWorkflows(): Promise<ApiResponse<WorkflowListResponse>> {
    return this.request<WorkflowListResponse>('/api/v1/workflows/list');
  }

  async getWorkflow(workflowId: string): Promise<ApiResponse<WorkflowInfo>> {
    return this.request<WorkflowInfo>(`/api/v1/workflows/${workflowId}`);
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export class for testing
export { ApiClient };
