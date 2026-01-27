'use client'

import { useParams } from 'next/navigation'
import { Space } from 'antd'
import { useAgentContext } from '@/components/agents/shared/AgentContext'
import AgentHistoryTable from '@/components/agents/history/AgentHistoryTable'

export default function AgentHistoryPage() {
  const params = useParams()
  const agentId = params.agentId as string
  const { agentInfo } = useAgentContext()

  if (!agentInfo) return null

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <AgentHistoryTable
        agentId={agentId}
        inputLabel={agentInfo.input_label}
        inputField={agentInfo.input_field}
      />
    </Space>
  )
}
