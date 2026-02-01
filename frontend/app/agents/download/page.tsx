'use client'

import { useState, useEffect, useMemo } from 'react'
import { Table, Button, Space, Alert, message } from 'antd'
import type { TableColumnsType, TableProps } from 'antd'
import { DownloadOutlined } from '@ant-design/icons'
import PageLayout from '@/components/PageLayout'
import { apiClient } from '@/lib/api-client'
import type { AgentVersionInfo, AgentVersionSelection } from '@/lib/types'

export default function MultiAgentDownloadPage() {
  const [agentVersions, setAgentVersions] = useState<AgentVersionInfo[]>([])
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
  const [loading, setLoading] = useState(false)
  const [downloading, setDownloading] = useState(false)

  // Fetch agent versions on mount
  useEffect(() => {
    fetchAgentVersions()
  }, [])

  const fetchAgentVersions = async () => {
    setLoading(true)
    try {
      const response = await apiClient.listAgentVersions()
      if (response.data) {
        setAgentVersions(response.data)
      } else if (response.error) {
        message.error(`Failed to load agent versions: ${response.error}`)
      }
    } catch (error) {
      message.error('Failed to load agent versions')
      console.error('Error fetching agent versions:', error)
    } finally {
      setLoading(false)
    }
  }

  // Calculate total conversations for selected versions
  const totalConversations = useMemo(() => {
    return agentVersions
      .filter((av) => selectedRowKeys.includes(`${av.agent_id}::${av.version}`))
      .reduce((sum, av) => sum + av.conversation_count, 0)
  }, [selectedRowKeys, agentVersions])

  // Handle selection changes
  const onSelectChange: TableProps<AgentVersionInfo>['rowSelection'] = {
    selectedRowKeys,
    onChange: (newSelectedRowKeys) => {
      setSelectedRowKeys(newSelectedRowKeys)
    },
  }

  // Handle download
  const handleDownload = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('Please select at least one agent version')
      return
    }

    setDownloading(true)
    try {
      // Parse selections from row keys
      const selections: AgentVersionSelection[] = selectedRowKeys.map((key) => {
        const [agent_id, version] = (key as string).split('::')
        return { agent_id, version }
      })

      const response = await apiClient.downloadMultiAgent(selections)

      if (response.data) {
        // Create blob and trigger download
        const blob = response.data
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url

        // Generate filename with timestamp
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
        link.download = `multi_agent_evals_${timestamp}.json`

        document.body.appendChild(link)
        link.click()

        // Cleanup
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)

        message.success(`Downloaded ${totalConversations} conversations`)
      } else if (response.error) {
        message.error(`Download failed: ${response.error}`)
      }
    } catch (error) {
      message.error('Download failed')
      console.error('Error downloading:', error)
    } finally {
      setDownloading(false)
    }
  }

  // Table columns
  const columns: TableColumnsType<AgentVersionInfo> = [
    {
      title: 'Agent',
      dataIndex: 'agent_name',
      key: 'agent_name',
      width: 200,
    },
    {
      title: 'Scenario Name',
      dataIndex: 'scenario_name',
      key: 'scenario_name',
      width: 250,
    },
    {
      title: 'Version',
      dataIndex: 'version',
      key: 'version',
      width: 120,
    },
    {
      title: 'Conversations',
      dataIndex: 'conversation_count',
      key: 'conversation_count',
      width: 120,
      align: 'right',
    },
  ]

  return (
    <PageLayout
      title="Multi-Agent Downloads"
      description="Download conversations from multiple agents and versions in eval format"
    >
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Alert
          message={
            selectedRowKeys.length > 0
              ? `${selectedRowKeys.length} version${selectedRowKeys.length > 1 ? 's' : ''} selected, ${totalConversations} conversation${totalConversations !== 1 ? 's' : ''} total`
              : 'Select agent versions to download'
          }
          type={selectedRowKeys.length > 0 ? 'info' : 'warning'}
          showIcon
        />

        <Table<AgentVersionInfo>
          dataSource={agentVersions}
          columns={columns}
          rowKey={(record) => `${record.agent_id}::${record.version}`}
          rowSelection={onSelectChange}
          loading={loading}
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} versions`,
          }}
        />

        <Button
          type="primary"
          icon={<DownloadOutlined />}
          onClick={handleDownload}
          disabled={selectedRowKeys.length === 0}
          loading={downloading}
          size="large"
        >
          Download Selected ({totalConversations} conversation{totalConversations !== 1 ? 's' : ''})
        </Button>
      </Space>
    </PageLayout>
  )
}
