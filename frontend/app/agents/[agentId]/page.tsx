'use client'

import { useState } from 'react'
import { useParams } from 'next/navigation'
import { Button, Card, Input, Space, Typography, message, Alert, Form, Select } from 'antd'
import { BulbOutlined } from '@ant-design/icons'
import { useAgentContext } from '@/components/agents/shared/AgentContext'
import AgentInstructionsCard from '@/components/agents/instructions/AgentInstructionsCard'
import AgentResultCard from '@/components/agents/result/AgentResultCard'
import SampleInputsModal from '@/components/agents/sample-inputs/SampleInputsModal'
import { apiClient } from '@/lib/api-client'
import type { AgentInvokeResponse } from '@/lib/api-client'

const { TextArea } = Input
const { Text } = Typography

export default function AgentGeneratePage() {
  const params = useParams()
  const agentId = params.agentId as string
  const { agentInfo } = useAgentContext()

  const [input, setInput] = useState('')
  const [promptCategory, setPromptCategory] = useState<string>('')
  const [promptTags, setPromptTags] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AgentInvokeResponse | null>(null)
  const [error, setError] = useState('')
  const [showSamplesModal, setShowSamplesModal] = useState(false)

  const handleSampleSelect = (value: string, category?: string, tags?: string[]) => {
    setInput(value)
    setPromptCategory(category || '')
    setPromptTags(tags || [])
  }

  const handleSubmit = async () => {
    if (!input.trim()) {
      message.warning(`Please enter ${agentInfo?.input_label?.toLowerCase() || 'input'}`)
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    const response = await apiClient.invokeAgent(
      agentId,
      input,
      promptCategory || undefined,
      promptTags.length > 0 ? promptTags : undefined
    )
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
    <Space orientation="vertical" size="large" style={{ width: '100%' }}>
      <AgentInstructionsCard instructions={agentInfo.instructions} />

      <Card title={`Generate with ${agentInfo.display_name}`}>
        <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
          {/* Main Input */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <Text strong>{agentInfo.input_label}</Text>
              {agentInfo.sample_inputs && agentInfo.sample_inputs.length > 0 && (
                <Button
                  type="default"
                  icon={<BulbOutlined />}
                  size="small"
                  onClick={() => setShowSamplesModal(true)}
                >
                  Try Sample Input
                </Button>
              )}
            </div>
            <TextArea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={agentInfo.input_placeholder}
              rows={6}
              disabled={loading}
            />
          </div>

          {/* Category Input (Optional) */}
          <Form.Item
            label="Category (Optional)"
            help="Categorize this prompt (e.g., Valid, Invalid, Edge Case)"
            style={{ marginBottom: 0 }}
          >
            <Input
              value={promptCategory}
              onChange={(e) => setPromptCategory(e.target.value)}
              placeholder="Enter category..."
              disabled={loading}
            />
          </Form.Item>

          {/* Tags Input (Optional) */}
          <Form.Item
            label="Tags (Optional)"
            help="Add tags to organize this prompt"
            style={{ marginBottom: 0 }}
          >
            <Select
              mode="tags"
              style={{ width: '100%' }}
              value={promptTags}
              onChange={setPromptTags}
              placeholder="Enter tags and press Enter..."
              tokenSeparators={[',']}
              disabled={loading}
            />
          </Form.Item>

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

      {agentInfo.sample_inputs && (
        <SampleInputsModal
          open={showSamplesModal}
          onClose={() => setShowSamplesModal(false)}
          sampleInputs={agentInfo.sample_inputs}
          onSelect={handleSampleSelect}
          inputLabel={agentInfo.input_label}
        />
      )}
    </Space>
  )
}
