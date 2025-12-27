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
  model: string;
  timestamp: string;
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
  model_id: string;
  model_name: string;
  description?: string;
}

export interface AvailableModelsResponse {
  models: ModelInfo[];
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
  model_id: string;
  prompt: string;
  stream?: boolean;
}

export interface GeneralPromptResponse {
  response_text: string;
  tokens_used?: number;
  time_taken_ms: number;
  start_time: string;
  end_time: string;
  model_id: string;
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
  role: string;
  agent_name: string;
  agent_version?: string;
  message: string;
  tokens_used?: number;
  time_taken_ms: number;
  timestamp: string;
}

export interface ConversationSimulationRequest {
  conversation_properties: ConversationProperties;
  model?: string;
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

// Backward compatibility types (to be deprecated)
export interface AgentInfo {
  agent_id: string;
  agent_name: string;
  description?: string;
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

  // Persona Generation APIs
  async getPersonaModels(): Promise<ApiResponse<AvailableModelsResponse>> {
    return this.request<AvailableModelsResponse>('/persona-generation/models');
  }

  async generatePersona(
    prompt: string,
    model: string = 'gpt-4'
  ): Promise<ApiResponse<PersonaGenerationResponse>> {
    return this.request<PersonaGenerationResponse>('/persona-generation/generate', {
      method: 'POST',
      body: JSON.stringify({ prompt, model }),
    });
  }

  // General Prompt APIs
  async getGeneralModels(): Promise<ApiResponse<AvailableModelsResponse>> {
    return this.request<AvailableModelsResponse>('/general-prompt/models');
  }

  async generateGeneralResponse(
    modelId: string,
    prompt: string
  ): Promise<ApiResponse<GeneralPromptResponse>> {
    return this.request<GeneralPromptResponse>('/general-prompt/generate', {
      method: 'POST',
      body: JSON.stringify({ model_id: modelId, prompt }),
    });
  }

  // Prompt Validator APIs
  async getPromptValidatorModels(): Promise<ApiResponse<AvailableModelsResponse>> {
    return this.request<AvailableModelsResponse>('/prompt-validator/models');
  }

  async validatePrompt(
    prompt: string,
    model: string = 'gpt-4'
  ): Promise<ApiResponse<PromptValidatorResponse>> {
    return this.request<PromptValidatorResponse>('/prompt-validator/validate', {
      method: 'POST',
      body: JSON.stringify({ prompt, model }),
    });
  }

  // Conversation Simulation APIs
  async getConversationModels(): Promise<ApiResponse<AvailableModelsResponse>> {
    return this.request<AvailableModelsResponse>('/conversation-simulation/models');
  }

  async simulateConversation(
    conversationProperties: ConversationProperties,
    model: string = 'gpt-4',
    maxTurns: number = 10
  ): Promise<ApiResponse<ConversationSimulationResponse>> {
    return this.request<ConversationSimulationResponse>('/conversation-simulation/simulate', {
      method: 'POST',
      body: JSON.stringify({
        conversation_properties: conversationProperties,
        model,
        max_turns: maxTurns,
      }),
    });
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export class for testing
export { ApiClient };
