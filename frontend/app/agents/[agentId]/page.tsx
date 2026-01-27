'use client'

import { useState } from 'react'
import { useParams } from 'next/navigation'
import { Button, Card, Input, Space, Typography, message, Alert } from 'antd'
import { useAgentContext } from '@/components/agents/shared/AgentContext'
import AgentInstructionsCard from '@/components/agents/instructions/AgentInstructionsCard'
import AgentResultCard from '@/components/agents/result/AgentResultCard'
import { apiClient } from '@/lib/api-client'
import type { AgentInvokeResponse } from '@/lib/api-client'

const { TextArea } = Input
const { Text } = Typography

export default function AgentGeneratePage() {
  const params = useParams()
  const agentId = params.agentId as string
  const { agentInfo } = useAgentContext()

  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AgentInvokeResponse | null>(null)
  const [error, setError] = useState('')

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
    } else if (response.error) {
      setError(response.error)
      message.error('Generation failed')
    }
  }

  if (!agentInfo) return null

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <AgentInstructionsCard instructions={agentInfo.instructions} />

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

          {agentInfo.sample_inputs && agentInfo.sample_inputs.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <Text strong>Sample {agentInfo.input_label}s</Text>
              <Space direction="vertical" style={{ width: '100%', marginTop: 8 }}>
                {agentInfo.sample_inputs.map((sample, index) => (
                  <Card key={index} size="small" style={{ background: '#f9f9f9' }}>
                    <Space
                      align="start"
                      style={{ width: '100%', justifyContent: 'space-between' }}
                    >
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

      {result && <AgentResultCard result={result} />}
    </Space>
  )
}
