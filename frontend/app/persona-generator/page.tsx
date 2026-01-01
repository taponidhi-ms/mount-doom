'use client'

import { useState } from 'react'
import { Button, Card, Input, Tabs, Table, Space, Typography, message, Spin, Alert } from 'antd'
import { LoadingOutlined, ReloadOutlined } from '@ant-design/icons'
import PageLayout from '@/components/PageLayout'
import { apiClient, PersonaGeneratorResponse, BrowseResponse } from '@/lib/api-client'

const { TextArea } = Input
const { Title, Paragraph, Text } = Typography

export default function PersonaGeneratorPage() {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<PersonaGeneratorResponse | null>(null)
  const [error, setError] = useState('')
  
  // History state
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyData, setHistoryData] = useState<BrowseResponse | null>(null)
  const [historyError, setHistoryError] = useState('')

  const loadHistory = async (page: number = 1, pageSize: number = 10) => {
    setHistoryLoading(true)
    setHistoryError('')
    const response = await apiClient.browsePersonaGenerations(page, pageSize)
    setHistoryLoading(false)
    
    if (response.data) {
      setHistoryData(response.data)
    } else if (response.error) {
      setHistoryError(response.error)
      message.error('Failed to load history')
    }
  }

  const samplePrompts = [
    "Generate 5 personas for technical support with varied sentiments (Frustrated, Confused, Angry) regarding internet connectivity issues.",
    "I need 3 personas for a travel agency. One planning a honeymoon (Happy), one cancelling a trip due to illness (Sad), and one inquiring about visa requirements (Neutral).",
    "Create 4 personas for an e-commerce return process. Include metadata like 'OrderValue', 'CustomerLoyaltyTier', and 'ReturnReason'."
  ]

  const handleSubmit = async () => {
    if (!prompt.trim()) {
      message.warning('Please enter a prompt')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    const response = await apiClient.generatePersonas(prompt)
    setLoading(false)

    if (response.data) {
      setResult(response.data)
      message.success('Personas generated successfully!')
      // Reload history to show the new result
      if (historyData) {
        loadHistory(1)
      }
    } else if (response.error) {
      setError(response.error)
      message.error('Failed to generate personas')
    }
  }

  const columns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (text: string) => new Date(text).toLocaleString(),
      width: 200,
    },
    {
      title: 'Prompt',
      dataIndex: 'prompt',
      key: 'prompt',
      ellipsis: true,
      render: (text: string) => text || 'N/A',
    },
    {
      title: 'Response Preview',
      dataIndex: 'response',
      key: 'response',
      ellipsis: true,
      render: (text: string) => text?.substring(0, 100) + (text?.length > 100 ? '...' : ''),
    },
    {
      title: 'Tokens',
      dataIndex: 'tokens_used',
      key: 'tokens',
      width: 100,
      render: (value: number) => value || 'N/A',
    },
    {
      title: 'Time (ms)',
      dataIndex: 'time_taken_ms',
      key: 'time',
      width: 120,
      render: (value: number) => value ? Math.round(value) : 'N/A',
    },
  ]

  const items = [
    {
      key: 'generate',
      label: 'Generate',
      children: (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Card title="Generate Personas" bordered={false}>
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <Text strong>Prompt</Text>
                <Paragraph type="secondary" style={{ marginBottom: 8 }}>
                  Describe what personas you want to generate (e.g., "Generate 5 personas for technical support with varied sentiments")
                </Paragraph>
                <TextArea
                  rows={6}
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Enter your prompt to generate personas..."
                  disabled={loading}
                />
              </div>

              <Button
                type="primary"
                size="large"
                onClick={handleSubmit}
                loading={loading}
                disabled={!prompt.trim()}
              >
                {loading ? 'Generating...' : 'Generate Personas'}
              </Button>

              <div style={{ marginTop: 16 }}>
                <Text strong>Sample Prompts</Text>
                <Space direction="vertical" style={{ width: '100%', marginTop: 8 }}>
                  {samplePrompts.map((sample, index) => (
                    <Card key={index} size="small" style={{ background: '#f9f9f9' }}>
                      <Space align="start" style={{ width: '100%', justifyContent: 'space-between' }}>
                        <Text style={{ fontSize: 13, color: '#666' }}>{sample}</Text>
                        <Button 
                          size="small" 
                          type="link" 
                          onClick={() => setPrompt(sample)}
                          style={{ padding: 0, marginLeft: 8 }}
                        >
                          Try it
                        </Button>
                      </Space>
                    </Card>
                  ))}
                </Space>
              </div>

              {error && (
                <Alert
                  message="Error"
                  description={error}
                  type="error"
                  showIcon
                  closable
                  onClose={() => setError('')}
                />
              )}
            </Space>
          </Card>

          {result && (
            <Card title="Generated Personas" bordered={false}>
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <div>
                  <Text strong>Response:</Text>
                  <Paragraph>
                    <pre style={{ 
                      background: '#f5f5f5', 
                      padding: '12px', 
                      borderRadius: '4px',
                      whiteSpace: 'pre-wrap',
                      wordWrap: 'break-word'
                    }}>
                      {result.response_text}
                    </pre>
                  </Paragraph>
                </div>

                {result.parsed_output && (
                  <div>
                    <Text strong>Parsed Output:</Text>
                    <Paragraph>
                      <pre style={{ 
                        background: '#e6f7ff', 
                        padding: '12px', 
                        borderRadius: '4px',
                        whiteSpace: 'pre-wrap',
                        wordWrap: 'break-word'
                      }}>
                        {JSON.stringify(result.parsed_output, null, 2)}
                      </pre>
                    </Paragraph>
                  </div>
                )}

                <div>
                  <Space size="large">
                    {result.tokens_used && (
                      <Text type="secondary">Tokens Used: {result.tokens_used}</Text>
                    )}
                    {result.time_taken_ms && (
                      <Text type="secondary">
                        Time Taken: {Math.round(result.time_taken_ms)}ms
                      </Text>
                    )}
                  </Space>
                </div>

                <div>
                  <Text strong>Agent Details:</Text>
                  <Paragraph>
                    <Space direction="vertical">
                      <Text>Agent: {result.agent_details.agent_name}</Text>
                      <Text>Version: {result.agent_details.agent_version}</Text>
                      <Text>Model: {result.agent_details.model_deployment_name}</Text>
                    </Space>
                  </Paragraph>
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
        <Card 
          title="Generation History" 
          bordered={false}
          extra={
            <Button 
              icon={<ReloadOutlined />} 
              onClick={() => loadHistory(historyData?.page || 1, historyData?.page_size || 10)}
              loading={historyLoading}
            >
              Reload
            </Button>
          }
        >
          {historyError && (
            <Alert
              message="Error"
              description={historyError}
              type="error"
              showIcon
              style={{ marginBottom: 16 }}
            />
          )}

          <Table
            columns={columns}
            dataSource={historyData?.items || []}
            rowKey="id"
            loading={historyLoading}
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
                <div>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div>
                      <Text strong>Prompt:</Text>
                      <Paragraph>{record.prompt}</Paragraph>
                    </div>
                    <div>
                      <Text strong>Response:</Text>
                      <Paragraph>
                        <pre style={{ 
                          background: '#f5f5f5', 
                          padding: '12px', 
                          borderRadius: '4px',
                          whiteSpace: 'pre-wrap',
                          wordWrap: 'break-word'
                        }}>
                          {record.response}
                        </pre>
                      </Paragraph>
                    </div>
                    {record.parsed_output && (
                      <div>
                        <Text strong>Parsed Output:</Text>
                        <Paragraph>
                          <pre style={{ 
                            background: '#e6f7ff', 
                            padding: '12px', 
                            borderRadius: '4px',
                            whiteSpace: 'pre-wrap',
                            wordWrap: 'break-word'
                          }}>
                            {JSON.stringify(record.parsed_output, null, 2)}
                          </pre>
                        </Paragraph>
                      </div>
                    )}
                  </Space>
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
      title="Persona Generator"
      description="Generate exact customer personas for conversation simulations"
      showBackButton
    >
      <Tabs defaultActiveKey="generate" items={items} />
    </PageLayout>
  )
}
