/**
 * API Client for Mount Doom Backend
 * 
 * This module provides a typed interface for interacting with the backend API.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Types
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

// Browse/Pagination Types
export interface BrowseResponse<T = any> {
  items: T[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

// Persona Distribution
export interface PersonaDistributionRequest {
  prompt: string;
  model?: string;
  stream?: boolean;
}

export interface PersonaDistributionResponse extends BaseResponse {
  parsed_output?: any;
}

// Persona Generator
export interface PersonaGeneratorRequest {
  prompt: string;
}

export interface PersonaGeneratorResponse extends BaseResponse {
  parsed_output?: any;
}

// Transcript Parser
export interface TranscriptParserRequest {
  transcript: string;
}

export interface TranscriptParserResponse extends BaseResponse {
  parsed_output?: any;
}

// Conversation Simulation
export interface ConversationSimulationRequest {
  customer_intent: string;
  customer_sentiment: string;
  conversation_subject: string;
  stream?: boolean;
}

export interface ConversationMessage {
  agent_name: string;
  message: string;
  timestamp: string;
}

export interface ConversationSimulationResponse {
  conversation_history: ConversationMessage[];
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

// API Response wrapper
interface ApiResponse<T> {
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
  ): Promise<ApiResponse<T>> {
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
  ): Promise<ApiResponse<Blob>> {
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

  // Persona Distribution APIs
  async generatePersonaDistribution(
    prompt: string
  ): Promise<ApiResponse<PersonaDistributionResponse>> {
    return this.request<PersonaDistributionResponse>('/api/v1/persona-distribution/generate', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    });
  }

  async browsePersonaDistributions(
    page: number = 1,
    pageSize: number = 10,
    orderBy: string = 'timestamp',
    orderDirection: 'ASC' | 'DESC' = 'DESC'
  ): Promise<ApiResponse<BrowseResponse>> {
    return this.request<BrowseResponse>(
      `/api/v1/persona-distribution/browse?page=${page}&page_size=${pageSize}&order_by=${orderBy}&order_direction=${orderDirection}`
    );
  }

  async deletePersonaDistributions(ids: string[]): Promise<ApiResponse<{ deleted_count: number; failed_count: number; errors: string[] }>> {
    return this.request('/api/v1/persona-distribution/delete', {
      method: 'POST',
      body: JSON.stringify(ids),
    });
  }

  async downloadPersonaDistributions(ids: string[]): Promise<ApiResponse<Blob>> {
    return this.requestBlob(`/api/v1/persona-distribution/download`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(ids),
    });
  }

  // Persona Generator APIs
  async generatePersonas(
    prompt: string
  ): Promise<ApiResponse<PersonaGeneratorResponse>> {
    return this.request<PersonaGeneratorResponse>('/api/v1/persona-generator/generate', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    });
  }

  async browsePersonaGenerations(
    page: number = 1,
    pageSize: number = 10,
    orderBy: string = 'timestamp',
    orderDirection: 'ASC' | 'DESC' = 'DESC'
  ): Promise<ApiResponse<BrowseResponse>> {
    return this.request<BrowseResponse>(
      `/api/v1/persona-generator/browse?page=${page}&page_size=${pageSize}&order_by=${orderBy}&order_direction=${orderDirection}`
    );
  }

  async deletePersonaGenerations(ids: string[]): Promise<ApiResponse<{ deleted_count: number; failed_count: number; errors: string[] }>> {
    return this.request('/api/v1/persona-generator/delete', {
      method: 'POST',
      body: JSON.stringify(ids),
    });
  }

  // Transcript Parser APIs
  async parseTranscript(
    transcript: string
  ): Promise<ApiResponse<TranscriptParserResponse>> {
    return this.request<TranscriptParserResponse>('/api/v1/transcript-parser/parse', {
      method: 'POST',
      body: JSON.stringify({ transcript }),
    });
  }

  async browseTranscripts(
    page: number = 1,
    pageSize: number = 10,
    orderBy: string = 'timestamp',
    orderDirection: 'ASC' | 'DESC' = 'DESC'
  ): Promise<ApiResponse<BrowseResponse>> {
    return this.request<BrowseResponse>(
      `/api/v1/transcript-parser/browse?page=${page}&page_size=${pageSize}&order_by=${orderBy}&order_direction=${orderDirection}`
    );
  }

  async deleteTranscripts(ids: string[]): Promise<ApiResponse<{ deleted_count: number; failed_count: number; errors: string[] }>> {
    return this.request('/api/v1/transcript-parser/delete', {
      method: 'POST',
      body: JSON.stringify(ids),
    });
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

  async simulateConversationV2(
    customer_intent: string,
    customer_sentiment: string,
    conversation_subject: string
  ): Promise<ApiResponse<ConversationSimulationResponse>> {
    return this.request<ConversationSimulationResponse>('/api/v1/conversation-simulation-v2/simulate', {
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
  ): Promise<ApiResponse<BrowseResponse>> {
    return this.request<BrowseResponse>(
      `/api/v1/conversation-simulation/browse?page=${page}&page_size=${pageSize}&order_by=${orderBy}&order_direction=${orderDirection}`
    );
  }

  async browseConversationSimulationsV2(
    page: number = 1,
    pageSize: number = 10,
    orderBy: string = 'timestamp',
    orderDirection: 'ASC' | 'DESC' = 'DESC'
  ): Promise<ApiResponse<BrowseResponse>> {
    return this.request<BrowseResponse>(
      `/api/v1/conversation-simulation-v2/browse?page=${page}&page_size=${pageSize}&order_by=${orderBy}&order_direction=${orderDirection}`
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

  async deleteConversationSimulationsV2(
    conversationIds: string[]
  ): Promise<ApiResponse<{ deleted_count: number; failed_count: number; errors: string[] }>> {
    return this.request<{ deleted_count: number; failed_count: number; errors: string[] }>(
      '/api/v1/conversation-simulation-v2/delete',
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

  async downloadConversationSimulationsV2(conversationIds: string[]): Promise<ApiResponse<Blob>> {
    return this.requestBlob(`/api/v1/conversation-simulation-v2/download`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(conversationIds),
    });
  }

  // C2 Message Generation APIs
  async generateC2Message(
    prompt: string
  ): Promise<ApiResponse<C2MessageGenerationResponse>> {
    return this.request<C2MessageGenerationResponse>('/api/v1/c2-message-generation/generate', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    });
  }

  async browseC2MessageGenerations(
    page: number = 1,
    pageSize: number = 10,
    orderBy: string = 'timestamp',
    orderDirection: 'ASC' | 'DESC' = 'DESC'
  ): Promise<ApiResponse<BrowseResponse>> {
    return this.request<BrowseResponse>(
      `/api/v1/c2-message-generation/browse?page=${page}&page_size=${pageSize}&order_by=${orderBy}&order_direction=${orderDirection}`
    );
  }

  async deleteC2MessageGenerations(ids: string[]): Promise<ApiResponse<{ deleted_count: number; failed_count: number; errors: string[] }>> {
    return this.request('/api/v1/c2-message-generation/delete', {
      method: 'POST',
      body: JSON.stringify(ids),
    });
  }

  async downloadC2MessageGenerations(ids: string[]): Promise<ApiResponse<Blob>> {
    return this.requestBlob(`/api/v1/c2-message-generation/download`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(ids),
    });
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export class for testing
export { ApiClient };
