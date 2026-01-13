'use client'

import { useState } from 'react'
import { Button, Card, Input, Tabs, Table, Space, Typography, message, Spin, Alert, Tag } from 'antd'
import { LoadingOutlined, ReloadOutlined } from '@ant-design/icons'
import PageLayout from '@/components/PageLayout'
import { apiClient, TranscriptParserResponse, BrowseResponse } from '@/lib/api-client'

const { TextArea } = Input
const { Title, Paragraph, Text } = Typography

export default function TranscriptParserPage() {
  const [transcript, setTranscript] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<TranscriptParserResponse | null>(null)
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
    const response = await apiClient.browseTranscripts(page, pageSize)
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
    
    const response = await apiClient.deleteTranscripts(ids)
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

  const sampleTranscripts = [
    "Customer: Hi, I've been trying to upgrade my phone plan but the website keeps giving me errors. Rep: I'm sorry about that. Let me look into this for you. When did you first encounter the error? Customer: This morning, around 10 AM. I really need this done today. Rep: I understand your urgency. I'm checking now... Ah, I found the issue. Let me process this manually for you.",
    "Customer: I just received my order but the device is damaged. I'm really frustrated! Rep: I sincerely apologize for the inconvenience. Can you describe the damage? Customer: The screen has cracks and it won't turn on. This is unacceptable! Rep: You're absolutely right. I'll process a replacement immediately at no cost to you.",
    "Customer: Could you help me understand how to access my account balance? Rep: Of course! I'd be happy to help. You can log in to your account... Customer: Okay, got it. Thank you for walking me through this. Rep: You're welcome! Is there anything else I can assist with? Customer: No, that's all. Have a good day! Rep: You too!"
  ]

  const handleSubmit = async () => {
    if (!transcript.trim()) {
      message.warning('Please enter a transcript')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    const response = await apiClient.parseTranscript(transcript)
    setLoading(false)

    if (response.data) {
      setResult(response.data)
      message.success('Transcript parsed successfully')
    } else if (response.error) {
      setError(response.error)
      message.error('Failed to parse transcript')
    }
  }

  const handleClear = () => {
    setTranscript('')
    setResult(null)
    setError('')
  }

  const handleLoadSample = (index: number) => {
    setTranscript(sampleTranscripts[index])
    setResult(null)
    setError('')
  }

  const renderParsedOutput = () => {
    if (!result?.parsed_output) return null
    
    const output = result.parsed_output as any
    return (
      <Card size="small" style={{ marginTop: 16 }}>
        <Title level={5}>Parsed Output</Title>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>Intent:</Text>
            <Tag color="blue" style={{ marginLeft: 8 }}>{output.intent || '(empty)'}</Tag>
          </div>
          <div>
            <Text strong>Subject:</Text>
            <Tag color="green" style={{ marginLeft: 8 }}>{output.subject || '(empty)'}</Tag>
          </div>
          <div>
            <Text strong>Sentiment:</Text>
            <Tag color="orange" style={{ marginLeft: 8 }}>{output.sentiment || '(empty)'}</Tag>
          </div>
        </Space>
      </Card>
    )
  }

  const historyColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 200,
      ellipsis: true,
      render: (text: string) => <Text code>{text.substring(0, 50)}...</Text>,
    },
    {
      title: 'Transcript Preview',
      dataIndex: 'transcript',
      key: 'transcript',
      ellipsis: true,
      render: (text: string) => text.substring(0, 100) + '...',
    },
    {
      title: 'Tokens Used',
      dataIndex: ['agent_details', 'tokens_used'],
      key: 'tokens_used',
      width: 120,
      align: 'right' as const,
    },
    {
      title: 'Time (ms)',
      dataIndex: 'time_taken_ms',
      key: 'time_taken_ms',
      width: 100,
      align: 'right' as const,
      render: (ms: number) => ms.toFixed(2),
    },
  ]

  const rowSelection = {
    selectedRowKeys,
    onChange: (keys: React.Key[]) => setSelectedRowKeys(keys),
  }

  const tabItems = [
    {
      key: '1',
      label: 'Parse Transcript',
      children: (
        <div style={{ display: 'flex', gap: 16 }}>
          <div style={{ flex: 1 }}>
            <Card>
              <Title level={5}>Transcript</Title>
              <Paragraph>
                Enter a customer-representative conversation to extract intent, subject, and sentiment.
              </Paragraph>
              
              <TextArea
                placeholder="Paste or type the transcript here..."
                rows={8}
                value={transcript}
                onChange={(e) => setTranscript(e.target.value)}
                style={{ marginBottom: 16 }}
              />

              <div style={{ marginBottom: 16 }}>
                <Title level={5} style={{ marginBottom: 8 }}>Sample Transcripts</Title>
                <Space wrap>
                  {sampleTranscripts.map((_, idx) => (
                    <Button
                      key={idx}
                      size="small"
                      onClick={() => handleLoadSample(idx)}
                    >
                      Sample {idx + 1}
                    </Button>
                  ))}
                </Space>
              </div>

              <Space>
                <Button
                  type="primary"
                  onClick={handleSubmit}
                  loading={loading}
                  icon={loading ? <LoadingOutlined /> : undefined}
                >
                  Parse Transcript
                </Button>
                <Button onClick={handleClear}>Clear</Button>
              </Space>

              {error && (
                <Alert
                  message="Error"
                  description={error}
                  type="error"
                  style={{ marginTop: 16 }}
                  showIcon
                />
              )}
            </Card>
          </div>

          <div style={{ width: 350 }}>
            {loading && (
              <Card>
                <div style={{ textAlign: 'center', padding: 40 }}>
                  <Spin indicator={<LoadingOutlined style={{ fontSize: 48 }} />} />
                </div>
              </Card>
            )}

            {result && !loading && (
              <Card>
                <Title level={5}>Result</Title>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <Text type="secondary">Response Text</Text>
                    <div style={{ background: '#f5f5f5', padding: 8, borderRadius: 4, marginTop: 4 }}>
                      <Text code>{result.response_text}</Text>
                    </div>
                  </div>

                  {renderParsedOutput()}

                  <div style={{ borderTop: '1px solid #f0f0f0', paddingTop: 12 }}>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      Tokens: {result.tokens_used || 'N/A'} | Time: {result.time_taken_ms.toFixed(2)}ms
                    </Text>
                  </div>
                </Space>
              </Card>
            )}
          </div>
        </div>
      ),
    },
    {
      key: '2',
      label: 'History',
      children: (
        <div>
          <div style={{ marginBottom: 16 }}>
            <Space>
              <Button
                type="primary"
                onClick={() => loadHistory(1)}
                loading={historyLoading}
                icon={<ReloadOutlined />}
              >
                Refresh
              </Button>
              <Button
                danger
                onClick={handleDeleteSelected}
                loading={deleteLoading}
                disabled={selectedRowKeys.length === 0}
              >
                Delete Selected ({selectedRowKeys.length})
              </Button>
            </Space>
          </div>

          {historyError && (
            <Alert
              message="Error"
              description={historyError}
              type="error"
              style={{ marginBottom: 16 }}
              showIcon
            />
          )}

          <Spin spinning={historyLoading}>
            <Table
              columns={historyColumns}
              dataSource={historyData?.items || []}
              rowKey="id"
              rowSelection={rowSelection}
              pagination={{
                current: historyData?.page || 1,
                pageSize: historyData?.page_size || 10,
                total: historyData?.total_count || 0,
                onChange: (page, pageSize) => loadHistory(page, pageSize),
              }}
              scroll={{ x: 800 }}
            />
          </Spin>
        </div>
      ),
    },
  ]

  return (
    <PageLayout
      title="Transcript Parser"
      description="Parse customer-representative transcripts to extract intent, subject, and sentiment"
    >
      <Tabs items={tabItems} defaultActiveKey="1" />
    </PageLayout>
  )
}
