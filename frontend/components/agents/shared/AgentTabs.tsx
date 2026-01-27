'use client'

import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { Menu } from 'antd'
import type { MenuProps } from 'antd'

interface AgentTabsProps {
  agentId: string
}

export default function AgentTabs({ agentId }: AgentTabsProps) {
  const pathname = usePathname()

  // Determine active key based on pathname
  let activeKey = 'generate'
  if (pathname.endsWith('/batch')) {
    activeKey = 'batch'
  } else if (pathname.endsWith('/history')) {
    activeKey = 'history'
  }

  const items: MenuProps['items'] = [
    {
      key: 'generate',
      label: <Link href={`/agents/${agentId}`}>Generate</Link>,
    },
    {
      key: 'batch',
      label: <Link href={`/agents/${agentId}/batch`}>Batch Processing</Link>,
    },
    {
      key: 'history',
      label: <Link href={`/agents/${agentId}/history`}>History</Link>,
    },
  ]

  return (
    <Menu
      mode="horizontal"
      selectedKeys={[activeKey]}
      items={items}
      style={{ marginBottom: 24 }}
    />
  )
}
