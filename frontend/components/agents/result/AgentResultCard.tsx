'use client'

import { useState } from 'react'
import { Card, Space, Typography, Segmented, Alert } from 'antd'
import type { AgentInvokeResponse } from '@/lib/api-client'

const { Text, Paragraph } = Typography

interface AgentResultCardProps {
  result: AgentInvokeResponse
}

export default function AgentResultCard({ result }: AgentResultCardProps) {
  const [viewMode, setViewMode] = useState<'text' | 'json'>('text')

  const tryParseJSON = (text: string): { isValid: boolean; parsed?: any } => {
    try {
      const parsed = JSON.parse(text)
      return { isValid: true, parsed }
    } catch {
      return { isValid: false }
    }
  }

  const jsonCheck = tryParseJSON(result.response_text)

  return (
    <Card title="Result">
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
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
                  padding: 16,
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
                    whiteSpace: 'pre-wrap',
                    background: '#f5f5f5',
                    padding: 16,
                    borderRadius: 8,
                    marginTop: 0,
                    maxHeight: 500,
                    overflow: 'auto',
                  }}
                >
                  {result.response_text}
                </Paragraph>
              </>
            )
          ) : (
            <Paragraph
              style={{
                whiteSpace: 'pre-wrap',
                background: '#f5f5f5',
                padding: 16,
                borderRadius: 8,
                marginTop: 0,
                maxHeight: 500,
                overflow: 'auto',
              }}
            >
              {result.response_text}
            </Paragraph>
          )}
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
            <Text strong>{result.agent_details?.model_deployment_name || 'N/A'}</Text>
          </div>
          <div>
            <Text type="secondary">Agent: </Text>
            <Text strong>{result.agent_details?.agent_name || 'N/A'}</Text>
          </div>
        </Space>
      </Space>
    </Card>
  )
}
