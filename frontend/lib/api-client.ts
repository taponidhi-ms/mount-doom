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

// Persona Generation
export interface PersonaGenerationRequest {
  prompt: string;
  model?: string;
  stream?: boolean;
}

export interface PersonaGenerationResponse extends BaseResponse {}

// General Prompt
export interface GeneralPromptRequest {
  prompt: string;
  stream?: boolean;
}

export interface GeneralPromptResponse {
  response_text: string;
  tokens_used?: number;
  time_taken_ms: number;
  start_time: string;
  end_time: string;
  model_deployment_name: string;
}

// Prompt Validator
export interface PromptValidatorRequest {
  prompt: string;
  model?: string;
  stream?: boolean;
}

export interface PromptValidatorResponse extends BaseResponse {}

// Conversation Simulation
export interface ConversationProperties {
  CustomerIntent: string;
  CustomerSentiment: string;
  ConversationSubject: string;
}

export interface ConversationMessage {
  agent_name: string;
  message: string;
  tokens_used?: number;
  timestamp: string;
}

export interface ConversationSimulationRequest {
  conversation_properties: ConversationProperties;
  conversation_prompt?: string;
  max_turns?: number;
  stream?: boolean;
}

export interface ConversationSimulationResponse {
  conversation_history: ConversationMessage[];
  conversation_status: string;
  total_tokens_used?: number;
  total_time_taken_ms: number;
  start_time: string;
  end_time: string;
  c1_agent_details: AgentDetails;
  c2_agent_details: AgentDetails;
  orchestrator_agent_details: AgentDetails;
}

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

  // Models API
  async getModels(): Promise<ApiResponse<AvailableModelsResponse>> {
    return this.request<AvailableModelsResponse>('/api/v1/models');
  }

  // Persona Generation APIs
  async generatePersona(
    prompt: string,
    model: string = 'gpt-4'
  ): Promise<ApiResponse<PersonaGenerationResponse>> {
    return this.request<PersonaGenerationResponse>('/api/v1/persona-generation/generate', {
      method: 'POST',
      body: JSON.stringify({ prompt, model }),
    });
  }

  async browsePersonaGenerations(
    page: number = 1,
    pageSize: number = 10,
    orderBy: string = 'timestamp',
    orderDirection: 'ASC' | 'DESC' = 'DESC'
  ): Promise<ApiResponse<BrowseResponse>> {
    return this.request<BrowseResponse>(
      `/api/v1/persona-generation/browse?page=${page}&page_size=${pageSize}&order_by=${orderBy}&order_direction=${orderDirection}`
    );
  }

  // General Prompt APIs
  async generateGeneralResponse(
    prompt: string
  ): Promise<ApiResponse<GeneralPromptResponse>> {
    return this.request<GeneralPromptResponse>('/api/v1/general-prompt/generate', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    });
  }

  async browseGeneralPrompts(
    page: number = 1,
    pageSize: number = 10,
    orderBy: string = 'timestamp',
    orderDirection: 'ASC' | 'DESC' = 'DESC'
  ): Promise<ApiResponse<BrowseResponse>> {
    return this.request<BrowseResponse>(
      `/api/v1/general-prompt/browse?page=${page}&page_size=${pageSize}&order_by=${orderBy}&order_direction=${orderDirection}`
    );
  }

  // Prompt Validator APIs
  async validatePrompt(
    prompt: string,
    model: string = 'gpt-4'
  ): Promise<ApiResponse<PromptValidatorResponse>> {
    return this.request<PromptValidatorResponse>('/api/v1/prompt-validator/validate', {
      method: 'POST',
      body: JSON.stringify({ prompt, model }),
    });
  }

  async browsePromptValidations(
    page: number = 1,
    pageSize: number = 10,
    orderBy: string = 'timestamp',
    orderDirection: 'ASC' | 'DESC' = 'DESC'
  ): Promise<ApiResponse<BrowseResponse>> {
    return this.request<BrowseResponse>(
      `/api/v1/prompt-validator/browse?page=${page}&page_size=${pageSize}&order_by=${orderBy}&order_direction=${orderDirection}`
    );
  }

  // Conversation Simulation APIs
  async simulateConversation(
    conversationProperties: ConversationProperties,
    conversationPrompt: string = '',
    maxTurns: number = 10
  ): Promise<ApiResponse<ConversationSimulationResponse>> {
    return this.request<ConversationSimulationResponse>('/api/v1/conversation-simulation/simulate', {
      method: 'POST',
      body: JSON.stringify({
        conversation_properties: conversationProperties,
        conversation_prompt: conversationPrompt,
        max_turns: maxTurns,
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
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export class for testing
export { ApiClient };
