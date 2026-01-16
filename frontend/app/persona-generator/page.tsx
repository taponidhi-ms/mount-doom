'use client'

import PageLayout from '@/components/PageLayout'
import SingleAgentTemplate from '@/components/SingleAgentTemplate'
import { apiClient } from '@/lib/api-client'
import type { SingleAgentConfig } from '@/lib/types'

const config: SingleAgentConfig = {
  title: 'Persona Generator',
  description: 'Generate exact customer personas with specific intents, sentiments, subjects, and metadata. Outputs a list of detailed personas for conversation simulations.',
  pageKey: 'persona-generator',
  
  inputLabel: 'Prompt',
  inputPlaceholder: 'Enter your prompt to generate personas...',
  inputFieldName: 'prompt',
  
  sampleInputs: [
    {
      label: 'Technical support personas with varied sentiments',
      value: 'Generate 5 personas for technical support with varied sentiments (Frustrated, Confused, Angry) regarding internet connectivity issues.',
    },
    {
      label: 'Travel agency personas',
      value: 'I need 3 personas for a travel agency. One planning a honeymoon (Happy), one cancelling a trip due to illness (Sad), and one inquiring about visa requirements (Neutral).',
    },
    {
      label: 'E-commerce return personas with metadata',
      value: "Create 4 personas for an e-commerce return process. Include metadata like 'OrderValue', 'CustomerLoyaltyTier', and 'ReturnReason'.",
    },
  ],
  
  generateFn: async (input: string) => {
    const response = await apiClient.generatePersonas(input)
    if (response.data) {
      return {
        data: {
          response_text: response.data.response_text,
          tokens_used: response.data.tokens_used,
          time_taken_ms: response.data.time_taken_ms,
          start_time: response.data.start_time,
          end_time: response.data.end_time,
          agent_details: response.data.agent_details,
          parsed_output: response.data.parsed_output,
        },
      }
    }
    return { error: response.error }
  },
  
  browseFn: async (page, pageSize, orderBy, orderDirection) => {
    return apiClient.browsePersonaGenerations(page, pageSize, orderBy, orderDirection)
  },
  
  deleteFn: async (ids) => {
    return apiClient.deletePersonaGenerations(ids)
  },
  
  downloadFn: async (ids) => {
    // Use persona distributions download as fallback since we don't have dedicated one
    return apiClient.downloadPersonaDistributions(ids)
  },
}

export default function PersonaGeneratorPage() {
  return (
    <PageLayout 
      title={config.title}
      description={config.description}
    >
      <SingleAgentTemplate config={config} />
    </PageLayout>
  )
}
