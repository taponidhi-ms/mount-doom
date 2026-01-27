'use client'

import { useState, useEffect, ReactNode } from 'react'
import { useParams } from 'next/navigation'
import { Spin, Alert } from 'antd'
import PageLayout from '@/components/PageLayout'
import AgentTabs from '@/components/agents/shared/AgentTabs'
import { AgentProvider } from '@/components/agents/shared/AgentContext'
import { apiClient } from '@/lib/api-client'
import type { AgentInfo } from '@/lib/api-client'

interface AgentLayoutProps {
  children: ReactNode
}

export default function AgentLayout({ children }: AgentLayoutProps) {
  const params = useParams()
  const agentId = params.agentId as string

  const [agentInfo, setAgentInfo] = useState<AgentInfo | null>(null)
  const [loadingAgent, setLoadingAgent] = useState(true)
  const [agentError, setAgentError] = useState('')

  useEffect(() => {
    const loadAgent = async () => {
      setLoadingAgent(true)
      setAgentError('')
      const response = await apiClient.getAgent(agentId)
      setLoadingAgent(false)

      if (response.data) {
        setAgentInfo(response.data)
      } else if (response.error) {
        setAgentError(response.error)
      }
    }

    loadAgent()
  }, [agentId])

  if (loadingAgent) {
    return (
      <PageLayout title="Loading Agent...">
        <div style={{ textAlign: 'center', padding: 100 }}>
          <Spin size="large" />
        </div>
      </PageLayout>
    )
  }

  if (agentError || !agentInfo) {
    return (
      <PageLayout title="Agent Error">
        <Alert
          message="Error"
          description={agentError || 'Failed to load agent information'}
          type="error"
          showIcon
        />
      </PageLayout>
    )
  }

  return (
    <AgentProvider value={{ agentInfo, loadingAgent, agentError }}>
      <PageLayout title={agentInfo.display_name} description={agentInfo.description}>
        <AgentTabs agentId={agentId} />
        {children}
      </PageLayout>
    </AgentProvider>
  )
}
