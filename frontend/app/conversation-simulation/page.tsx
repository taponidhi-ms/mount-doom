'use client'

import { useState } from 'react'
import { Button, Card, Input, Tabs, Table, Space, Typography, message, Alert, Collapse, Tag } from 'antd'
import PageLayout from '@/components/PageLayout'
import { apiClient, ConversationSimulationResponse, BrowseResponse, ConversationMessage } from '@/lib/api-client'

const { TextArea } = Input
const { Paragraph, Text, Title } = Typography
const { Panel } = Collapse

export default function ConversationSimulationPage() {
  const [customerIntent, setCustomerIntent] = useState('')
  const [customerSentiment, setCustomerSentiment] = useState('')
  const [conversationSubject, setConversationSubject] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ConversationSimulationResponse | null>(null)
  const [error, setError] = useState('')
  
  // History state
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyData, setHistoryData] = useState<BrowseResponse | null>(null)
  const [historyError, setHistoryError] = useState('')

  const loadHistory = async (page: number = 1, pageSize: number = 10) => {
    setHistoryLoading(true)
    setHistoryError('')
    const response = await apiClient.browseConversationSimulations(page, pageSize)
    setHistoryLoading(false)
    
    if (response.data) {
      setHistoryData(response.data)
    } else if (response.error) {
      setHistoryError(response.error)
      message.error('Failed to load history')
    }
  }

  const handleSubmit = async () => {
    if (!customerIntent.trim() || !customerSentiment.trim() || !conversationSubject.trim()) {
      message.warning('Please fill in all fields')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    const response = await apiClient.simulateConversation(
      customerIntent,
      customerSentiment,
      conversationSubject
    )
    setLoading(false)

    if (response.data) {
      setResult(response.data)
      message.success('Conversation simulated successfully!')
      if (historyData) {
        loadHistory(1)
      }
    } else if (response.error) {
      setError(response.error)
      message.error('Failed to simulate conversation')
    }
  }

  const renderConversationHistory = (history: ConversationMessage[]) => {
    return (
      <Space direction="vertical" size="small" style={{ width: '100%' }}>
        {history.map((msg, index) => (
          <Card 
            key={index} 
            size="small"
            style={{ 
              background: msg.agent_name === 'C1Agent' ? '#e6f7ff' : '#f6ffed',
            }}
          >
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <div>
                <Tag color={msg.agent_name === 'C1Agent' ? 'blue' : 'green'}>
                  {msg.agent_name === 'C1Agent' ? 'Service Rep' : 'Customer'}
                </Tag>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </Text>
              </div>
              <Text>{msg.message}</Text>
              {msg.tokens_used && (
                <Text type="secondary" style={{ fontSize: 12 }}>
                  Tokens: {msg.tokens_used}
                </Text>
              )}
            </Space>
          </Card>
        ))}
      </Space>
    )
  }

  const columns = [
    {
      title: 'Timestamp',
      dataIndex: 'start_time',
      key: 'timestamp',
      render: (text: string) => new Date(text).toLocaleString(),
      width: 180,
    },
    {
      title: 'Intent',
      dataIndex: 'conversation_properties',
      key: 'intent',
      width: 150,
      ellipsis: true,
      render: (props: any) => props?.CustomerIntent || 'N/A',
    },
    {
      title: 'Sentiment',
      dataIndex: 'conversation_properties',
      key: 'sentiment',
      width: 120,
      render: (props: any) => props?.CustomerSentiment || 'N/A',
    },
    {
      title: 'Subject',
      dataIndex: 'conversation_properties',
      key: 'subject',
      ellipsis: true,
      render: (props: any) => props?.ConversationSubject || 'N/A',
    },
    {
      title: 'Status',
      dataIndex: 'conversation_status',
      key: 'status',
      width: 120,
      render: (status: string) => (
        <Tag color={status === 'Completed' ? 'green' : 'orange'}>
          {status}
        </Tag>
      ),
    },
    {
      title: 'Messages',
      dataIndex: 'conversation_history',
      key: 'messages',
      width: 100,
      render: (history: any[]) => history?.length || 0,
    },
    {
      title: 'Tokens',
      dataIndex: 'total_tokens_used',
      key: 'tokens',
      width: 100,
      render: (value: number) => value || 'N/A',
    },
  ]

  const tabItems = [
    {
      key: 'simulate',
      label: 'Simulate',
      children: (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Card title="Conversation Configuration">
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <Text strong>Customer Intent</Text>
                <Input
                  value={customerIntent}
                  onChange={(e) => setCustomerIntent(e.target.value)}
                  placeholder="e.g., Technical Support, Billing Inquiry, Product Return"
                  style={{ marginTop: 8 }}
                  disabled={loading}
                  size="large"
                />
              </div>

              <div>
                <Text strong>Customer Sentiment</Text>
                <Input
                  value={customerSentiment}
                  onChange={(e) => setCustomerSentiment(e.target.value)}
                  placeholder="e.g., Frustrated, Happy, Confused, Angry"
                  style={{ marginTop: 8 }}
                  disabled={loading}
                  size="large"
                />
              </div>

              <div>
                <Text strong>Conversation Subject</Text>
                <Input
                  value={conversationSubject}
                  onChange={(e) => setConversationSubject(e.target.value)}
                  placeholder="e.g., Product Defect, Service Cancellation, Account Issue"
                  style={{ marginTop: 8 }}
                  disabled={loading}
                  size="large"
                />
              </div>
              
              <Alert 
                message="Note" 
                description="Conversations will run up to 20 turns or until completion is detected by the orchestrator agent."
                type="info" 
                showIcon 
              />

              <Button 
                type="primary" 
                size="large"
                onClick={handleSubmit}
                loading={loading}
                disabled={!customerIntent.trim() || !customerSentiment.trim() || !conversationSubject.trim()}
                block
              >
                {loading ? 'Simulating...' : 'Start Simulation'}
              </Button>

              {error && (
                <Alert message="Error" description={error} type="error" showIcon />
              )}
            </Space>
          </Card>

          {result && (
            <Card title="Simulation Results">
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <Space size="large" wrap>
                  <div>
                    <Text type="secondary">Status: </Text>
                    <Tag color={result.conversation_status === 'Completed' ? 'green' : 'orange'}>
                      {result.conversation_status}
                    </Tag>
                  </div>
                  <div>
                    <Text type="secondary">Total Messages: </Text>
                    <Text strong>{result.conversation_history.length}</Text>
                  </div>
                  <div>
                    <Text type="secondary">Total Tokens: </Text>
                    <Text strong>{result.total_tokens_used || 'N/A'}</Text>
                  </div>
                  <div>
                    <Text type="secondary">Time Taken: </Text>
                    <Text strong>{Math.round(result.total_time_taken_ms)} ms</Text>
                  </div>
                </Space>

                <div>
                  <Text strong style={{ fontSize: 16 }}>Conversation History</Text>
                  <div style={{ marginTop: 16 }}>
                    {renderConversationHistory(result.conversation_history)}
                  </div>
                </div>
              </Space>
            </Card>
          )}
        </Space>
      ),
    },
    {
      key: 'history',
      label: 'History',
      children: (
        <Card title="Simulation History">
          {historyError && (
            <Alert message="Error" description={historyError} type="error" showIcon style={{ marginBottom: 16 }} />
          )}
          
          <Table
            dataSource={historyData?.items || []}
            columns={columns}
            loading={historyLoading}
            rowKey={(record) => record.id || record.start_time}
            pagination={{
              current: historyData?.page || 1,
              pageSize: historyData?.page_size || 10,
              total: historyData?.total_count || 0,
              showSizeChanger: true,
              showTotal: (total) => `Total ${total} items`,
              onChange: (page, pageSize) => loadHistory(page, pageSize),
            }}
            expandable={{
              expandedRowRender: (record) => (
                <div style={{ padding: 16 }}>
                  {record.conversation_history && renderConversationHistory(record.conversation_history)}
                </div>
              ),
            }}
          />
        </Card>
      ),
    },
  ]

  return (
    <PageLayout
      title="Conversation Simulation"
      description="Simulate multi-turn conversations between customer service representatives and customers."
      showBackButton
    >
      <Tabs 
        defaultActiveKey="simulate" 
        items={tabItems}
        onChange={(key) => {
          if (key === 'history' && !historyData) {
            loadHistory(1)
          }
        }}
      />
    </PageLayout>
  )
}
