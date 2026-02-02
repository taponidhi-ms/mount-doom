'use client'

import { useState, useCallback, useEffect } from 'react'
import {
  Card,
  Table,
  Space,
  Button,
  Tooltip,
  Select,
  Popconfirm,
  Alert,
  Dropdown,
  Checkbox,
  Typography,
  Tag,
  message,
} from 'antd'
import {
  ReloadOutlined,
  DownloadOutlined,
  DeleteOutlined,
  SortAscendingOutlined,
  SortDescendingOutlined,
  SettingOutlined,
} from '@ant-design/icons'
import { apiClient } from '@/lib/api-client'
import type { BrowseResponse, AgentHistoryItem } from '@/lib/api-client'
import { useTimezone } from '@/lib/timezone-context'
import AgentResultModal from '../result/AgentResultModal'

const { Text } = Typography

interface AgentHistoryTableProps {
  agentId: string
  inputLabel: string
  inputField: string
}

export default function AgentHistoryTable({
  agentId,
  inputLabel,
  inputField,
}: AgentHistoryTableProps) {
  const { formatTimestamp } = useTimezone()

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
  const [selectedVersionInstructions, setSelectedVersionInstructions] = useState<string | null>(
    null
  )

  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [selectedRecord, setSelectedRecord] = useState<AgentHistoryItem | null>(null)

  const [visibleColumns, setVisibleColumns] = useState<Record<string, boolean>>({
    timestamp: true,
    document_id: false,
    conversation_id: false,
    input: true,
    response: true,
    prompt_category: true,  // Visible by default
    prompt_tags: true,      // Visible by default
    tokens: true,
    time: true,
    actions: true,
  })

  const loadHistory = useCallback(
    async (page: number = 1, size: number = pageSize) => {
      setHistoryLoading(true)
      setHistoryError('')
      const response = await apiClient.browseAgentHistory(
        agentId,
        page,
        size,
        orderBy,
        orderDirection
      )
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
    },
    [agentId, orderBy, orderDirection, pageSize]
  )

  // Auto-load history on mount
  useEffect(() => {
    loadHistory(1)
  }, [loadHistory])

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

  const handleViewDetail = (record: AgentHistoryItem) => {
    setSelectedRecord(record)
    setDetailModalVisible(true)
  }

  const allHistoryColumns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (text: string) => formatTimestamp(text),
      width: 250,
      visible: visibleColumns.timestamp,
    },
    {
      title: 'Document ID',
      dataIndex: 'id',
      key: 'document_id',
      width: 220,
      ellipsis: { showTitle: false },
      visible: visibleColumns.document_id,
      render: (text: string) => (
        <Tooltip title={text} overlayStyle={{ maxWidth: 500 }}>
          <Text copyable={{ text }}>{text}</Text>
        </Tooltip>
      ),
    },
    {
      title: 'Conversation ID',
      dataIndex: 'conversation_id',
      key: 'conversation_id',
      width: 220,
      ellipsis: { showTitle: false },
      visible: visibleColumns.conversation_id,
      render: (text: string) =>
        text ? (
          <Tooltip title={text} overlayStyle={{ maxWidth: 500 }}>
            <Text copyable={{ text }}>{text}</Text>
          </Tooltip>
        ) : (
          'N/A'
        ),
    },
    {
      title: inputLabel,
      dataIndex: inputField,
      key: 'input',
      width: 250,
      ellipsis: { showTitle: false },
      visible: visibleColumns.input,
      render: (text: string) => (
        <Tooltip title={text} overlayStyle={{ maxWidth: 500 }}>
          <div style={{ maxWidth: '100%', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {text || 'N/A'}
          </div>
        </Tooltip>
      ),
    },
    {
      title: 'Response Preview',
      dataIndex: 'response',
      key: 'response',
      width: 250,
      ellipsis: { showTitle: false },
      visible: visibleColumns.response,
      render: (text: string) => {
        const displayText = text
          ? text.length > 100
            ? text.substring(0, 100) + '...'
            : text
          : 'N/A'
        return (
          <Tooltip title={text} overlayStyle={{ maxWidth: 500 }}>
            <div style={{ maxWidth: '100%', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {displayText}
            </div>
          </Tooltip>
        )
      },
    },
    {
      title: 'Category',
      dataIndex: 'prompt_category',
      key: 'prompt_category',
      width: 120,
      visible: visibleColumns.prompt_category,
      render: (category: string) => category ? <Tag color="blue">{category}</Tag> : '-',
    },
    {
      title: 'Tags',
      dataIndex: 'prompt_tags',
      key: 'prompt_tags',
      width: 200,
      ellipsis: { showTitle: false },
      visible: visibleColumns.prompt_tags,
      render: (tags: string[]) => {
        if (!tags || tags.length === 0) return '-'
        return (
          <Space size={[0, 4]} wrap>
            {tags.map((tag, i) => (
              <Tag key={i} color="green">{tag}</Tag>
            ))}
          </Space>
        )
      },
    },
    {
      title: 'Tokens',
      dataIndex: 'tokens_used',
      key: 'tokens',
      width: 100,
      visible: visibleColumns.tokens,
      render: (value: number) => value || 'N/A',
    },
    {
      title: 'Time (ms)',
      dataIndex: 'time_taken_ms',
      key: 'time',
      width: 120,
      visible: visibleColumns.time,
      render: (value: number) => (value ? Math.round(value) : 'N/A'),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      visible: visibleColumns.actions,
      render: (_: unknown, record: AgentHistoryItem) => (
        <Button type="link" size="small" onClick={() => handleViewDetail(record)}>
          View
        </Button>
      ),
    },
  ]

  const historyColumns = allHistoryColumns.filter((col) => col.visible)

  const rowSelection = {
    selectedRowKeys,
    onChange: (keys: React.Key[]) => setSelectedRowKeys(keys),
  }

  return (
    <>
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
                options={[...agentVersions.map((v) => ({ value: v, label: `Version ${v}` }))]}
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
                icon={
                  orderDirection === 'DESC' ? <SortDescendingOutlined /> : <SortAscendingOutlined />
                }
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
                        onChange={(e) =>
                          setVisibleColumns({ ...visibleColumns, timestamp: e.target.checked })
                        }
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
                        onChange={(e) =>
                          setVisibleColumns({ ...visibleColumns, document_id: e.target.checked })
                        }
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
                        onChange={(e) =>
                          setVisibleColumns({
                            ...visibleColumns,
                            conversation_id: e.target.checked,
                          })
                        }
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
                        onChange={(e) =>
                          setVisibleColumns({ ...visibleColumns, input: e.target.checked })
                        }
                      >
                        {inputLabel}
                      </Checkbox>
                    ),
                  },
                  {
                    key: 'response',
                    label: (
                      <Checkbox
                        checked={visibleColumns.response}
                        onChange={(e) =>
                          setVisibleColumns({ ...visibleColumns, response: e.target.checked })
                        }
                      >
                        Response Preview
                      </Checkbox>
                    ),
                  },
                  {
                    key: 'prompt_category',
                    label: (
                      <Checkbox
                        checked={visibleColumns.prompt_category}
                        onChange={(e) =>
                          setVisibleColumns({
                            ...visibleColumns,
                            prompt_category: e.target.checked,
                          })
                        }
                      >
                        Category
                      </Checkbox>
                    ),
                  },
                  {
                    key: 'prompt_tags',
                    label: (
                      <Checkbox
                        checked={visibleColumns.prompt_tags}
                        onChange={(e) =>
                          setVisibleColumns({ ...visibleColumns, prompt_tags: e.target.checked })
                        }
                      >
                        Tags
                      </Checkbox>
                    ),
                  },
                  {
                    key: 'tokens',
                    label: (
                      <Checkbox
                        checked={visibleColumns.tokens}
                        onChange={(e) =>
                          setVisibleColumns({ ...visibleColumns, tokens: e.target.checked })
                        }
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
                        onChange={(e) =>
                          setVisibleColumns({ ...visibleColumns, time: e.target.checked })
                        }
                      >
                        Time (ms)
                      </Checkbox>
                    ),
                  },
                  {
                    key: 'actions',
                    label: (
                      <Checkbox
                        checked={visibleColumns.actions}
                        onChange={(e) =>
                          setVisibleColumns({ ...visibleColumns, actions: e.target.checked })
                        }
                      >
                        Actions
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
          <Alert
            message="Error"
            description={historyError}
            type="error"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}

        {selectedVersionInstructions && (
          <Card
            size="small"
            title={`Agent Version ${selectedAgentVersion} Instructions`}
            style={{ marginBottom: 16, background: '#f9f9f9' }}
          >
            <pre
              style={{
                whiteSpace: 'pre-wrap',
                wordWrap: 'break-word',
                maxHeight: 300,
                overflow: 'auto',
                fontSize: 12,
                margin: 0,
              }}
            >
              {selectedVersionInstructions}
            </pre>
          </Card>
        )}

        {(historyData || historyLoading) && (
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
        )}

        {(historyData || historyLoading) && (
          <Table
            dataSource={
              selectedAgentVersion
                ? (historyData?.items || []).filter(
                    (item: any) => item.agent_version === selectedAgentVersion
                  )
                : historyData?.items || []
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

      <AgentResultModal
        visible={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        record={selectedRecord}
        inputLabel={inputLabel}
        inputField={inputField}
      />
    </>
  )
}
