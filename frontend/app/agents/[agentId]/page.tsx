'use client'

import { useState, useEffect, useCallback } from 'react'
import { useParams } from 'next/navigation'
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
  Segmented,
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
import type { AgentInfo, AgentInvokeResponse, BrowseResponse, SingleAgentHistoryItem } from '@/lib/api-client'
import { useTimezone } from '@/lib/timezone-context'

const { TextArea } = Input
const { Paragraph, Text, Title } = Typography

interface BatchItem {
  key: string
  input: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  result?: AgentInvokeResponse
  error?: string
}

export default function AgentPage() {
  const params = useParams()
  const agentId = params.agentId as string
  const { formatTimestamp } = useTimezone()
  
  // Agent info state
  const [agentInfo, setAgentInfo] = useState<AgentInfo | null>(null)
  const [loadingAgent, setLoadingAgent] = useState(true)
  const [agentError, setAgentError] = useState('')
  
  // Generate state
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AgentInvokeResponse | null>(null)
  const [error, setError] = useState('')
  
  // Instructions visibility
  const [showInstructions, setShowInstructions] = useState(false)

  // History state
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyData, setHistoryData] = useState<BrowseResponse | null>(null)
  const [historyError, setHistoryError] = useState('')
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [orderBy, setOrderBy] = useState('timestamp')
  const [orderDirection, setOrderDirection] = useState<'ASC' | 'DESC'>('DESC')
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [selectedAgentVersion, setSelectedAgentVersion] = useState<string | null>(null)
  const [agentVersions, setAgentVersions] = useState<string[]>([])
  const [selectedVersionInstructions, setSelectedVersionInstructions] = useState<string | null>(null)

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
  const [selectedRecord, setSelectedRecord] = useState<SingleAgentHistoryItem | null>(null)

  // Response view mode (Plain Text or JSON)
  const [responseViewMode, setResponseViewMode] = useState<'text' | 'json'>('text')
  const [modalResponseViewMode, setModalResponseViewMode] = useState<'text' | 'json'>('text')

  // Load agent info on mount
  useEffect(() => {
    const loadAgent = async () => {
      setLoadingAgent(true)
      setAgentError('')
      const response = await apiClient.getAgent(agentId)
      setLoadingAgent(false)
      
      if (response.data) {
        setAgentInfo(response.data)
      } else if (response.error) {
        setAgentError(response.error)
        message.error('Failed to load agent info')
      }
    }
    
    loadAgent()
  }, [agentId])

  const loadHistory = useCallback(async (page: number = 1, size: number = pageSize) => {
    setHistoryLoading(true)
    setHistoryError('')
    const response = await apiClient.browseAgentHistory(agentId, page, size, orderBy, orderDirection)
    setHistoryLoading(false)

    if (response.data) {
      setHistoryData(response.data)
      setSelectedRowKeys([])
      setCurrentPage(page)
      setPageSize(size)

      // Extract unique agent versions from the data
      const versions = new Set<string>()
      response.data.items.forEach((item: any) => {
        if (item.agent_version) {
          versions.add(item.agent_version)
        }
      })
      setAgentVersions(Array.from(versions).sort())
    } else if (response.error) {
      setHistoryError(response.error)
      message.error('Failed to load history')
    }
  }, [agentId, orderBy, orderDirection, pageSize])

  const handleSubmit = async () => {
    if (!input.trim()) {
      message.warning(`Please enter ${agentInfo?.input_label?.toLowerCase() || 'input'}`)
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    const response = await apiClient.invokeAgent(agentId, input)
    setLoading(false)

    if (response.data) {
      setResult(response.data)
      message.success('Generated successfully!')
      if (historyData) {
        loadHistory(1)
      }
    } else if (response.error) {
      setError(response.error)
      message.error('Generation failed')
    }
  }

  const handleDeleteSelected = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('Please select items to delete')
      return
    }

    setDeleteLoading(true)
    const ids = selectedRowKeys.map((key) => String(key))

    const response = await apiClient.deleteAgentRecords(agentId, ids)
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
    const response = await apiClient.downloadAgentRecords(agentId, ids)

    if (response.data) {
      const url = URL.createObjectURL(response.data)
      const link = document.createElement('a')
      link.href = url
      link.download = `${agentId}_${new Date().toISOString().replace(/[:.]/g, '-')}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      message.success('Download started')
    } else if (response.error) {
      message.error('Failed to download: ' + response.error)
    }
  }

  const handleViewDetail = (record: SingleAgentHistoryItem) => {
    setSelectedRecord(record)
    setDetailModalVisible(true)
    setModalResponseViewMode('text') // Reset to text view when opening modal
  }

  const tryParseJSON = (text: string): { isValid: boolean; parsed?: any } => {
    try {
      const parsed = JSON.parse(text)
      return { isValid: true, parsed }
    } catch {
      return { isValid: false }
    }
  }

  const loadBatchItemsFromText = () => {
    if (!batchJsonInput.trim()) {
      message.warning('Paste JSON to load batch items.')
      return
    }

    try {
      const json = JSON.parse(batchJsonInput)
      const fieldName = agentInfo?.input_field || 'prompt'

      if (!Array.isArray(json)) {
        message.error(`Invalid JSON format. Expected an array of objects with "${fieldName}" field.`)
        return
      }

      const parsedItems = json
        .map((item: unknown, index: number) => {
          if (typeof item !== 'object' || item === null || !(fieldName in item)) {
            return null
          }
          const inputText = (item as Record<string, unknown>)[fieldName]
          if (typeof inputText !== 'string') {
            return null
          }
          return {
            key: `batch-${index}-${Date.now()}`,
            input: inputText,
            status: 'pending' as const,
          }
        })
        .filter((item): item is { key: string; input: string; status: 'pending' } => item !== null && item.input.trim() !== '')
      
      const items: BatchItem[] = parsedItems

      if (items.length === 0) {
        message.error(`No valid objects with "${fieldName}" field found in JSON.`)
        return
      }

      setBatchItems(items)
      setBatchProgress(0)
      setCurrentBatchIndex(-1)
      message.success(`Loaded ${items.length} items.`)
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
        const response = await apiClient.invokeAgent(agentId, newItems[i].input)

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

  if (loadingAgent) {
    return (
      <PageLayout title="Loading Agent...">
        <div style={{ textAlign: 'center', padding: 100 }}>
          <Spin size="large" />
        </div>
      </PageLayout>
    )
  }

  if (agentError || !agentInfo) {
    return (
      <PageLayout title="Agent Error">
        <Alert
          message="Error"
          description={agentError || 'Failed to load agent information'}
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
      width: 200,
    },
    {
      title: agentInfo.input_label,
      dataIndex: agentInfo.input_field,
      key: agentInfo.input_field,
      ellipsis: true,
      render: (text: string) => text || 'N/A',
    },
    {
      title: 'Response Preview',
      dataIndex: 'response',
      key: 'response',
      ellipsis: true,
      render: (text: string) => (text ? text.substring(0, 100) + (text.length > 100 ? '...' : '') : 'N/A'),
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
      render: (value: number) => (value ? Math.round(value) : 'N/A'),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      render: (_: unknown, record: SingleAgentHistoryItem) => (
        <Button type="link" size="small" onClick={() => handleViewDetail(record)}>
          View
        </Button>
      ),
    },
  ]

  const batchColumns = [
    {
      title: agentInfo.input_label,
      dataIndex: 'input',
      key: 'input',
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
            <Space direction="vertical" size={0}>
              <Text type="secondary" style={{ fontSize: 12 }}>
                {record.result.tokens_used || 'N/A'} tokens
              </Text>
              <Text type="secondary" style={{ fontSize: 12 }}>
                {Math.round(record.result.time_taken_ms)} ms
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
      key: 'generate',
      label: 'Generate',
      children: (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* Agent Instructions Card */}
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
              <pre style={{ 
                whiteSpace: 'pre-wrap', 
                wordWrap: 'break-word',
                background: '#f5f5f5',
                padding: 12,
                borderRadius: 8,
                maxHeight: 400,
                overflow: 'auto',
                fontSize: 12,
              }}>
                {agentInfo.instructions}
              </pre>
            ) : (
              <Text type="secondary">Click &quot;Show&quot; to view the agent&apos;s instruction set</Text>
            )}
          </Card>

          <Card title={`Generate with ${agentInfo.display_name}`}>
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <Text strong>{agentInfo.input_label}</Text>
                <TextArea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={agentInfo.input_placeholder}
                  rows={6}
                  style={{ marginTop: 8 }}
                  disabled={loading}
                />
              </div>

              {/* Sample Inputs Section */}
              {agentInfo.sample_inputs && agentInfo.sample_inputs.length > 0 && (
                <div style={{ marginTop: 16 }}>
                  <Text strong>Sample {agentInfo.input_label}s</Text>
                  <Space direction="vertical" style={{ width: '100%', marginTop: 8 }}>
                    {agentInfo.sample_inputs.map((sample, index) => (
                      <Card key={index} size="small" style={{ background: '#f9f9f9' }}>
                        <Space align="start" style={{ width: '100%', justifyContent: 'space-between' }}>
                          <Text style={{ fontSize: 13, color: '#666' }}>
                            {sample.label || sample.value.substring(0, 80) + '...'}
                          </Text>
                          <Button
                            size="small"
                            type="link"
                            onClick={() => setInput(sample.value)}
                            style={{ padding: 0, marginLeft: 8 }}
                          >
                            Try it
                          </Button>
                        </Space>
                      </Card>
                    ))}
                  </Space>
                </div>
              )}

              <Button
                type="primary"
                size="large"
                onClick={handleSubmit}
                loading={loading}
                disabled={!input.trim()}
                block
              >
                {loading ? 'Generating...' : 'Generate'}
              </Button>

              {error && <Alert message="Error" description={error} type="error" showIcon />}
            </Space>
          </Card>

          {result && (
            <Card title="Result">
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                    <Text strong>Response:</Text>
                    <Segmented
                      options={['Plain Text', 'JSON']}
                      value={responseViewMode === 'text' ? 'Plain Text' : 'JSON'}
                      onChange={(value) => setResponseViewMode(value === 'JSON' ? 'json' : 'text')}
                      size="small"
                    />
                  </div>
                  {(() => {
                    const jsonCheck = tryParseJSON(result.response_text)
                    if (responseViewMode === 'json') {
                      if (jsonCheck.isValid) {
                        return (
                          <pre
                            style={{
                              background: '#e6f7ff',
                              padding: 16,
                              borderRadius: 8,
                              whiteSpace: 'pre-wrap',
                              wordWrap: 'break-word',
                              marginTop: 0,
                            }}
                          >
                            {JSON.stringify(jsonCheck.parsed, null, 2)}
                          </pre>
                        )
                      } else {
                        return (
                          <>
                            <Alert
                              message="Invalid JSON"
                              description="Response is not valid JSON. Showing as plain text."
                              type="warning"
                              showIcon
                              style={{ marginBottom: 8 }}
                            />
                            <Paragraph
                              style={{
                                whiteSpace: 'pre-wrap',
                                background: '#f5f5f5',
                                padding: 16,
                                borderRadius: 8,
                                marginTop: 0,
                              }}
                            >
                              {result.response_text}
                            </Paragraph>
                          </>
                        )
                      }
                    } else {
                      return (
                        <Paragraph
                          style={{
                            whiteSpace: 'pre-wrap',
                            background: '#f5f5f5',
                            padding: 16,
                            borderRadius: 8,
                            marginTop: 0,
                          }}
                        >
                          {result.response_text}
                        </Paragraph>
                      )
                    }
                  })()}
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
                    <Text strong>{(result.agent_details as Record<string, unknown>)?.model_deployment_name as string || 'N/A'}</Text>
                  </div>
                  <div>
                    <Text type="secondary">Agent: </Text>
                    <Text strong>{(result.agent_details as Record<string, unknown>)?.agent_name as string || 'N/A'}</Text>
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
              <div>
                <Text strong>Paste JSON Array</Text>
                <Paragraph type="secondary" style={{ marginBottom: 8 }}>
                  Format: [{`"${agentInfo.input_field}": "..."`}, ...]
                </Paragraph>
                <TextArea
                  value={batchJsonInput}
                  onChange={(e) => setBatchJsonInput(e.target.value)}
                  placeholder={`[{ "${agentInfo.input_field}": "..." }, { "${agentInfo.input_field}": "..." }]`}
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
                  options={Array.from({ length: 60 }, (_, i) => i + 1).map((s) => ({
                    value: s,
                    label: `${s} second${s !== 1 ? 's' : ''} delay`,
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

                  {batchLoading && (
                    <Progress percent={batchProgress} status="active" />
                  )}

                  <Table
                    dataSource={batchItems}
                    columns={batchColumns}
                    rowKey="key"
                    pagination={false}
                    size="small"
                    scroll={{ y: 400 }}
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
                {agentVersions.length > 0 && (
                  <Select
                    value={selectedAgentVersion}
                    onChange={(val) => {
                      setSelectedAgentVersion(val)
                      // Find instructions for this version from history data
                      if (val && historyData) {
                        const item = historyData.items.find((i: any) => i.agent_version === val)
                        if (item && (item as any).agent_instructions) {
                          setSelectedVersionInstructions((item as any).agent_instructions)
                        }
                      } else {
                        setSelectedVersionInstructions(null)
                      }
                    }}
                    allowClear
                    placeholder="Filter by version"
                    style={{ width: 150 }}
                    options={[
                      ...agentVersions.map((v) => ({ value: v, label: `Version ${v}` }))
                    ]}
                  />
                )}
                <Select
                  value={orderBy}
                  onChange={(val) => {
                    setOrderBy(val)
                    loadHistory(1)
                  }}
                  style={{ width: 150 }}
                  options={[
                    { value: 'timestamp', label: 'Sort by Time' },
                    { value: 'tokens_used', label: 'Sort by Tokens' },
                    { value: 'time_taken_ms', label: 'Sort by Duration' },
                  ]}
                />
                <Tooltip title={orderDirection === 'DESC' ? 'Descending' : 'Ascending'}>
                  <Button
                    icon={orderDirection === 'DESC' ? <SortDescendingOutlined /> : <SortAscendingOutlined />}
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
              <Alert message="Error" description={historyError} type="error" showIcon style={{ marginBottom: 16 }} />
            )}

            {selectedVersionInstructions && (
              <Card
                size="small"
                title={`Agent Version ${selectedAgentVersion} Instructions`}
                style={{ marginBottom: 16, background: '#f9f9f9' }}
              >
                <pre style={{
                  whiteSpace: 'pre-wrap',
                  wordWrap: 'break-word',
                  maxHeight: 300,
                  overflow: 'auto',
                  fontSize: 12,
                  margin: 0,
                }}>
                  {selectedVersionInstructions}
                </pre>
              </Card>
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
              <Table
                dataSource={
                  selectedAgentVersion
                    ? (historyData?.items || []).filter((item: any) => item.agent_version === selectedAgentVersion)
                    : (historyData?.items || [])
                }
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
      title={agentInfo.display_name}
      description={agentInfo.description}
    >
      <Tabs defaultActiveKey="generate" items={tabItems} />

      <Modal
        title="Record Details"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={800}
      >
        {selectedRecord && (
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <Text strong>ID:</Text>
              <Text copyable style={{ marginLeft: 8 }}>{selectedRecord.id}</Text>
            </div>
            <div>
              <Text strong>Timestamp:</Text>
              <Text style={{ marginLeft: 8 }}>{formatTimestamp(selectedRecord.timestamp)}</Text>
            </div>
            <div>
              <Text strong>{agentInfo.input_label}:</Text>
              <Paragraph style={{ background: '#f5f5f5', padding: 12, borderRadius: 8, marginTop: 8 }}>
                {selectedRecord[agentInfo.input_field as keyof SingleAgentHistoryItem] as string || 'N/A'}
              </Paragraph>
            </div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <Text strong>Response:</Text>
                <Segmented
                  options={['Plain Text', 'JSON']}
                  value={modalResponseViewMode === 'text' ? 'Plain Text' : 'JSON'}
                  onChange={(value) => setModalResponseViewMode(value === 'JSON' ? 'json' : 'text')}
                  size="small"
                />
              </div>
              {(() => {
                const responseText = selectedRecord.response || selectedRecord.response_text || 'N/A'
                const jsonCheck = tryParseJSON(responseText)
                if (modalResponseViewMode === 'json') {
                  if (jsonCheck.isValid) {
                    return (
                      <pre
                        style={{
                          background: '#e6f7ff',
                          padding: 12,
                          borderRadius: 8,
                          whiteSpace: 'pre-wrap',
                          wordWrap: 'break-word',
                          marginTop: 0,
                        }}
                      >
                        {JSON.stringify(jsonCheck.parsed, null, 2)}
                      </pre>
                    )
                  } else {
                    return (
                      <>
                        <Alert
                          message="Invalid JSON"
                          description="Response is not valid JSON. Showing as plain text."
                          type="warning"
                          showIcon
                          style={{ marginBottom: 8 }}
                        />
                        <Paragraph style={{ background: '#f5f5f5', padding: 12, borderRadius: 8, marginTop: 0, whiteSpace: 'pre-wrap' }}>
                          {responseText}
                        </Paragraph>
                      </>
                    )
                  }
                } else {
                  return (
                    <Paragraph style={{ background: '#f5f5f5', padding: 12, borderRadius: 8, marginTop: 0, whiteSpace: 'pre-wrap' }}>
                      {responseText}
                    </Paragraph>
                  )
                }
              })()}
            </div>
            <Space size="large">
              <div>
                <Text type="secondary">Tokens: </Text>
                <Text strong>{selectedRecord.tokens_used || 'N/A'}</Text>
              </div>
              <div>
                <Text type="secondary">Time: </Text>
                <Text strong>{selectedRecord.time_taken_ms ? Math.round(selectedRecord.time_taken_ms) + ' ms' : 'N/A'}</Text>
              </div>
            </Space>
          </Space>
        )}
      </Modal>
    </PageLayout>
  )
}
