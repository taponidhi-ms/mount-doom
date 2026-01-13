'use client'

import { useState } from 'react'
import { Button, Card, Input, Tabs, Table, Space, Typography, message, Alert } from 'antd'
import { ReloadOutlined } from '@ant-design/icons'
import PageLayout from '@/components/PageLayout'
import { apiClient, PromptValidatorResponse, BrowseResponse } from '@/lib/api-client'

const { TextArea } = Input
const { Paragraph, Text } = Typography

export default function PromptValidatorPage() {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<PromptValidatorResponse | null>(null)
  const [error, setError] = useState('')
  
  // History state
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyData, setHistoryData] = useState<BrowseResponse | null>(null)
  const [historyError, setHistoryError] = useState('')
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
  const [deleteLoading, setDeleteLoading] = useState(false)

  const loadHistory = async (page: number = 1, pageSize: number = 10) => {
    setHistoryLoading(true)
    setHistoryError('')
    const response = await apiClient.browsePromptValidations(page, pageSize)
    setHistoryLoading(false)
    
    if (response.data) {
      setHistoryData(response.data)
      setSelectedRowKeys([])
    } else if (response.error) {
      setHistoryError(response.error)
      message.error('Failed to load history')
    }
  }

  const handleDeleteSelected = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('Please select items to delete')
      return
    }

    const confirmDelete = window.confirm(
      `Are you sure you want to delete ${selectedRowKeys.length} item(s)? This action cannot be undone.`
    )
    
    if (!confirmDelete) return

    setDeleteLoading(true)
    const ids = selectedRowKeys.map(key => String(key))
    
    const response = await apiClient.deletePromptValidations(ids)
    setDeleteLoading(false)

    if (response.data) {
      const { deleted_count, failed_count } = response.data
      message.success(`Deleted ${deleted_count} item(s)`)
      if (failed_count > 0) {
        message.warning(`Failed to delete ${failed_count} item(s)`)
      }
      setSelectedRowKeys([])
      loadHistory(1)
    } else if (response.error) {
      message.error(response.error)
    }
  }

  const samplePrompts = [
    "Generate a conversation between a customer and a support agent.",
    "Simulate a call where the customer is angry about a billing error and threatens to cancel service.",
    "Create a roleplay scenario for a sales training exercise involving a hesitant buyer."
  ]

  const handleSubmit = async () => {
    if (!prompt.trim()) {
      message.warning('Please enter a prompt to validate')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    const response = await apiClient.validatePrompt(prompt)
    setLoading(false)

    if (response.data) {
      setResult(response.data)
      message.success('Prompt validated successfully!')
      if (historyData) {
        loadHistory(1)
      }
    } else if (response.error) {
      setError(response.error)
      message.error('Failed to validate prompt')
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
      title: 'Validation Preview',
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
      key: 'validate',
      label: 'Validate',
      children: (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Card title="Validate Prompt">
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <Text strong>Simulation Prompt</Text>
                <TextArea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Enter your simulation prompt to validate..."
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
                {loading ? 'Validating...' : 'Validate Prompt'}
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
                <Alert message="Error" description={error} type="error" showIcon />
              )}
            </Space>
          </Card>

          {result && (
            <Card title="Validation Result">
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <div>
                  <Text strong>Feedback:</Text>
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
        <Card 
          title="History"
          extra={
            <Space>
              {selectedRowKeys.length > 0 && (
                <Button 
                  danger 
                  onClick={handleDeleteSelected}
                  loading={deleteLoading}
                >
                  Delete Selected ({selectedRowKeys.length})
                </Button>
              )}
              <Button 
                icon={<ReloadOutlined />} 
                onClick={() => loadHistory(historyData?.page || 1, historyData?.page_size || 10)}
                loading={historyLoading}
              >
                Reload
              </Button>
            </Space>
          }
        >
          {historyError && (
            <Alert message="Error" description={historyError} type="error" showIcon style={{ marginBottom: 16 }} />
          )}
          
          <Table
            dataSource={historyData?.items || []}
            columns={columns}
            loading={historyLoading}
            rowKey="id"
            rowSelection={{
              selectedRowKeys,
              onChange: (keys) => setSelectedRowKeys(keys),
            }}
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
                      <Text strong>Validation Result:</Text>
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
      title="Prompt Validator"
      description="Validate simulation prompts to ensure they meet quality standards."
      showBackButton
    >
      <Tabs 
        defaultActiveKey="validate" 
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
