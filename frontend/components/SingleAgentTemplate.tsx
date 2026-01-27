'use client'

import { useState, useCallback, useEffect, ReactNode } from 'react'
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
  Checkbox,
  Popconfirm,
  Tooltip,
  Modal,
  Dropdown,
} from 'antd'
import {
  ReloadOutlined,
  DownloadOutlined,
  DeleteOutlined,
  FilterOutlined,
  SortAscendingOutlined,
  SortDescendingOutlined,
  SettingOutlined,
} from '@ant-design/icons'
import { useTimezone } from '@/lib/timezone-context'
import type {
  SingleAgentConfig,
  SingleAgentResponse,
  SingleAgentHistoryItem,
  BatchItem,
  BrowseResponse,
} from '@/lib/types'

const { TextArea } = Input
const { Paragraph, Text } = Typography

interface SingleAgentTemplateProps {
  config: SingleAgentConfig
}

export default function SingleAgentTemplate({ config }: SingleAgentTemplateProps) {
  const { formatTimestamp } = useTimezone()
  
  // Generate state
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<SingleAgentResponse | null>(null)
  const [error, setError] = useState('')

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
  const [visibleColumns, setVisibleColumns] = useState<Record<string, boolean>>({
    timestamp: true,
    document_id: false,
    conversation_id: false,
    input: true,
    response: true,
    tokens: true,
    time: true,
    actions: true,
  })

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

  // Batch detail modal
  const [batchDetailModalVisible, setBatchDetailModalVisible] = useState(false)
  const [selectedBatchItem, setSelectedBatchItem] = useState<BatchItem | null>(null)

  const loadBatchItemsFromText = () => {
    if (!batchJsonInput.trim()) {
      message.warning('Paste JSON to load batch items.')
      return
    }

    try {
      const json = JSON.parse(batchJsonInput)
      const fieldName = config.inputFieldName

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
        const response = await config.generateFn(newItems[i].input)

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

  const loadHistory = useCallback(async (page: number = 1, size: number = pageSize) => {
    setHistoryLoading(true)
    setHistoryError('')
    const response = await config.browseFn(page, size, orderBy, orderDirection)
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
  }, [config, orderBy, orderDirection, pageSize])

  // Load history on component mount
  useEffect(() => {
    loadHistory(1)
  }, [])

  const handleDeleteSelected = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('Please select items to delete')
      return
    }

    setDeleteLoading(true)
    const ids = selectedRowKeys.map((key) => String(key))

    const response = await config.deleteFn(ids)
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
    const response = await config.downloadFn(ids)

    if (response.data) {
      const url = URL.createObjectURL(response.data)
      const link = document.createElement('a')
      link.href = url
      link.download = `${config.pageKey}_${new Date().toISOString().replace(/[:.]/g, '-')}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      message.success('Download started')
    } else if (response.error) {
      message.error('Failed to download: ' + response.error)
    }
  }

  const handleSubmit = async () => {
    if (!input.trim()) {
      message.warning(`Please enter ${config.inputLabel.toLowerCase()}`)
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    const response = await config.generateFn(input)
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

  const handleViewDetail = (record: SingleAgentHistoryItem) => {
    setSelectedRecord(record)
    setDetailModalVisible(true)
  }

  const handleViewBatchDetail = (item: BatchItem) => {
    setSelectedBatchItem(item)
    setBatchDetailModalVisible(true)
  }

  const allHistoryColumns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (text: string) => formatTimestamp(text),
      width: 200,
      visible: visibleColumns.timestamp,
    },
    {
      title: 'Document ID',
      dataIndex: 'id',
      key: 'document_id',
      width: 120,
      ellipsis: {
        showTitle: false,
      },
      render: (text: string) => (
        <Tooltip title={text}>
          <span>{text?.substring(0, 8)}...</span>
        </Tooltip>
      ),
      visible: visibleColumns.document_id,
    },
    {
      title: 'Conversation ID',
      dataIndex: 'conversation_id',
      key: 'conversation_id',
      width: 150,
      ellipsis: {
        showTitle: false,
      },
      render: (text: string) => (
        <Tooltip title={text}>
          <span>{text?.substring(0, 12)}...</span>
        </Tooltip>
      ),
      visible: visibleColumns.conversation_id,
    },
    {
      title: 'Input',
      dataIndex: config.inputFieldName,
      key: 'input',
      width: 300,
      ellipsis: {
        showTitle: false,
      },
      render: (text: string) => (
        <Tooltip title={text} overlayStyle={{ maxWidth: 500 }}>
          <div style={{
            maxWidth: '100%',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}>
            {text || 'N/A'}
          </div>
        </Tooltip>
      ),
      visible: visibleColumns.input,
    },
    {
      title: 'Response',
      dataIndex: 'response',
      key: 'response',
      width: 400,
      ellipsis: {
        showTitle: false,
      },
      render: (text: string) => (
        <Tooltip title={text} overlayStyle={{ maxWidth: 500 }}>
          <div style={{
            maxWidth: '100%',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}>
            {text || 'N/A'}
          </div>
        </Tooltip>
      ),
      visible: visibleColumns.response,
    },
    {
      title: 'Tokens',
      dataIndex: 'tokens_used',
      key: 'tokens',
      width: 100,
      render: (value: number) => value || 'N/A',
      visible: visibleColumns.tokens,
    },
    {
      title: 'Time (ms)',
      dataIndex: 'time_taken_ms',
      key: 'time',
      width: 120,
      render: (value: number) => (value ? Math.round(value) : 'N/A'),
      visible: visibleColumns.time,
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      fixed: 'right' as const,
      render: (_: unknown, record: SingleAgentHistoryItem) => (
        <Button type="link" size="small" onClick={() => handleViewDetail(record)}>
          View
        </Button>
      ),
      visible: visibleColumns.actions,
    },
  ]

  const historyColumns = (config.historyColumns || allHistoryColumns).filter((col: any) => col.visible !== false)

  const batchColumns = [
    {
      title: config.inputLabel,
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
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      render: (_: unknown, record: BatchItem) => (
        <Button
          type="link"
          size="small"
          onClick={() => handleViewBatchDetail(record)}
          disabled={record.status !== 'completed' && record.status !== 'failed'}
        >
          View
        </Button>
      ),
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
          <Card title={`Generate ${config.title}`}>
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <Text strong>{config.inputLabel}</Text>
                <TextArea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={config.inputPlaceholder}
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
                disabled={!input.trim()}
                block
              >
                {loading ? 'Generating...' : 'Generate'}
              </Button>

              {config.sampleInputs.length > 0 && (
                <div style={{ marginTop: 16 }}>
                  <Text strong>Sample {config.inputLabel}s</Text>
                  <Space direction="vertical" style={{ width: '100%', marginTop: 8 }}>
                    {config.sampleInputs.map((sample, index) => (
                      <Card key={index} size="small" style={{ background: '#f9f9f9' }}>
                        <Space align="start" style={{ width: '100%', justifyContent: 'space-between' }}>
                          <Text style={{ fontSize: 13, color: '#666' }}>
                            {sample.label || sample.value}
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

              {error && <Alert message="Error" description={error} type="error" showIcon />}
            </Space>
          </Card>

          {result && (
            <Card title="Result">
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <div>
                  <Text strong>Response:</Text>
                  <Paragraph
                    style={{
                      whiteSpace: 'pre-wrap',
                      background: '#f5f5f5',
                      padding: 16,
                      borderRadius: 8,
                      marginTop: 8,
                    }}
                  >
                    {result.response_text}
                  </Paragraph>
                </div>

                {result.parsed_output && config.renderParsedOutput && (
                  <div>
                    <Text strong>Parsed Output:</Text>
                    {config.renderParsedOutput(result.parsed_output)}
                  </div>
                )}

                {result.parsed_output && !config.renderParsedOutput && (
                  <div>
                    <Text strong>Parsed Output:</Text>
                    <Paragraph>
                      <pre
                        style={{
                          background: '#e6f7ff',
                          padding: '12px',
                          borderRadius: '4px',
                          whiteSpace: 'pre-wrap',
                          wordWrap: 'break-word',
                        }}
                      >
                        {JSON.stringify(result.parsed_output, null, 2)}
                      </pre>
                    </Paragraph>
                  </div>
                )}

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
              <div>
                <Text strong>Paste JSON Array</Text>
                <Paragraph type="secondary" style={{ marginBottom: 8 }}>
                  Format: [{`"${config.inputFieldName}": "..."`}, ...]
                </Paragraph>
                <TextArea
                  value={batchJsonInput}
                  onChange={(e) => setBatchJsonInput(e.target.value)}
                  placeholder={`[{ "${config.inputFieldName}": "..." }, { "${config.inputFieldName}": "..." }]`}
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
                <Dropdown
                  menu={{
                    items: [
                      {
                        key: 'timestamp',
                        label: (
                          <Checkbox
                            checked={visibleColumns.timestamp}
                            onChange={(e) => setVisibleColumns({ ...visibleColumns, timestamp: e.target.checked })}
                          >
                            Timestamp
                          </Checkbox>
                        ),
                      },
                      {
                        key: 'document_id',
                        label: (
                          <Checkbox
                            checked={visibleColumns.document_id}
                            onChange={(e) => setVisibleColumns({ ...visibleColumns, document_id: e.target.checked })}
                          >
                            Document ID
                          </Checkbox>
                        ),
                      },
                      {
                        key: 'conversation_id',
                        label: (
                          <Checkbox
                            checked={visibleColumns.conversation_id}
                            onChange={(e) => setVisibleColumns({ ...visibleColumns, conversation_id: e.target.checked })}
                          >
                            Conversation ID
                          </Checkbox>
                        ),
                      },
                      {
                        key: 'input',
                        label: (
                          <Checkbox
                            checked={visibleColumns.input}
                            onChange={(e) => setVisibleColumns({ ...visibleColumns, input: e.target.checked })}
                          >
                            Input
                          </Checkbox>
                        ),
                      },
                      {
                        key: 'response',
                        label: (
                          <Checkbox
                            checked={visibleColumns.response}
                            onChange={(e) => setVisibleColumns({ ...visibleColumns, response: e.target.checked })}
                          >
                            Response
                          </Checkbox>
                        ),
                      },
                      {
                        key: 'tokens',
                        label: (
                          <Checkbox
                            checked={visibleColumns.tokens}
                            onChange={(e) => setVisibleColumns({ ...visibleColumns, tokens: e.target.checked })}
                          >
                            Tokens
                          </Checkbox>
                        ),
                      },
                      {
                        key: 'time',
                        label: (
                          <Checkbox
                            checked={visibleColumns.time}
                            onChange={(e) => setVisibleColumns({ ...visibleColumns, time: e.target.checked })}
                          >
                            Time (ms)
                          </Checkbox>
                        ),
                      },
                    ],
                  }}
                  trigger={['click']}
                >
                  <Tooltip title="Column Settings">
                    <Button icon={<SettingOutlined />} />
                  </Tooltip>
                </Dropdown>
              </Space>
            }
          >
            {historyError && (
              <Alert message="Error" description={historyError} type="error" showIcon style={{ marginBottom: 16 }} />
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

            <Table
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
              scroll={{ x: 'max-content' }}
            />
          </Card>
        </Space>
      ),
    },
  ]

  return (
    <>
      <Tabs defaultActiveKey="generate" items={tabItems} />

      <Modal
        title="Record Details"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={800}
      >
        {selectedRecord && (
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            <div>
              <Text strong>Document ID:</Text>
              <Text copyable style={{ marginLeft: 8 }}>{selectedRecord.id}</Text>
            </div>
            <div>
              <Text strong>Conversation ID:</Text>
              <Text copyable style={{ marginLeft: 8 }}>{selectedRecord.conversation_id || 'N/A'}</Text>
            </div>
            <div>
              <Text strong>Timestamp:</Text>
              <Text style={{ marginLeft: 8 }}>{formatTimestamp(selectedRecord.timestamp)}</Text>
            </div>
            <div>
              <Text strong>{config.inputLabel}:</Text>
              <Paragraph style={{ background: '#f5f5f5', padding: 12, borderRadius: 8, marginTop: 8, whiteSpace: 'pre-wrap', maxHeight: 200, overflow: 'auto' }}>
                {selectedRecord[config.inputFieldName as keyof SingleAgentHistoryItem] as string || 'N/A'}
              </Paragraph>
            </div>
            <div>
              <Text strong>Response:</Text>
              <Paragraph style={{ background: '#f5f5f5', padding: 12, borderRadius: 8, marginTop: 8, whiteSpace: 'pre-wrap', maxHeight: 300, overflow: 'auto' }}>
                {selectedRecord.response || selectedRecord.response_text || 'N/A'}
              </Paragraph>
            </div>
            {selectedRecord.parsed_output && (
              <div>
                <Text strong>Parsed Output:</Text>
                <pre style={{ background: '#e6f7ff', padding: 12, borderRadius: 8, marginTop: 8, whiteSpace: 'pre-wrap', maxHeight: 300, overflow: 'auto' }}>
                  {JSON.stringify(selectedRecord.parsed_output, null, 2)}
                </pre>
              </div>
            )}
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

      <Modal
        title="Batch Item Details"
        open={batchDetailModalVisible}
        onCancel={() => setBatchDetailModalVisible(false)}
        footer={null}
        width={800}
      >
        {selectedBatchItem && (
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            <div>
              <Text strong>Status:</Text>
              <Tag
                color={
                  selectedBatchItem.status === 'completed' ? 'success' :
                  selectedBatchItem.status === 'failed' ? 'error' :
                  selectedBatchItem.status === 'running' ? 'processing' : 'default'
                }
                style={{ marginLeft: 8 }}
              >
                {selectedBatchItem.status.toUpperCase()}
              </Tag>
            </div>
            <div>
              <Text strong>{config.inputLabel}:</Text>
              <Paragraph style={{ background: '#f5f5f5', padding: 12, borderRadius: 8, marginTop: 8, whiteSpace: 'pre-wrap', maxHeight: 200, overflow: 'auto' }}>
                {selectedBatchItem.input || 'N/A'}
              </Paragraph>
            </div>
            {selectedBatchItem.status === 'completed' && selectedBatchItem.result && (
              <>
                <div>
                  <Text strong>Response:</Text>
                  <Paragraph style={{ background: '#f5f5f5', padding: 12, borderRadius: 8, marginTop: 8, whiteSpace: 'pre-wrap', maxHeight: 300, overflow: 'auto' }}>
                    {selectedBatchItem.result.response_text || 'N/A'}
                  </Paragraph>
                </div>
                {selectedBatchItem.result.parsed_output && (
                  <div>
                    <Text strong>Parsed Output:</Text>
                    <pre style={{ background: '#e6f7ff', padding: 12, borderRadius: 8, marginTop: 8, whiteSpace: 'pre-wrap', maxHeight: 300, overflow: 'auto' }}>
                      {JSON.stringify(selectedBatchItem.result.parsed_output, null, 2)}
                    </pre>
                  </div>
                )}
                <Space size="large">
                  <div>
                    <Text type="secondary">Tokens: </Text>
                    <Text strong>{selectedBatchItem.result.tokens_used || 'N/A'}</Text>
                  </div>
                  <div>
                    <Text type="secondary">Time: </Text>
                    <Text strong>{Math.round(selectedBatchItem.result.time_taken_ms)} ms</Text>
                  </div>
                  <div>
                    <Text type="secondary">Model: </Text>
                    <Text strong>{selectedBatchItem.result.agent_details.model_deployment_name}</Text>
                  </div>
                  <div>
                    <Text type="secondary">Agent: </Text>
                    <Text strong>{selectedBatchItem.result.agent_details.agent_name}</Text>
                  </div>
                </Space>
              </>
            )}
            {selectedBatchItem.status === 'failed' && (
              <div>
                <Text strong>Error:</Text>
                <Paragraph style={{ background: '#fff2f0', padding: 12, borderRadius: 8, marginTop: 8, whiteSpace: 'pre-wrap', maxHeight: 200, overflow: 'auto', color: '#ff4d4f' }}>
                  {selectedBatchItem.error || 'Unknown error'}
                </Paragraph>
              </div>
            )}
          </Space>
        )}
      </Modal>
    </>
  )
}
