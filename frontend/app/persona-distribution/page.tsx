'use client'

import PageLayout from '@/components/PageLayout'
import SingleAgentTemplate from '@/components/SingleAgentTemplate'
import { apiClient } from '@/lib/api-client'
import type { SingleAgentConfig } from '@/lib/types'

const config: SingleAgentConfig = {
  title: 'Persona Distribution',
  description: 'Generate persona distributions from simulation prompts using specialized AI agents. Outputs structured JSON with conversation counts, intents, sentiments, and proportions.',
  pageKey: 'persona-distribution',
  
  inputLabel: 'Prompt',
  inputPlaceholder: 'Enter your simulation prompt to generate a persona distribution...',
  inputFieldName: 'prompt',
  
  sampleInputs: [
    {
      label: 'Telecom billing and technical support mix',
      value: 'Generate a distribution of 100 calls for a telecom company where 60% are billing inquiries (mostly negative sentiment), 30% are technical support (mixed sentiment), and 10% are new service requests (positive sentiment).',
    },
    {
      label: 'Retail bank customer service',
      value: "Create a persona distribution for a retail bank's customer service. I need 50 conversations about credit card disputes, 30 about loan applications, and 20 about account balance checks.",
    },
    {
      label: 'Healthcare appointment scheduling',
      value: "Simulate a healthcare provider's appointment line. 40% scheduling new appointments, 40% rescheduling existing ones, and 20% cancelling. Most callers should be anxious or neutral.",
    },
  ],
  
  generateFn: async (input: string) => {
    const response = await apiClient.generatePersonaDistribution(input)
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
    return apiClient.browsePersonaDistributions(page, pageSize, orderBy, orderDirection)
  },
  
  deleteFn: async (ids) => {
    return apiClient.deletePersonaDistributions(ids)
  },
  
  downloadFn: async (ids) => {
    return apiClient.downloadPersonaDistributions(ids)
  },
}

export default function PersonaDistributionPage() {
  return (
    <PageLayout 
      title={config.title}
      description={config.description}
    >
      <SingleAgentTemplate config={config} />
    </PageLayout>
  )
}
