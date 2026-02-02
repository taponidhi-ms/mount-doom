'use client'

import { useState, useCallback, useEffect, useRef } from 'react'
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
} from 'antd'
import {
  ReloadOutlined,
  DownloadOutlined,
  DeleteOutlined,
  SortAscendingOutlined,
  SortDescendingOutlined,
  PauseOutlined,
  PlayCircleOutlined,
} from '@ant-design/icons'
import PageLayout from '@/components/PageLayout'
import { apiClient } from '@/lib/api-client'
import type { ConversationMessage, WorkflowHistoryItem, BrowseResponse, ConversationSimulationResponse } from '@/lib/types'
import { useTimezone } from '@/lib/timezone-context'

const { TextArea } = Input
const { Text } = Typography

interface BatchItem {
  key: string
  inputs: {
    customerIntent: string
    customerSentiment: string
    conversationSubject: string
  }
  status: 'pending' | 'running' | 'completed' | 'failed'
  result?: ConversationSimulationResponse
  error?: string
}

export default function ConversationSimulationPage() {
  const { formatTimestamp, formatTime } = useTimezone()

  // Simulate state
  const [customerIntent, setCustomerIntent] = useState('')
  const [customerSentiment, setCustomerSentiment] = useState('')
  const [conversationSubject, setConversationSubject] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ConversationSimulationResponse | null>(null)
  const [error, setError] = useState('')

  // History state
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyData, setHistoryData] = useState<BrowseResponse<WorkflowHistoryItem> | null>(null)
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
  const [batchPaused, setBatchPaused] = useState(false)
  const [batchProgress, setBatchProgress] = useState(0)
  const [currentBatchIndex, setCurrentBatchIndex] = useState(-1)
  const [batchJsonInput, setBatchJsonInput] = useState('')
  const [batchDelay, setBatchDelay] = useState(5)

  // Use refs to avoid closure issues in async batch loop
  const stopBatchRef = useRef(false)
  const pauseBatchRef = useRef(false)

  // Detail modal
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [selectedRecord, setSelectedRecord] = useState<WorkflowHistoryItem | null>(null)

  const loadHistory = useCallback(
    async (page: number = 1, size: number = pageSize) => {
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
    },
    [orderBy, orderDirection, pageSize]
  )

  // Load history on component mount
  useEffect(() => {
    loadHistory(1)
  }, [loadHistory])

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
      message.success('Simulation completed successfully!')
      if (historyData) {
        loadHistory(1)
      }
    } else if (response.error) {
      setError(response.error)
      message.error('Simulation failed')
    }
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

          const intent = String(itemObj.customerIntent || itemObj.CustomerIntent || '')
          const sentiment = String(itemObj.customerSentiment || itemObj.CustomerSentiment || '')
          const subject = String(itemObj.conversationSubject || itemObj.ConversationSubject || '')

          if (!intent.trim() || !sentiment.trim() || !subject.trim()) return null

          return {
            key: `batch-${index}-${Date.now()}`,
            inputs: {
              customerIntent: intent,
              customerSentiment: sentiment,
              conversationSubject: subject,
            },
            status: 'pending' as const,
          }
        })
        .filter((item): item is BatchItem => item !== null)

      if (parsedBatchItems.length === 0) {
        message.warning('No valid items found in JSON.')
        return
      }

      setBatchItems(parsedBatchItems)
      setBatchProgress(0)
      setCurrentBatchIndex(-1)
      message.success(`Loaded ${parsedBatchItems.length} items.`)
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
    setBatchPaused(false)
    stopBatchRef.current = false
    pauseBatchRef.current = false

    const newItems = [...batchItems]

    for (let i = 0; i < newItems.length; i++) {
      // Check stop flag
      if (stopBatchRef.current) {
        message.info('Batch processing stopped by user.')
        break
      }

      // Skip already completed or failed items
      if (newItems[i].status === 'completed' || newItems[i].status === 'failed') {
        continue
      }

      // Wait while paused
      while (pauseBatchRef.current) {
        await sleep(100) // Check every 100ms if still paused
        if (stopBatchRef.current) {
          message.info('Batch processing stopped by user.')
          break
        }
      }

      if (stopBatchRef.current) break

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

      // Delay before next item (if not stopped and not last item)
      if (i < newItems.length - 1 && !stopBatchRef.current) {
        await sleep(batchDelay * 1000)
      }
    }

    setBatchLoading(false)
    setBatchPaused(false)
    setCurrentBatchIndex(-1)
    stopBatchRef.current = false
    pauseBatchRef.current = false

    if (!stopBatchRef.current) {
      message.success('Batch processing completed!')
    }

    if (historyData) {
      loadHistory(1)
    }
  }

  const handleStopBatch = () => {
    stopBatchRef.current = true
    pauseBatchRef.current = false
    setBatchPaused(false)
  }

  const handlePauseBatch = () => {
    pauseBatchRef.current = true
    setBatchPaused(true)
    message.info('Batch processing paused')
  }

  const handleResumeBatch = () => {
    pauseBatchRef.current = false
    setBatchPaused(false)
    message.info('Batch processing resumed')
  }

  const handleDeleteBatchItem = (key: string) => {
    const newItems = batchItems.filter((item) => item.key !== key)
    setBatchItems(newItems)
    message.success('Item deleted')
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
      link.download = `conversation-simulation_${new Date().toISOString().replace(/[:.]/g, '-')}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      message.success('Download started')
    } else if (response.error) {
      message.error('Failed to download: ' + response.error)
    }
  }

  const handleViewDetail = (record: WorkflowHistoryItem) => {
    setSelectedRecord(record)
    setDetailModalVisible(true)
  }

  const renderConversation = (history: ConversationMessage[]) => {
    return (
      <Space orientation="vertical" size="small" style={{ width: '100%' }}>
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
              <Space orientation="vertical" size="small" style={{ width: '100%' }}>
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
  }

  const historyColumns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (text: string) => formatTimestamp(text),
      width: 250,
    },
    {
      title: 'Conversation ID',
      dataIndex: 'conversation_id',
      key: 'conversation_id',
      width: 220,
      render: (_: string, record: WorkflowHistoryItem) => {
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
      title: 'Tokens',
      dataIndex: 'total_tokens_used',
      key: 'tokens',
      width: 100,
      render: (value: number) => value || 'N/A',
    },
  ]

  const batchColumns = [
    {
      title: 'Customer Intent',
      dataIndex: ['inputs', 'customerIntent'],
      key: 'customerIntent',
      ellipsis: true,
    },
    {
      title: 'Customer Sentiment',
      dataIndex: ['inputs', 'customerSentiment'],
      key: 'customerSentiment',
      ellipsis: true,
    },
    {
      title: 'Conversation Subject',
      dataIndex: ['inputs', 'conversationSubject'],
      key: 'conversationSubject',
      ellipsis: true,
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
            <Space orientation="vertical" size={0}>
              <Text type="secondary" style={{ fontSize: 12 }} copyable>
                {record.result.conversation_id}
              </Text>
              <Text type="secondary" style={{ fontSize: 12 }}>
                {record.result.conversation_history.length} msgs
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
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      align: 'center' as const,
      render: (_: unknown, record: BatchItem) => {
        if (record.status === 'pending' && !batchLoading) {
          return (
            <Popconfirm
              title="Delete this item?"
              description="This action cannot be undone."
              onConfirm={() => handleDeleteBatchItem(record.key)}
              okText="Delete"
              cancelText="Cancel"
              okButtonProps={{ danger: true }}
            >
              <Button type="link" danger icon={<DeleteOutlined />} size="small">
                Delete
              </Button>
            </Popconfirm>
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

  const tabItems = [
    {
      key: 'simulate',
      label: 'Simulate',
      children: (
        <Space orientation="vertical" size="large" style={{ width: '100%' }}>
          <Card title="Simulation Configuration">
            <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
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
                <Space orientation="vertical" style={{ width: '100%', marginTop: 8 }}>
                  {sampleConfigs.map((sample, index) => (
                    <Card key={index} size="small" style={{ background: '#f9f9f9' }}>
                      <Space
                        align="start"
                        style={{ width: '100%', justifyContent: 'space-between' }}
                      >
                        <Space orientation="vertical" size={0}>
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
                          onClick={() => {
                            setCustomerIntent(sample.customerIntent)
                            setCustomerSentiment(sample.customerSentiment)
                            setConversationSubject(sample.conversationSubject)
                          }}
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
              <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
                <Space size="large" wrap>
                  <div>
                    <Text type="secondary">Status: </Text>
                    <Tag color={result.conversation_status === 'Completed' ? 'green' : 'orange'}>
                      {result.conversation_status}
                    </Tag>
                  </div>
                  <div>
                    <Text type="secondary">Messages: </Text>
                    <Text strong>{result.conversation_history.length}</Text>
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
                    {renderConversation(result.conversation_history)}
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
        <Space orientation="vertical" size="large" style={{ width: '100%' }}>
          <Card title="Batch Processing">
            <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <Text strong>Paste JSON Array</Text>
                <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>
                  Format: Array of objects with customerIntent, customerSentiment, conversationSubject fields
                </Text>
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
                      loading={batchLoading && !batchPaused}
                      disabled={batchItems.length === 0 || batchLoading}
                    >
                      {batchLoading
                        ? batchPaused
                          ? `Paused at ${currentBatchIndex + 1}/${batchItems.length}`
                          : `Processing ${currentBatchIndex + 1}/${batchItems.length}`
                        : 'Start Batch'}
                    </Button>
                    {batchLoading && !batchPaused && (
                      <>
                        <Button icon={<PauseOutlined />} onClick={handlePauseBatch}>
                          Pause
                        </Button>
                        <Button danger onClick={handleStopBatch}>
                          Stop
                        </Button>
                      </>
                    )}
                    {batchLoading && batchPaused && (
                      <>
                        <Button
                          type="primary"
                          icon={<PlayCircleOutlined />}
                          onClick={handleResumeBatch}
                        >
                          Resume
                        </Button>
                        <Button danger onClick={handleStopBatch}>
                          Stop
                        </Button>
                      </>
                    )}
                  </Space>

                  {batchLoading && (
                    <Progress
                      percent={batchProgress}
                      status={batchPaused ? 'normal' : 'active'}
                    />
                  )}

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
                            {renderConversation(record.result.conversation_history)}
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
        <Space orientation="vertical" size="large" style={{ width: '100%' }}>
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

            <Table<WorkflowHistoryItem>
              dataSource={historyData?.items || []}
              columns={historyColumns as any}
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
                    {renderConversation(record.conversation_history)}
                  </div>
                ),
                rowExpandable: (record) => record.conversation_history?.length > 0,
              }}
              scroll={{ x: true }}
            />
          </Card>
        </Space>
      ),
    },
  ]

  return (
    <PageLayout
      title="Conversation Simulation"
      description="Simulate multi-turn conversations between C1 (customer service representative) and C2 (customer) agents."
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
          <Space orientation="vertical" style={{ width: '100%' }}>
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
                <Tag
                  color={selectedRecord.conversation_status === 'Completed' ? 'green' : 'orange'}
                >
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
                {renderConversation(selectedRecord.conversation_history)}
              </div>
            </div>
          </Space>
        )}
      </Modal>
    </PageLayout>
  )
}
