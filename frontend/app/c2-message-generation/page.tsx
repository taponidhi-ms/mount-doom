'use client'

import { useState } from 'react'
import { Button, Card, Input, Tabs, Table, Space, Typography, message, Alert, Progress, Select, Tag } from 'antd'
import { ReloadOutlined, DownloadOutlined } from '@ant-design/icons'
import PageLayout from '@/components/PageLayout'
import { apiClient, C2MessageGenerationResponse, BrowseResponse } from '@/lib/api-client'

const { TextArea } = Input
const { Paragraph, Text } = Typography

interface BatchItem {
  key: string;
  prompt: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: C2MessageGenerationResponse;
  error?: string;
}

export default function C2MessageGenerationPage() {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<C2MessageGenerationResponse | null>(null)
  const [error, setError] = useState('')
  
  // History state
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyData, setHistoryData] = useState<BrowseResponse | null>(null)
  const [historyError, setHistoryError] = useState('')
  const [selectedHistoryRowKeys, setSelectedHistoryRowKeys] = useState<React.Key[]>([])
  const [deleteLoading, setDeleteLoading] = useState(false)

  // Batch state
  const [batchItems, setBatchItems] = useState<BatchItem[]>([])
  const [batchLoading, setBatchLoading] = useState(false)
  const [batchProgress, setBatchProgress] = useState(0)
  const [currentBatchIndex, setCurrentBatchIndex] = useState(-1)
  const [batchJsonInput, setBatchJsonInput] = useState('')
  const [stopBatchRequested, setStopBatchRequested] = useState(false)
  const [batchDelay, setBatchDelay] = useState(5)

  const loadBatchItemsFromText = () => {
    if (!batchJsonInput.trim()) {
      message.warning('Paste prompts JSON to load batch items.')
      return
    }

    try {
      const json = JSON.parse(batchJsonInput)

      if (!Array.isArray(json)) {
        message.error('Invalid JSON format. Expected an array of objects with "prompt" field.')
        return
      }

      const items: BatchItem[] = json
        .map((item: unknown, index: number) => {
          if (typeof item !== 'object' || item === null || !('prompt' in item)) {
            return null
          }
          const promptText = (item as { prompt?: unknown }).prompt
          if (typeof promptText !== 'string') {
            return null
          }
          return {
            key: `batch-${index}-${Date.now()}`,
            prompt: promptText,
            status: 'pending' as const
          }
        })
        .filter((item: BatchItem | null) => item !== null && item.prompt.trim()) as BatchItem[]

      if (items.length === 0) {
        message.error('No valid objects with "prompt" field found in JSON.')
        return
      }

      setBatchItems(items)
      setBatchProgress(0)
      setCurrentBatchIndex(-1)
      message.success(`Loaded ${items.length} prompts.`)
    } catch (err) {
      message.error('Failed to parse JSON text. Expected format: [{ "prompt": "..." }, { "prompt": "..." }]')
      console.error(err)
    }
  }

  const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

  const runBatchGenerations = async () => {
    if (batchItems.length === 0) return
    
    setBatchLoading(true)
    setBatchProgress(0)
    setStopBatchRequested(false)
    
    const newItems = [...batchItems]
    
    for (let i = 0; i < newItems.length; i++) {
      // Check if stop was requested
      if (stopBatchRequested) {
        message.info('Batch processing stopped by user.')
        break
      }

      setCurrentBatchIndex(i)
      newItems[i].status = 'running'
      setBatchItems([...newItems])
      
      try {
        const response = await apiClient.generateC2Message(newItems[i].prompt)
        
        if (response.data) {
          newItems[i].status = 'completed'
          newItems[i].result = response.data
        } else {
          newItems[i].status = 'failed'
          newItems[i].error = response.error || 'Unknown error'
        }
      } catch {
        newItems[i].status = 'failed'
        newItems[i].error = 'Exception occurred'
      }
      
      setBatchItems([...newItems])
      setBatchProgress(Math.round(((i + 1) / newItems.length) * 100))
      
      // Add delay between generations (except after the last one)
      if (i < newItems.length - 1 && !stopBatchRequested) {
        await sleep(batchDelay * 1000)
      }
    }
    
    setBatchLoading(false)
    setCurrentBatchIndex(-1)
    setStopBatchRequested(false)
    message.success('Batch processing completed!')
    
    // Refresh history if we're on that tab or to keep it updated
    if (historyData) {
      loadHistory(1)
    }
  }

  const handleStopBatch = () => {
    setStopBatchRequested(true)
  }

  const loadHistory = async (page: number = 1, pageSize: number = 10) => {
    setHistoryLoading(true)
    setHistoryError('')
    const response = await apiClient.browseC2MessageGenerations(page, pageSize)
    setHistoryLoading(false)
    
    if (response.data) {
      setHistoryData(response.data)
      setSelectedHistoryRowKeys([])
    } else if (response.error) {
      setHistoryError(response.error)
      message.error('Failed to load history')
    }
  }

  const handleDeleteSelected = async () => {
    if (selectedHistoryRowKeys.length === 0) {
      message.warning('Please select items to delete')
      return
    }

    const confirmDelete = window.confirm(
      `Are you sure you want to delete ${selectedHistoryRowKeys.length} item(s)? This action cannot be undone.`
    )
    
    if (!confirmDelete) return

    setDeleteLoading(true)
    const ids = selectedHistoryRowKeys.map(key => String(key))
    
    const response = await apiClient.deleteC2MessageGenerations(ids)
    setDeleteLoading(false)

    if (response.data) {
      const { deleted_count, failed_count } = response.data
      message.success(`Deleted ${deleted_count} item(s)`)
      if (failed_count > 0) {
        message.warning(`Failed to delete ${failed_count} item(s)`)
      }
      setSelectedHistoryRowKeys([])
      loadHistory(1)
    } else if (response.error) {
      message.error(response.error)
    }
  }

  const handleDownloadConversations = async () => {
    if (selectedHistoryRowKeys.length === 0) {
      message.warning('Please select conversations to download')
      return
    }

    const ids = selectedHistoryRowKeys.map(key => String(key))
    const response = await apiClient.downloadC2MessageGenerations(ids)

    if (response.data) {
      const url = URL.createObjectURL(response.data)
      const link = document.createElement('a')
      link.href = url
      link.download = `c2_message_generations_${new Date().toISOString().replace(/[:.]/g, '-')}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      message.success('Download started')
    } else if (response.error) {
      message.error('Failed to download: ' + response.error)
    }
  }

  const samplePrompts = [
    'Ongoing transcript: {"Properties": {"CustomerIntent": "billing inquiry", "CustomerSentiment": "frustrated", "ConversationSubject": "Overcharge on bill"}, "messages": [{"customer": "Hello", "Id": 1}, {"agent": "Hi there, how can I help you today?", "Id": 2}]}',
    'Ongoing transcript: {"Properties": {"CustomerIntent": "technical support", "CustomerSentiment": "confused", "ConversationSubject": "Internet not working"}, "messages": [{"customer": "Hello", "Id": 1}, {"agent": "Hello! I understand you\'re having issues with your internet. Can you describe the problem?", "Id": 2}]}',
    'Ongoing transcript: {"Properties": {"CustomerIntent": "product return", "CustomerSentiment": "angry", "ConversationSubject": "Defective product"}, "messages": [{"customer": "Hello", "Id": 1}, {"agent": "Hi! How may I assist you today?", "Id": 2}]}'
  ]

  const handleSubmit = async () => {
    if (!prompt.trim()) {
      message.warning('Please enter a prompt')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    const response = await apiClient.generateC2Message(prompt)
    setLoading(false)

    if (response.data) {
      setResult(response.data)
      message.success('C2 message generated successfully!')
      // Reload history to show the new result
      if (historyData) {
        loadHistory(1)
      }
    } else if (response.error) {
      setError(response.error)
      message.error('Failed to generate C2 message')
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
      title: 'Prompt Preview',
      dataIndex: 'prompt',
      key: 'prompt',
      ellipsis: true,
      render: (text: string) => text?.substring(0, 80) + (text?.length > 80 ? '...' : ''),
    },
    {
      title: 'Response',
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

  const batchColumns = [
    {
      title: 'Prompt',
      dataIndex: 'prompt',
      key: 'prompt',
      ellipsis: true,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => {
        let color = 'default';
        if (status === 'running') color = 'processing';
        if (status === 'completed') color = 'success';
        if (status === 'failed') color = 'error';
        return <Tag color={color}>{status.toUpperCase()}</Tag>;
      },
    },
    {
      title: 'Result',
      key: 'result',
      width: 150,
      render: (_: unknown, record: BatchItem) => {
        if (record.status === 'completed' && record.result) {
          return (
            <Space direction="vertical" size={0}>
              <Text type="secondary" style={{ fontSize: 12 }}>{record.result.tokens_used || 'N/A'} tokens</Text>
              <Text type="secondary" style={{ fontSize: 12 }}>{Math.round(record.result.time_taken_ms)} ms</Text>
            </Space>
          );
        }
        if (record.status === 'failed') {
          return <Text type="danger" style={{ fontSize: 12 }}>{record.error}</Text>;
        }
        return '-';
      }
    }
  ];

  const tabItems = [
    {
      key: 'generate',
      label: 'Generate',
      children: (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Card title="Generate C2 Message">
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <Text strong>Transcript Context Prompt</Text>
                <TextArea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder='Enter an "Ongoing transcript" JSON with Properties and messages array...'
                  rows={8}
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
                {loading ? 'Generating...' : 'Generate C2 Message'}
              </Button>

              <div style={{ marginTop: 16 }}>
                <Text strong>Sample Prompts</Text>
                <Space direction="vertical" style={{ width: '100%', marginTop: 8 }}>
                  {samplePrompts.map((sample, index) => (
                    <Card key={index} size="small" style={{ background: '#f9f9f9' }}>
                      <Space align="start" style={{ width: '100%', justifyContent: 'space-between' }}>
                        <Text style={{ fontSize: 13, color: '#666' }}>{sample.substring(0, 150)}...</Text>
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
            <Card title="Generated C2 Message">
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
      key: 'batch',
      label: 'Batch Processing',
      children: (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Card title="Batch Processing">
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <Alert
                message="Paste Prompts JSON"
                description="Paste a JSON array of objects, where each object must have a 'prompt' field. The C2 message will be generated for each prompt sequentially."
                type="info"
                showIcon
              />

              <TextArea
                rows={8}
                value={batchJsonInput}
                onChange={(e) => setBatchJsonInput(e.target.value)}
                placeholder='[
  {"prompt": "Ongoing transcript: {...}"},
  {"prompt": "Ongoing transcript: {...}"}
]'
                disabled={batchLoading}
              />

              <div>
                <Text strong>Delay Between Generations (seconds)</Text>
                <Select
                  value={batchDelay}
                  onChange={(value) => setBatchDelay(value)}
                  disabled={batchLoading}
                  style={{ width: 200, marginLeft: 12 }}
                  options={[
                    { value: 5, label: '5 seconds' },
                    { value: 10, label: '10 seconds' },
                    { value: 15, label: '15 seconds' },
                    { value: 20, label: '20 seconds' },
                    { value: 25, label: '25 seconds' },
                    { value: 30, label: '30 seconds' },
                  ]}
                />
              </div>

              <Space wrap>
                <Button 
                  size="large" 
                  onClick={loadBatchItemsFromText}
                  disabled={batchLoading}
                >
                  Load Prompts
                </Button>
                <Button 
                  type="primary" 
                  size="large" 
                  onClick={runBatchGenerations}
                  disabled={batchItems.length === 0 || batchLoading}
                  loading={batchLoading}
                >
                  {batchLoading ? 'Processing Batch...' : 'Start Batch Processing'}
                </Button>
                {batchLoading && (
                  <Button 
                    danger 
                    size="large"
                    onClick={handleStopBatch}
                  >
                    Stop Batch
                  </Button>
                )}
              </Space>

              {batchLoading && (
                <div style={{ marginTop: 16 }}>
                  <Text>Processing prompt {currentBatchIndex + 1} of {batchItems.length}</Text>
                  <Progress percent={batchProgress} status="active" />
                </div>
              )}
            </Space>
          </Card>

          {batchItems.length > 0 && (
            <Card title={`Loaded Prompts (${batchItems.length})`}>
              <Table
                dataSource={batchItems}
                columns={batchColumns}
                pagination={{ pageSize: 10 }}
                expandable={{
                  expandedRowRender: (record) => (
                    <div style={{ padding: 16 }}>
                      {record.result ? (
                        <Space direction="vertical" size="small" style={{ width: '100%' }}>
                          <Text strong>Generation Result:</Text>
                          <Space size="large">
                            <Text>Tokens: {record.result.tokens_used || 'N/A'}</Text>
                            <Text>Time: {Math.round(record.result.time_taken_ms)}ms</Text>
                          </Space>
                          <div style={{ marginTop: 8 }}>
                            <Text strong>Response:</Text>
                            <Paragraph style={{ 
                              whiteSpace: 'pre-wrap', 
                              background: '#f5f5f5', 
                              padding: 12, 
                              borderRadius: 4,
                              marginTop: 8,
                              maxHeight: '300px',
                              overflow: 'auto'
                            }}>
                              {record.result.response_text}
                            </Paragraph>
                          </div>
                        </Space>
                      ) : (
                        <Text type="secondary">No result available yet.</Text>
                      )}
                    </div>
                  ),
                }}
              />
            </Card>
          )}
        </Space>
      )
    },
    {
      key: 'history',
      label: 'History',
      children: (
        <Card 
          title="History"
          extra={
            <Space>
              {selectedHistoryRowKeys.length > 0 && (
                <>
                  <Button 
                    type="primary"
                    icon={<DownloadOutlined />}
                    onClick={handleDownloadConversations}
                  >
                    Download ({selectedHistoryRowKeys.length})
                  </Button>
                  <Button 
                    danger 
                    onClick={handleDeleteSelected}
                    loading={deleteLoading}
                  >
                    Delete Selected ({selectedHistoryRowKeys.length})
                  </Button>
                </>
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
              selectedRowKeys: selectedHistoryRowKeys,
              onChange: (keys) => setSelectedHistoryRowKeys(keys),
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
                      <Paragraph>
                        <pre style={{ 
                          background: '#f5f5f5', 
                          padding: '12px', 
                          borderRadius: '4px',
                          whiteSpace: 'pre-wrap',
                          wordWrap: 'break-word'
                        }}>
                          {record.prompt}
                        </pre>
                      </Paragraph>
                    </div>
                    <div>
                      <Text strong>Response:</Text>
                      <Paragraph>
                        <pre style={{ 
                          background: '#e6f7ff', 
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
      title="C2 Message Generator"
      description="Generate customer (C2) messages using the C2MessageGeneratorAgent for conversation simulations."
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
