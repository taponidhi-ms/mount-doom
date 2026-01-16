'use client'

import { Tag, Space, Typography } from 'antd'
import PageLayout from '@/components/PageLayout'
import SingleAgentTemplate from '@/components/SingleAgentTemplate'
import { apiClient } from '@/lib/api-client'
import type { SingleAgentConfig } from '@/lib/types'

const { Text } = Typography

const config: SingleAgentConfig = {
  title: 'Transcript Parser',
  description: 'Parse customer-representative transcripts to extract intent, subject, and sentiment. Analyzes conversations and extracts key metadata.',
  pageKey: 'transcript-parser',
  
  inputLabel: 'Transcript',
  inputPlaceholder: 'Paste or type the transcript here...',
  inputFieldName: 'transcript',
  
  sampleInputs: [
    {
      label: 'Phone upgrade inquiry',
      value: "Customer: Hi, I've been trying to upgrade my phone plan but the website keeps giving me errors. Rep: I'm sorry about that. Let me look into this for you. When did you first encounter the error? Customer: This morning, around 10 AM. I really need this done today. Rep: I understand your urgency. I'm checking now... Ah, I found the issue. Let me process this manually for you.",
    },
    {
      label: 'Damaged product complaint',
      value: "Customer: I just received my order but the device is damaged. I'm really frustrated! Rep: I sincerely apologize for the inconvenience. Can you describe the damage? Customer: The screen has cracks and it won't turn on. This is unacceptable! Rep: You're absolutely right. I'll process a replacement immediately at no cost to you.",
    },
    {
      label: 'Account balance inquiry',
      value: "Customer: Could you help me understand how to access my account balance? Rep: Of course! I'd be happy to help. You can log in to your account... Customer: Okay, got it. Thank you for walking me through this. Rep: You're welcome! Is there anything else I can assist with? Customer: No, that's all. Have a good day! Rep: You too!",
    },
  ],
  
  generateFn: async (input: string) => {
    const response = await apiClient.parseTranscript(input)
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
    return apiClient.browseTranscripts(page, pageSize, orderBy, orderDirection)
  },
  
  deleteFn: async (ids) => {
    return apiClient.deleteTranscripts(ids)
  },
  
  downloadFn: async (ids) => {
    // Use persona distributions download as fallback
    return apiClient.downloadPersonaDistributions(ids)
  },
  
  renderParsedOutput: (parsedOutput: Record<string, unknown>) => {
    const output = parsedOutput as { intent?: string; subject?: string; sentiment?: string }
    return (
      <Space direction="vertical" style={{ width: '100%', marginTop: 8 }}>
        <div>
          <Text strong>Intent:</Text>
          <Tag color="blue" style={{ marginLeft: 8 }}>{output.intent || '(empty)'}</Tag>
        </div>
        <div>
          <Text strong>Subject:</Text>
          <Tag color="green" style={{ marginLeft: 8 }}>{output.subject || '(empty)'}</Tag>
        </div>
        <div>
          <Text strong>Sentiment:</Text>
          <Tag color="orange" style={{ marginLeft: 8 }}>{output.sentiment || '(empty)'}</Tag>
        </div>
      </Space>
    )
  },
}

export default function TranscriptParserPage() {
  return (
    <PageLayout 
      title={config.title}
      description={config.description}
    >
      <SingleAgentTemplate config={config} />
    </PageLayout>
  )
}
