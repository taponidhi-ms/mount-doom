'use client'

import PageLayout from '@/components/PageLayout'
import SingleAgentTemplate from '@/components/SingleAgentTemplate'
import { apiClient } from '@/lib/api-client'
import type { SingleAgentConfig } from '@/lib/types'

const config: SingleAgentConfig = {
  title: 'C2 Message Generation',
  description: 'Generate C2 (customer) messages using the C2 Message Generator Agent. Useful for testing and creating sample customer responses.',
  pageKey: 'c2-message-generation',
  
  inputLabel: 'Prompt',
  inputPlaceholder: 'Enter your prompt to generate a C2 (customer) message...',
  inputFieldName: 'prompt',
  
  sampleInputs: [
    {
      label: 'Frustrated customer with billing issue',
      value: 'Generate a customer message expressing frustration about an incorrect charge on their bill. The customer should be upset but not rude.',
    },
    {
      label: 'Happy customer with service inquiry',
      value: 'Generate a positive customer message asking about upgrading their service plan. The customer should be enthusiastic and curious.',
    },
    {
      label: 'Confused customer needing technical help',
      value: 'Generate a customer message from someone confused about how to set up their new device. They should be patient but clearly need step-by-step guidance.',
    },
  ],
  
  generateFn: async (input: string) => {
    const response = await apiClient.generateC2Message(input)
    if (response.data) {
      return {
        data: {
          response_text: response.data.response_text,
          tokens_used: response.data.tokens_used,
          time_taken_ms: response.data.time_taken_ms,
          start_time: response.data.start_time,
          end_time: response.data.end_time,
          agent_details: response.data.agent_details,
        },
      }
    }
    return { error: response.error }
  },
  
  browseFn: async (page, pageSize, orderBy, orderDirection) => {
    return apiClient.browseC2MessageGenerations(page, pageSize, orderBy, orderDirection)
  },
  
  deleteFn: async (ids) => {
    return apiClient.deleteC2MessageGenerations(ids)
  },
  
  downloadFn: async (ids) => {
    return apiClient.downloadC2MessageGenerations(ids)
  },
}

export default function C2MessageGenerationPage() {
  return (
    <PageLayout 
      title={config.title}
      description={config.description}
    >
      <SingleAgentTemplate config={config} />
    </PageLayout>
  )
}
