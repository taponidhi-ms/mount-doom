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
  orchestrator_agent_details: AgentDetails;
  conversation_id: string;
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
    prompt: string
  ): Promise<ApiResponse<PromptValidatorResponse>> {
    return this.request<PromptValidatorResponse>('/api/v1/prompt-validator/validate', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
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
