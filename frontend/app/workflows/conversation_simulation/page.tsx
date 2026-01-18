'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  Button,
  Card,
  Input,
  Tabs,
  Table,
  Space,
  Typography,
  message,
  Alert,
  Progress,
  Select,
  Tag,
  Popconfirm,
  Tooltip,
  Modal,
  Collapse,
  Spin,
} from 'antd'
import {
  ReloadOutlined,
  DownloadOutlined,
  DeleteOutlined,
  SortAscendingOutlined,
  SortDescendingOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons'
import PageLayout from '@/components/PageLayout'
import { apiClient } from '@/lib/api-client'
import type { 
  WorkflowInfo, 
  BrowseResponse, 
  MultiAgentHistoryItem,
  ConversationMessage,
} from '@/lib/api-client'
import { useTimezone } from '@/lib/timezone-context'

const { TextArea } = Input
const { Paragraph, Text, Title } = Typography
const { Panel } = Collapse

interface MultiAgentResponse {
  conversation_history: ConversationMessage[]
  conversation_status: string
  total_time_taken_ms: number
  start_time: string
  end_time: string
  conversation_id: string
}

interface BatchItem {
  key: string
  inputs: Record<string, string>
  status: 'pending' | 'running' | 'completed' | 'failed'
  result?: MultiAgentResponse
  error?: string
}

export default function ConversationSimulationPage() {
  const { formatTimestamp, formatTime } = useTimezone()
  
  // Workflow info state
  const [workflowInfo, setWorkflowInfo] = useState<WorkflowInfo | null>(null)
  const [loadingWorkflow, setLoadingWorkflow] = useState(true)
  const [workflowError, setWorkflowError] = useState('')
  
  // Simulate state
  const [inputs, setInputs] = useState({
    customerIntent: '',
    customerSentiment: '',
    conversationSubject: '',
  })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<MultiAgentResponse | null>(null)
  const [error, setError] = useState('')
  
  // Instructions visibility
  const [showInstructions, setShowInstructions] = useState(false)

  // History state
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyData, setHistoryData] = useState<BrowseResponse<MultiAgentHistoryItem> | null>(null)
  const [historyError, setHistoryError] = useState('')
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [orderBy, setOrderBy] = useState('timestamp')
  const [orderDirection, setOrderDirection] = useState<'ASC' | 'DESC'>('DESC')
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)

  // Batch state
  const [batchItems, setBatchItems] = useState<BatchItem[]>([])
  const [batchLoading, setBatchLoading] = useState(false)
  const [batchProgress, setBatchProgress] = useState(0)
  const [currentBatchIndex, setCurrentBatchIndex] = useState(-1)
  const [batchJsonInput, setBatchJsonInput] = useState('')
  const [stopBatchRequested, setStopBatchRequested] = useState(false)
  const [batchDelay, setBatchDelay] = useState(5)

  // Detail modal
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [selectedRecord, setSelectedRecord] = useState<MultiAgentHistoryItem | null>(null)

  const sampleConfigs = [
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
  ]

  // Load workflow info on mount
  useEffect(() => {
    const loadWorkflow = async () => {
      setLoadingWorkflow(true)
      setWorkflowError('')
      const response = await apiClient.getWorkflow('conversation_simulation')
      setLoadingWorkflow(false)
      
      if (response.data) {
        setWorkflowInfo(response.data)
      } else if (response.error) {
        setWorkflowError(response.error)
        message.error('Failed to load workflow info')
      }
    }
    
    loadWorkflow()
  }, [])

  const loadHistory = useCallback(async (page: number = 1, size: number = pageSize) => {
    setHistoryLoading(true)
    setHistoryError('')
    const response = await apiClient.browseConversationSimulations(page, size, orderBy, orderDirection)
    setHistoryLoading(false)

    if (response.data) {
      setHistoryData(response.data)
      setSelectedRowKeys([])
      setCurrentPage(page)
      setPageSize(size)
    } else if (response.error) {
      setHistoryError(response.error)
      message.error('Failed to load history')
    }
  }, [orderBy, orderDirection, pageSize])

  const updateInput = (name: string, value: string) => {
    setInputs((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async () => {
    if (!inputs.customerIntent.trim() || !inputs.customerSentiment.trim() || !inputs.conversationSubject.trim()) {
      message.warning('Please fill in all fields')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    const response = await apiClient.simulateConversation(
      inputs.customerIntent,
      inputs.customerSentiment,
      inputs.conversationSubject
    )
    setLoading(false)

    if (response.data) {
      setResult(response.data as unknown as MultiAgentResponse)
      message.success('Simulation completed successfully!')
      if (historyData) {
        loadHistory(1)
      }
    } else if (response.error) {
      setError(response.error)
      message.error('Simulation failed')
    }
  }

  const handleDeleteSelected = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('Please select items to delete')
      return
    }

    setDeleteLoading(true)
    const ids = selectedRowKeys.map((key) => String(key))

    const response = await apiClient.deleteConversationSimulations(ids)
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

  const handleDownloadSelected = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('Please select items to download')
      return
    }

    const ids = selectedRowKeys.map((key) => String(key))
    const response = await apiClient.downloadConversationSimulations(ids)

    if (response.data) {
      const url = URL.createObjectURL(response.data)
      const link = document.createElement('a')
      link.href = url
      link.download = `conversation_simulation_${new Date().toISOString().replace(/[:.]/g, '-')}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      message.success('Download started')
    } else if (response.error) {
      message.error('Failed to download: ' + response.error)
    }
  }

  const handleViewDetail = (record: MultiAgentHistoryItem) => {
    setSelectedRecord(record)
    setDetailModalVisible(true)
  }

  const loadBatchItemsFromText = () => {
    if (!batchJsonInput.trim()) {
      message.warning('Paste JSON to load batch items.')
      return
    }

    try {
      const json = JSON.parse(batchJsonInput)
      let items: unknown[] = []

      if (Array.isArray(json)) {
        items = json
      } else if (json.CustomerPersonas && Array.isArray(json.CustomerPersonas)) {
        items = json.CustomerPersonas
      } else {
        message.error('Invalid JSON format. Expected array or object with CustomerPersonas array.')
        return
      }

      const parsedBatchItems = items
        .map((item: unknown, index: number) => {
          if (typeof item !== 'object' || item === null) return null

          const itemObj = item as Record<string, unknown>
          const batchInputs: Record<string, string> = {
            customerIntent: String(itemObj.customerIntent || itemObj.CustomerIntent || ''),
            customerSentiment: String(itemObj.customerSentiment || itemObj.CustomerSentiment || ''),
            conversationSubject: String(itemObj.conversationSubject || itemObj.ConversationSubject || ''),
          }

          if (!batchInputs.customerIntent || !batchInputs.customerSentiment || !batchInputs.conversationSubject) {
            return null
          }

          return {
            key: `batch-${index}-${Date.now()}`,
            inputs: batchInputs,
            status: 'pending' as const,
          }
        })
        .filter((item): item is { key: string; inputs: Record<string, string>; status: 'pending' } => item !== null)
      
      const batchItemsToSet: BatchItem[] = parsedBatchItems

      if (batchItemsToSet.length === 0) {
        message.warning('No valid items found in JSON.')
        return
      }

      setBatchItems(batchItemsToSet)
      setBatchProgress(0)
      setCurrentBatchIndex(-1)
      message.success(`Loaded ${batchItemsToSet.length} items.`)
    } catch (err) {
      message.error('Failed to parse JSON.')
      console.error(err)
    }
  }

  const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

  const runBatch = async () => {
    if (batchItems.length === 0) return

    setBatchLoading(true)
    setBatchProgress(0)
    setStopBatchRequested(false)

    const newItems = [...batchItems]

    for (let i = 0; i < newItems.length; i++) {
      if (stopBatchRequested) {
        message.info('Batch processing stopped by user.')
        break
      }

      setCurrentBatchIndex(i)
      newItems[i].status = 'running'
      setBatchItems([...newItems])

      try {
        const response = await apiClient.simulateConversation(
          newItems[i].inputs.customerIntent,
          newItems[i].inputs.customerSentiment,
          newItems[i].inputs.conversationSubject
        )

        if (response.data) {
          newItems[i].status = 'completed'
          newItems[i].result = response.data as unknown as MultiAgentResponse
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

      if (i < newItems.length - 1 && !stopBatchRequested) {
        await sleep(batchDelay * 1000)
      }
    }

    setBatchLoading(false)
    setCurrentBatchIndex(-1)
    setStopBatchRequested(false)
    message.success('Batch processing completed!')

    if (historyData) {
      loadHistory(1)
    }
  }

  const handleStopBatch = () => {
    setStopBatchRequested(true)
  }

  const renderConversation = (history: ConversationMessage[]) => {
    return (
      <Space direction="vertical" size="small" style={{ width: '100%' }}>
        {history.map((msg, index) => {
          const isSystem = msg.agent_name === 'System'
          const isC1 = msg.agent_name === 'C1Agent' || msg.agent_name === 'C1MessageGeneratorAgent'

          let bgColor = '#ffffff'
          if (isC1) bgColor = '#e6f7ff'
          else if (!isSystem) bgColor = '#f6ffed'

          let tagColor = 'default'
          if (isC1) tagColor = 'blue'
          else if (!isSystem) tagColor = 'green'

          return (
            <Card
              key={index}
              size="small"
              style={{
                background: bgColor,
                border: isSystem ? 'none' : undefined,
                boxShadow: isSystem ? 'none' : undefined,
              }}
              styles={{
                body: isSystem
                  ? { padding: '4px 0', fontStyle: 'italic', color: '#888', textAlign: 'center' }
                  : undefined,
              }}
            >
              {isSystem ? (
                <Text type="secondary" italic style={{ fontSize: 12 }}>
                  {msg.message}
                </Text>
              ) : (
                <Space direction="vertical" size="small" style={{ width: '100%' }}>
                  <div>
                    <Tag color={tagColor}>{msg.agent_name}</Tag>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {formatTime(msg.timestamp)}
                    </Text>
                  </div>
                  <Text>{msg.message}</Text>
                </Space>
              )}
            </Card>
          )
        })}
      </Space>
    )
  }

  if (loadingWorkflow) {
    return (
      <PageLayout title="Loading Workflow...">
        <div style={{ textAlign: 'center', padding: 100 }}>
          <Spin size="large" />
        </div>
      </PageLayout>
    )
  }

  if (workflowError) {
    return (
      <PageLayout title="Workflow Error">
        <Alert
          message="Error"
          description={workflowError}
          type="error"
          showIcon
        />
      </PageLayout>
    )
  }

  const historyColumns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (text: string) => formatTimestamp(text),
      width: 180,
    },
    {
      title: 'Conversation ID',
      dataIndex: 'conversation_id',
      key: 'conversation_id',
      width: 220,
      render: (_: string, record: MultiAgentHistoryItem) => {
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
      render: (props: Record<string, unknown>) => (props?.CustomerIntent as string) || 'N/A',
    },
    {
      title: 'Sentiment',
      dataIndex: 'conversation_properties',
      key: 'sentiment',
      width: 120,
      render: (props: Record<string, unknown>) => (props?.CustomerSentiment as string) || 'N/A',
    },
    {
      title: 'Subject',
      dataIndex: 'conversation_properties',
      key: 'subject',
      ellipsis: true,
      render: (props: Record<string, unknown>) => (props?.ConversationSubject as string) || 'N/A',
    },
    {
      title: 'Status',
      dataIndex: 'conversation_status',
      key: 'status',
      width: 120,
      render: (status: string) => (
        <Tag color={status === 'Completed' ? 'green' : 'orange'}>{status}</Tag>
      ),
    },
    {
      title: 'Messages',
      dataIndex: 'conversation_history',
      key: 'messages',
      width: 100,
      render: (history: ConversationMessage[]) => history?.length || 0,
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      render: (_: unknown, record: MultiAgentHistoryItem) => (
        <Button type="link" size="small" onClick={() => handleViewDetail(record)}>
          View
        </Button>
      ),
    },
  ]

  const batchColumns = [
    {
      title: 'Intent',
      dataIndex: ['inputs', 'customerIntent'],
      key: 'intent',
      ellipsis: true,
      render: (_: unknown, record: BatchItem) => record.inputs.customerIntent || 'N/A',
    },
    {
      title: 'Sentiment',
      dataIndex: ['inputs', 'customerSentiment'],
      key: 'sentiment',
      ellipsis: true,
      render: (_: unknown, record: BatchItem) => record.inputs.customerSentiment || 'N/A',
    },
    {
      title: 'Subject',
      dataIndex: ['inputs', 'conversationSubject'],
      key: 'subject',
      ellipsis: true,
      render: (_: unknown, record: BatchItem) => record.inputs.conversationSubject || 'N/A',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => {
        let color = 'default'
        if (status === 'running') color = 'processing'
        if (status === 'completed') color = 'success'
        if (status === 'failed') color = 'error'
        return <Tag color={color}>{status.toUpperCase()}</Tag>
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
              <Text type="secondary" style={{ fontSize: 12 }} copyable>
                {record.result.conversation_id}
              </Text>
              <Text type="secondary" style={{ fontSize: 12 }}>
                {record.result.conversation_history?.length || 0} msgs
              </Text>
            </Space>
          )
        }
        if (record.status === 'failed') {
          return (
            <Text type="danger" style={{ fontSize: 12 }}>
              {record.error}
            </Text>
          )
        }
        return '-'
      },
    },
  ]

  const rowSelection = {
    selectedRowKeys,
    onChange: (keys: React.Key[]) => setSelectedRowKeys(keys),
  }

  const tabItems = [
    {
      key: 'simulate',
      label: 'Simulate',
      children: (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* Agent Instructions Cards */}
          {workflowInfo && (
            <Card 
              title={
                <Space>
                  <InfoCircleOutlined />
                  <span>Agent Instructions</span>
                </Space>
              }
              extra={
                <Button 
                  type="text" 
                  onClick={() => setShowInstructions(!showInstructions)}
                >
                  {showInstructions ? 'Hide' : 'Show'}
                </Button>
              }
              size="small"
            >
              {showInstructions ? (
                <Collapse defaultActiveKey={[]}>
                  {workflowInfo.agents.map((agent) => (
                    <Panel 
                      header={
                        <Space>
                          <Text strong>{agent.display_name}</Text>
                          <Tag>{agent.role}</Tag>
                        </Space>
                      } 
                      key={agent.agent_id}
                    >
                      <pre style={{ 
                        whiteSpace: 'pre-wrap', 
                        wordWrap: 'break-word',
                        background: '#f5f5f5',
                        padding: 12,
                        borderRadius: 8,
                        maxHeight: 300,
                        overflow: 'auto',
                        fontSize: 12,
                      }}>
                        {agent.instructions}
                      </pre>
                    </Panel>
                  ))}
                </Collapse>
              ) : (
                <Text type="secondary">
                  Click &quot;Show&quot; to view the instruction sets for {workflowInfo.agents.length} agents
                </Text>
              )}
            </Card>
          )}

          <Card title="Simulation Configuration">
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <Text strong>Customer Intent</Text>
                <Input
                  value={inputs.customerIntent}
                  onChange={(e) => updateInput('customerIntent', e.target.value)}
                  placeholder="e.g., Technical Support, Billing Inquiry, Product Return"
                  style={{ marginTop: 8 }}
                  disabled={loading}
                  size="large"
                />
              </div>

              <div>
                <Text strong>Customer Sentiment</Text>
                <Input
                  value={inputs.customerSentiment}
                  onChange={(e) => updateInput('customerSentiment', e.target.value)}
                  placeholder="e.g., Frustrated, Happy, Confused, Angry"
                  style={{ marginTop: 8 }}
                  disabled={loading}
                  size="large"
                />
              </div>

              <div>
                <Text strong>Conversation Subject</Text>
                <Input
                  value={inputs.conversationSubject}
                  onChange={(e) => updateInput('conversationSubject', e.target.value)}
                  placeholder="e.g., Product Defect, Service Cancellation, Account Issue"
                  style={{ marginTop: 8 }}
                  disabled={loading}
                  size="large"
                />
              </div>

              <Button
                type="primary"
                size="large"
                onClick={handleSubmit}
                loading={loading}
                block
              >
                {loading ? 'Simulating...' : 'Start Simulation'}
              </Button>

              <div style={{ marginTop: 16 }}>
                <Text strong>Sample Configurations</Text>
                <Space direction="vertical" style={{ width: '100%', marginTop: 8 }}>
                  {sampleConfigs.map((sample, index) => (
                    <Card key={index} size="small" style={{ background: '#f9f9f9' }}>
                      <Space
                        align="start"
                        style={{ width: '100%', justifyContent: 'space-between' }}
                      >
                        <Space direction="vertical" size={0}>
                          <Text style={{ fontSize: 13, color: '#666' }}>
                            <strong>Intent:</strong> {sample.customerIntent}
                          </Text>
                          <Text style={{ fontSize: 13, color: '#666' }}>
                            <strong>Sentiment:</strong> {sample.customerSentiment}
                          </Text>
                          <Text style={{ fontSize: 13, color: '#666' }}>
                            <strong>Subject:</strong> {sample.conversationSubject}
                          </Text>
                        </Space>
                        <Button
                          size="small"
                          type="link"
                          onClick={() => setInputs(sample)}
                          style={{ padding: 0, marginLeft: 8 }}
                        >
                          Try it
                        </Button>
                      </Space>
                    </Card>
                  ))}
                </Space>
              </div>

              {error && <Alert message="Error" description={error} type="error" showIcon />}
            </Space>
          </Card>

          {result && (
            <Card title="Simulation Result">
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <Space size="large" wrap>
                  <div>
                    <Text type="secondary">Status: </Text>
                    <Tag color={result.conversation_status === 'Completed' ? 'green' : 'orange'}>
                      {result.conversation_status}
                    </Tag>
                  </div>
                  <div>
                    <Text type="secondary">Messages: </Text>
                    <Text strong>{result.conversation_history?.length || 0}</Text>
                  </div>
                  <div>
                    <Text type="secondary">Time Taken: </Text>
                    <Text strong>{Math.round(result.total_time_taken_ms)} ms</Text>
                  </div>
                  <div>
                    <Text type="secondary">Conversation ID: </Text>
                    <Text copyable strong>
                      {result.conversation_id}
                    </Text>
                  </div>
                </Space>

                <div>
                  <Text strong>Conversation:</Text>
                  <div style={{ marginTop: 8, maxHeight: 500, overflowY: 'auto' }}>
                    {renderConversation(result.conversation_history || [])}
                  </div>
                </div>
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
              <div>
                <Text strong>Paste JSON Array</Text>
                <Paragraph type="secondary" style={{ marginBottom: 8 }}>
                  Format: Array of objects with customerIntent, customerSentiment, conversationSubject fields
                </Paragraph>
                <TextArea
                  value={batchJsonInput}
                  onChange={(e) => setBatchJsonInput(e.target.value)}
                  placeholder={`[{ "customerIntent": "...", "customerSentiment": "...", "conversationSubject": "..." }]`}
                  rows={6}
                  disabled={batchLoading}
                />
              </div>

              <Space>
                <Button onClick={loadBatchItemsFromText} disabled={batchLoading}>
                  Load Items
                </Button>
                <Select
                  value={batchDelay}
                  onChange={setBatchDelay}
                  style={{ width: 180 }}
                  disabled={batchLoading}
                  options={[5, 10, 15, 20, 30, 45, 60].map((s) => ({
                    value: s,
                    label: `${s} second delay`,
                  }))}
                />
              </Space>

              {batchItems.length > 0 && (
                <>
                  <Space>
                    <Button
                      type="primary"
                      onClick={runBatch}
                      loading={batchLoading}
                      disabled={batchItems.length === 0}
                    >
                      {batchLoading
                        ? `Processing ${currentBatchIndex + 1}/${batchItems.length}`
                        : 'Start Batch'}
                    </Button>
                    {batchLoading && (
                      <Button danger onClick={handleStopBatch}>
                        Stop Batch
                      </Button>
                    )}
                  </Space>

                  {batchLoading && <Progress percent={batchProgress} status="active" />}

                  <Table
                    dataSource={batchItems}
                    columns={batchColumns}
                    rowKey="key"
                    pagination={false}
                    size="small"
                    scroll={{ y: 400 }}
                    expandable={{
                      expandedRowRender: (record) =>
                        record.result ? (
                          <div style={{ padding: 16 }}>
                            {renderConversation(record.result.conversation_history || [])}
                          </div>
                        ) : null,
                      rowExpandable: (record) => record.status === 'completed',
                    }}
                  />
                </>
              )}
            </Space>
          </Card>
        </Space>
      ),
    },
    {
      key: 'history',
      label: 'History',
      children: (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Card
            title="History"
            extra={
              <Space>
                <Tooltip title="Reload">
                  <Button
                    icon={<ReloadOutlined />}
                    onClick={() => loadHistory(currentPage)}
                    loading={historyLoading}
                  />
                </Tooltip>
                <Select
                  value={orderBy}
                  onChange={(val) => {
                    setOrderBy(val)
                    loadHistory(1)
                  }}
                  style={{ width: 150 }}
                  options={[
                    { value: 'timestamp', label: 'Sort by Time' },
                    { value: 'total_tokens_used', label: 'Sort by Tokens' },
                    { value: 'total_time_taken_ms', label: 'Sort by Duration' },
                  ]}
                />
                <Tooltip title={orderDirection === 'DESC' ? 'Descending' : 'Ascending'}>
                  <Button
                    icon={
                      orderDirection === 'DESC' ? (
                        <SortDescendingOutlined />
                      ) : (
                        <SortAscendingOutlined />
                      )
                    }
                    onClick={() => {
                      setOrderDirection(orderDirection === 'DESC' ? 'ASC' : 'DESC')
                      loadHistory(1)
                    }}
                  />
                </Tooltip>
              </Space>
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

            <Space style={{ marginBottom: 16 }}>
              <Popconfirm
                title="Delete selected items?"
                description={`This will permanently delete ${selectedRowKeys.length} item(s).`}
                onConfirm={handleDeleteSelected}
                okText="Delete"
                okButtonProps={{ danger: true }}
                disabled={selectedRowKeys.length === 0}
              >
                <Button
                  icon={<DeleteOutlined />}
                  danger
                  disabled={selectedRowKeys.length === 0}
                  loading={deleteLoading}
                >
                  Delete ({selectedRowKeys.length})
                </Button>
              </Popconfirm>
              <Button
                icon={<DownloadOutlined />}
                onClick={handleDownloadSelected}
                disabled={selectedRowKeys.length === 0}
              >
                Download ({selectedRowKeys.length})
              </Button>
            </Space>

            {!historyData && !historyLoading && !historyError && (
              <div style={{ textAlign: 'center', padding: 40 }}>
                <Button type="primary" onClick={() => loadHistory(1)}>
                  Load History
                </Button>
              </div>
            )}

            {(historyData || historyLoading) && (
              <Table<MultiAgentHistoryItem>
                dataSource={historyData?.items || []}
                columns={historyColumns}
                rowKey="id"
                loading={historyLoading}
                rowSelection={rowSelection}
                pagination={{
                  current: historyData?.page || 1,
                  pageSize: historyData?.page_size || 10,
                  total: historyData?.total_count || 0,
                  showSizeChanger: true,
                  showTotal: (total, range) => `${range[0]}-${range[1]} of ${total}`,
                  onChange: (page, size) => loadHistory(page, size),
                }}
                expandable={{
                  expandedRowRender: (record) => (
                    <div style={{ padding: 16 }}>
                      {renderConversation(record.conversation_history || [])}
                    </div>
                  ),
                  rowExpandable: (record) => (record.conversation_history?.length || 0) > 0,
                }}
                scroll={{ x: true }}
              />
            )}
          </Card>
        </Space>
      ),
    },
  ]

  return (
    <PageLayout 
      title={workflowInfo?.display_name || 'Conversation Simulation'}
      description={workflowInfo?.description || 'Simulate multi-turn conversations between C1 (customer service representative) and C2 (customer) agents.'}
    >
      <Tabs defaultActiveKey="simulate" items={tabItems} />

      <Modal
        title="Conversation Details"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={900}
      >
        {selectedRecord && (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Space size="large" wrap>
              <div>
                <Text type="secondary">Conversation ID: </Text>
                <Text copyable strong>
                  {selectedRecord.conversation_id || selectedRecord.id}
                </Text>
              </div>
              <div>
                <Text type="secondary">Timestamp: </Text>
                <Text>{formatTimestamp(selectedRecord.timestamp)}</Text>
              </div>
              <div>
                <Text type="secondary">Status: </Text>
                <Tag color={selectedRecord.conversation_status === 'Completed' ? 'green' : 'orange'}>
                  {selectedRecord.conversation_status}
                </Tag>
              </div>
            </Space>

            {selectedRecord.conversation_properties && (
              <Card size="small" title="Properties">
                <Space wrap>
                  {Object.entries(selectedRecord.conversation_properties).map(([key, value]) => (
                    <div key={key}>
                      <Text type="secondary">{key}: </Text>
                      <Text strong>{String(value)}</Text>
                    </div>
                  ))}
                </Space>
              </Card>
            )}

            <div>
              <Text strong>Conversation:</Text>
              <div style={{ marginTop: 8, maxHeight: 500, overflowY: 'auto' }}>
                {renderConversation(selectedRecord.conversation_history || [])}
              </div>
            </div>
          </Space>
        )}
      </Modal>
    </PageLayout>
  )
}
