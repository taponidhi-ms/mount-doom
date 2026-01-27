'use client'

import { Tag, Space, Card, Typography } from 'antd'
import PageLayout from '@/components/PageLayout'
import MultiAgentTemplate from '@/components/MultiAgentTemplate'
import { apiClient } from '@/lib/api-client'
import type { MultiAgentConfig, ConversationMessage, MultiAgentHistoryItem, MultiAgentHistoryColumnConfig } from '@/lib/types'
import { useTimezone } from '@/lib/timezone-context'

const { Text } = Typography

// Custom history columns for conversation simulation
const getHistoryColumns = (formatTimestamp: (ts: string) => string): MultiAgentHistoryColumnConfig[] => [
  {
    title: 'Timestamp',
    dataIndex: 'timestamp',
    key: 'timestamp',
    render: (text: unknown) => formatTimestamp(text as string),
    width: 180,
  },
  {
    title: 'Conversation ID',
    dataIndex: 'conversation_id',
    key: 'conversation_id',
    width: 220,
    render: (_: unknown, record: MultiAgentHistoryItem) => {
      const convId = record.conversation_id || record.id
      return convId ? <Text copyable>{convId}</Text> : 'N/A'
    },
  },
  {
    title: 'Intent',
    dataIndex: 'conversation_properties',
    key: 'intent',
    width: 150,
    ellipsis: true,
    render: (props: unknown) => ((props as Record<string, unknown>)?.CustomerIntent as string) || 'N/A',
  },
  {
    title: 'Sentiment',
    dataIndex: 'conversation_properties',
    key: 'sentiment',
    width: 120,
    render: (props: unknown) => ((props as Record<string, unknown>)?.CustomerSentiment as string) || 'N/A',
  },
  {
    title: 'Subject',
    dataIndex: 'conversation_properties',
    key: 'subject',
    ellipsis: true,
    render: (props: unknown) => ((props as Record<string, unknown>)?.ConversationSubject as string) || 'N/A',
  },
  {
    title: 'Status',
    dataIndex: 'conversation_status',
    key: 'status',
    width: 120,
    render: (status: unknown) => (
      <Tag color={(status as string) === 'Completed' ? 'green' : 'orange'}>{status as string}</Tag>
    ),
  },
  {
    title: 'Messages',
    dataIndex: 'conversation_history',
    key: 'messages',
    width: 100,
    render: (history: unknown) => (history as ConversationMessage[])?.length || 0,
  },
  {
    title: 'Tokens',
    dataIndex: 'total_tokens_used',
    key: 'tokens',
    width: 100,
    render: (value: unknown) => (value as number) || 'N/A',
  },
]

function ConversationSimulationContent() {
  const { formatTimestamp, formatTime } = useTimezone()

  const config: MultiAgentConfig = {
    title: 'Conversation Simulation',
    description: 'Simulate multi-turn conversations between C1 (customer service representative) and C2 (customer) agents. Configure customer intent, sentiment, and subject to generate realistic conversation flows.',
    pageKey: 'conversation-simulation',
    
    inputFields: [
      {
        name: 'customerIntent',
        label: 'Customer Intent',
        placeholder: 'e.g., Technical Support, Billing Inquiry, Product Return',
        required: true,
      },
      {
        name: 'customerSentiment',
        label: 'Customer Sentiment',
        placeholder: 'e.g., Frustrated, Happy, Confused, Angry',
        required: true,
      },
      {
        name: 'conversationSubject',
        label: 'Conversation Subject',
        placeholder: 'e.g., Product Defect, Service Cancellation, Account Issue',
        required: true,
      },
    ],
    
    sampleConfigs: [
      {
        customerIntent: 'Technical Support',
        customerSentiment: 'Frustrated',
        conversationSubject: 'Internet connection keeps dropping every 10 minutes',
      },
      {
        customerIntent: 'Billing Inquiry',
        customerSentiment: 'Confused',
        conversationSubject: 'Unexpected charge of $50 on the monthly statement',
      },
      {
        customerIntent: 'Product Return',
        customerSentiment: 'Neutral',
        conversationSubject: 'Returning a pair of shoes that are the wrong size',
      },
    ],
    
    simulateFn: async (inputs) => {
      const response = await apiClient.simulateConversation(
        inputs.customerIntent,
        inputs.customerSentiment,
        inputs.conversationSubject
      )
      if (response.data) {
        return {
          data: {
            conversation_history: response.data.conversation_history,
            conversation_status: response.data.conversation_status,
            total_time_taken_ms: response.data.total_time_taken_ms,
            start_time: response.data.start_time,
            end_time: response.data.end_time,
            conversation_id: response.data.conversation_id,
            agent_details: response.data.agent_details,
          },
        }
      }
      return { error: response.error }
    },
    
    browseFn: async (page, pageSize, orderBy, orderDirection) => {
      return apiClient.browseConversationSimulations(page, pageSize, orderBy, orderDirection)
    },
    
    deleteFn: async (ids) => {
      return apiClient.deleteConversationSimulations(ids)
    },
    
    downloadFn: async (ids) => {
      return apiClient.downloadConversationSimulations(ids)
    },
    
    historyColumns: getHistoryColumns(formatTimestamp),
    
    renderConversation: (history: ConversationMessage[]) => {
      return (
        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          {history.map((msg, index) => {
            const isAgent = msg.role === 'agent'
            const isCustomer = msg.role === 'customer'

            let bgColor = '#ffffff'
            if (isAgent) bgColor = '#e6f7ff'
            else if (isCustomer) bgColor = '#f6ffed'

            let tagColor = 'default'
            let tagLabel = msg.role
            if (isAgent) {
              tagColor = 'blue'
              tagLabel = 'Agent'
            } else if (isCustomer) {
              tagColor = 'green'
              tagLabel = 'Customer'
            }

            return (
              <Card
                key={index}
                size="small"
                style={{
                  background: bgColor,
                }}
              >
                <Space direction="vertical" size="small" style={{ width: '100%' }}>
                  <div>
                    <Tag color={tagColor}>{tagLabel}</Tag>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {formatTime(msg.timestamp)}
                    </Text>
                    {msg.tokens_used && (
                      <Text type="secondary" style={{ fontSize: 12, marginLeft: 8 }}>
                        ({msg.tokens_used} tokens)
                      </Text>
                    )}
                  </div>
                  <Text style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</Text>
                </Space>
              </Card>
            )
          })}
        </Space>
      )
    },
  }

  return <MultiAgentTemplate config={config} />
}

export default function ConversationSimulationPage() {
  return (
    <PageLayout 
      title="Conversation Simulation"
      description="Simulate multi-turn conversations between C1 (customer service representative) and C2 (customer) agents."
    >
      <ConversationSimulationContent />
    </PageLayout>
  )
}
