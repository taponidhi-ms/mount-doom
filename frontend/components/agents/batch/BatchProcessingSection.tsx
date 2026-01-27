'use client'

import { useState } from 'react'
import { Card, Space, Typography, Button, Input, Select, Progress, Table, Tag, message } from 'antd'
import { apiClient } from '@/lib/api-client'
import type { AgentInvokeResponse } from '@/lib/api-client'

const { TextArea } = Input
const { Text, Paragraph } = Typography

interface BatchItem {
  key: string
  input: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  result?: AgentInvokeResponse
  error?: string
}

interface BatchProcessingSectionProps {
  agentId: string
  inputLabel: string
  inputField: string
  onBatchComplete?: () => void
}

export default function BatchProcessingSection({
  agentId,
  inputLabel,
  inputField,
  onBatchComplete,
}: BatchProcessingSectionProps) {
  const [batchItems, setBatchItems] = useState<BatchItem[]>([])
  const [batchLoading, setBatchLoading] = useState(false)
  const [batchProgress, setBatchProgress] = useState(0)
  const [currentBatchIndex, setCurrentBatchIndex] = useState(-1)
  const [batchJsonInput, setBatchJsonInput] = useState('')
  const [stopBatchRequested, setStopBatchRequested] = useState(false)
  const [batchDelay, setBatchDelay] = useState(5)

  const loadBatchItemsFromText = () => {
    if (!batchJsonInput.trim()) {
      message.warning('Paste JSON to load batch items.')
      return
    }

    try {
      const json = JSON.parse(batchJsonInput)

      if (!Array.isArray(json)) {
        message.error(`Invalid JSON format. Expected an array of objects with "${inputField}" field.`)
        return
      }

      const parsedItems = json
        .map((item: unknown, index: number) => {
          if (typeof item !== 'object' || item === null || !(inputField in item)) {
            return null
          }
          const inputText = (item as Record<string, unknown>)[inputField]
          if (typeof inputText !== 'string') {
            return null
          }
          return {
            key: `batch-${index}-${Date.now()}`,
            input: inputText,
            status: 'pending' as const,
          }
        })
        .filter(
          (item): item is { key: string; input: string; status: 'pending' } =>
            item !== null && item.input.trim() !== ''
        )

      const items: BatchItem[] = parsedItems

      if (items.length === 0) {
        message.error(`No valid objects with "${inputField}" field found in JSON.`)
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

    if (onBatchComplete) {
      onBatchComplete()
    }
  }

  const handleStopBatch = () => {
    setStopBatchRequested(true)
  }

  const batchColumns = [
    {
      title: inputLabel,
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

  return (
    <Card title="Batch Processing">
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <div>
          <Text strong>Paste JSON Array</Text>
          <Paragraph type="secondary" style={{ marginBottom: 8 }}>
            Format: [{`"${inputField}": "..."`}, ...]
          </Paragraph>
          <TextArea
            value={batchJsonInput}
            onChange={(e) => setBatchJsonInput(e.target.value)}
            placeholder={`[{ "${inputField}": "..." }, { "${inputField}": "..." }]`}
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

            {batchLoading && <Progress percent={batchProgress} status="active" />}

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
  )
}
