'use client'

import { useParams } from 'next/navigation'
import { Space } from 'antd'
import { useAgentContext } from '@/components/agents/shared/AgentContext'
import BatchProcessingSection from '@/components/agents/batch/BatchProcessingSection'

export default function AgentBatchPage() {
  const params = useParams()
  const agentId = params.agentId as string
  const { agentInfo } = useAgentContext()

  if (!agentInfo) return null

  return (
    <Space orientation="vertical" size="large" style={{ width: '100%' }}>
      <BatchProcessingSection
        agentId={agentId}
        inputLabel={agentInfo.input_label}
        inputField={agentInfo.input_field}
        sampleInputs={agentInfo.sample_inputs}
      />
    </Space>
  )
}
