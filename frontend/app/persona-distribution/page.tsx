'use client'

import { useState } from 'react'
import { Button, Card, Input, Tabs, Table, Space, Typography, message, Spin, Alert } from 'antd'
import { LoadingOutlined } from '@ant-design/icons'
import PageLayout from '@/components/PageLayout'
import { apiClient, PersonaDistributionResponse, BrowseResponse } from '@/lib/api-client'

const { TextArea } = Input
const { Title, Paragraph, Text } = Typography

export default function PersonaDistributionPage() {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<PersonaDistributionResponse | null>(null)
  const [error, setError] = useState('')
  
  // History state
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyData, setHistoryData] = useState<BrowseResponse | null>(null)
  const [historyError, setHistoryError] = useState('')

  const loadHistory = async (page: number = 1, pageSize: number = 10) => {
    setHistoryLoading(true)
    setHistoryError('')
    const response = await apiClient.browsePersonaDistributions(page, pageSize)
    setHistoryLoading(false)
    
    if (response.data) {
      setHistoryData(response.data)
    } else if (response.error) {
      setHistoryError(response.error)
      message.error('Failed to load history')
    }
  }

  const handleSubmit = async () => {
    if (!prompt.trim()) {
      message.warning('Please enter a prompt')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    const response = await apiClient.generatePersonaDistribution(prompt)
    setLoading(false)

    if (response.data) {
      setResult(response.data)
      message.success('Persona distribution generated successfully!')
      // Reload history to show the new result
      if (historyData) {
        loadHistory(1)
      }
    } else if (response.error) {
      setError(response.error)
      message.error('Failed to generate persona distribution')
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

  const tabItems = [
    {
      key: 'generate',
      label: 'Generate',
      children: (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Card title="Generate Persona Distribution">
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <Text strong>Simulation Prompt</Text>
                <TextArea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Enter your simulation prompt to generate a persona distribution..."
                  rows={6}
                  style={{ marginTop: 8 }}
                  disabled={loading}
                />
              </div>
              
              <Button 
                type="primary" 
                size="large"
                onClick={handleSubmit}
                loading={loading}
                disabled={!prompt.trim()}
                block
              >
                {loading ? 'Generating...' : 'Generate Persona Distribution'}
              </Button>

              {error && (
                <Alert message="Error" description={error} type="error" showIcon />
              )}
            </Space>
          </Card>

          {result && (
            <Card title="Generated Persona Distribution">
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <div>
                  <Text strong>Response:</Text>
                  <Paragraph style={{ 
                    whiteSpace: 'pre-wrap', 
                    background: '#f5f5f5', 
                    padding: 16, 
                    borderRadius: 8,
                    marginTop: 8 
                  }}>
                    {result.response_text}
                  </Paragraph>
                </div>

                <Space size="large" wrap>
                  <div>
                    <Text type="secondary">Tokens Used: </Text>
                    <Text strong>{result.tokens_used || 'N/A'}</Text>
                  </div>
                  <div>
                    <Text type="secondary">Time Taken: </Text>
                    <Text strong>{Math.round(result.time_taken_ms)} ms</Text>
                  </div>
                  <div>
                    <Text type="secondary">Model: </Text>
                    <Text strong>{result.agent_details.model_deployment_name}</Text>
                  </div>
                  <div>
                    <Text type="secondary">Agent: </Text>
                    <Text strong>{result.agent_details.agent_name}</Text>
                  </div>
                </Space>
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
        <Card title="Generation History">
          {historyError && (
            <Alert message="Error" description={historyError} type="error" showIcon style={{ marginBottom: 16 }} />
          )}
          
          <Table
            dataSource={historyData?.items || []}
            columns={columns}
            loading={historyLoading}
            rowKey={(record) => record.id || record.timestamp}
            pagination={{
              current: historyData?.page || 1,
              pageSize: historyData?.page_size || 10,
              total: historyData?.total_count || 0,
              showSizeChanger: true,
              showTotal: (total) => `Total ${total} items`,
              onChange: (page, pageSize) => loadHistory(page, pageSize),
            }}
          />
        </Card>
      ),
    },
  ]

  return (
    <PageLayout
      title="Persona Distribution Generator"
      description="Generate persona distributions from simulation prompts using the PersonaDistributionGeneratorAgent."
      showBackButton
    >
      <Tabs 
        defaultActiveKey="generate" 
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
