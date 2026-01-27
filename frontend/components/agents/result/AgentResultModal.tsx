'use client'

import { useState } from 'react'
import { Modal, Space, Typography, Alert, Segmented } from 'antd'
import type { AgentInvokeResponse, AgentHistoryItem } from '@/lib/api-client'
import { useTimezone } from '@/lib/timezone-context'

const { Text, Paragraph } = Typography

interface AgentResultModalProps {
  visible: boolean
  onCancel: () => void
  record: AgentHistoryItem | null
  inputLabel: string
  inputField: string
}

export default function AgentResultModal({
  visible,
  onCancel,
  record,
  inputLabel,
  inputField,
}: AgentResultModalProps) {
  const { formatTimestamp } = useTimezone()
  const [viewMode, setViewMode] = useState<'text' | 'json'>('text')

  const tryParseJSON = (text: string): { isValid: boolean; parsed?: any } => {
    try {
      const parsed = JSON.parse(text)
      return { isValid: true, parsed }
    } catch {
      return { isValid: false }
    }
  }

  if (!record) return null

  const responseText = record.response || record.response_text || 'N/A'
  const jsonCheck = tryParseJSON(responseText)

  return (
    <Modal
      title="Record Details"
      open={visible}
      onCancel={onCancel}
      footer={null}
      width={800}
      afterClose={() => setViewMode('text')}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <div>
          <Text strong>ID:</Text>
          <Text copyable style={{ marginLeft: 8 }}>
            {record.id}
          </Text>
        </div>

        <div>
          <Text strong>Timestamp:</Text>
          <Text style={{ marginLeft: 8 }}>{formatTimestamp(record.timestamp)}</Text>
        </div>

        <div>
          <Text strong>{inputLabel}:</Text>
          <Paragraph
            style={{
              background: '#f5f5f5',
              padding: 12,
              borderRadius: 8,
              marginTop: 8,
            }}
          >
            {(record[inputField as keyof AgentHistoryItem] as string) || 'N/A'}
          </Paragraph>
        </div>

        <div>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: 8,
            }}
          >
            <Text strong>Response:</Text>
            <Segmented
              options={['Plain Text', 'JSON']}
              value={viewMode === 'text' ? 'Plain Text' : 'JSON'}
              onChange={(value) => setViewMode(value === 'JSON' ? 'json' : 'text')}
              size="small"
            />
          </div>

          {viewMode === 'json' ? (
            jsonCheck.isValid ? (
              <pre
                style={{
                  background: '#e6f7ff',
                  padding: 12,
                  borderRadius: 8,
                  whiteSpace: 'pre-wrap',
                  wordWrap: 'break-word',
                  marginTop: 0,
                  maxHeight: 500,
                  overflow: 'auto',
                }}
              >
                {JSON.stringify(jsonCheck.parsed, null, 2)}
              </pre>
            ) : (
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
                    background: '#f5f5f5',
                    padding: 12,
                    borderRadius: 8,
                    marginTop: 0,
                    whiteSpace: 'pre-wrap',
                    maxHeight: 500,
                    overflow: 'auto',
                  }}
                >
                  {responseText}
                </Paragraph>
              </>
            )
          ) : (
            <Paragraph
              style={{
                background: '#f5f5f5',
                padding: 12,
                borderRadius: 8,
                marginTop: 0,
                whiteSpace: 'pre-wrap',
                maxHeight: 500,
                overflow: 'auto',
              }}
            >
              {responseText}
            </Paragraph>
          )}
        </div>

        <Space size="large" wrap>
          <div>
            <Text type="secondary">Tokens: </Text>
            <Text strong>{record.tokens_used || 'N/A'}</Text>
          </div>
          <div>
            <Text type="secondary">Time: </Text>
            <Text strong>
              {record.time_taken_ms ? Math.round(record.time_taken_ms) + ' ms' : 'N/A'}
            </Text>
          </div>
          {record.agent_version && (
            <div>
              <Text type="secondary">Agent Version: </Text>
              <Text strong>{record.agent_version}</Text>
            </div>
          )}
        </Space>
      </Space>
    </Modal>
  )
}
