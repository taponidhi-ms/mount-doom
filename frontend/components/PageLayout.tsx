'use client'

import { ReactNode, useState, useEffect } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import {
  HomeOutlined,
  UsergroupAddOutlined,
  UserAddOutlined,
  MessageOutlined,
  CommentOutlined,
  FileSearchOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  RobotOutlined,
  BranchesOutlined,
  GlobalOutlined,
} from '@ant-design/icons'
import { Button, Typography, Layout, Menu, theme, Select, Space, Tooltip } from 'antd'
import type { MenuProps } from 'antd'
import { useTimezone, type TimezoneOption } from '@/lib/timezone-context'
import { apiClient, type AgentInfo } from '@/lib/api-client'

const { Title, Text } = Typography
const { Header, Content, Footer, Sider } = Layout

type MenuItem = Required<MenuProps>['items'][number]

// Icon mapping for agents
const AGENT_ICON_MAP: Record<string, React.ReactNode> = {
  persona_distribution: <UsergroupAddOutlined />,
  persona_generator: <UserAddOutlined />,
  transcript_parser: <FileSearchOutlined />,
  c2_message_generation: <MessageOutlined />
}
const DEFAULT_AGENT_ICON = <RobotOutlined />

function getItem(
  label: React.ReactNode,
  key: React.Key,
  icon?: React.ReactNode,
  children?: MenuItem[],
  type?: 'group',
): MenuItem {
  return {
    key,
    icon,
    children,
    label,
    type,
  } as MenuItem
}

interface PageLayoutProps {
  title: string
  description?: string
  showBackButton?: boolean
  children: ReactNode
  extra?: ReactNode
}

export default function PageLayout({
  title,
  description,
  showBackButton = false,
  children,
  extra
}: PageLayoutProps) {
  const [collapsed, setCollapsed] = useState(false)
  const pathname = usePathname()
  const router = useRouter()
  const { timezone, setTimezone } = useTimezone()

  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken()

  // Dynamic agents state
  const [agentsList, setAgentsList] = useState<AgentInfo[]>([])
  const [agentsLoading, setAgentsLoading] = useState(true)

  // Fetch agents on mount
  useEffect(() => {
    const loadAgents = async () => {
      try {
        const response = await apiClient.listAgents()
        if (response.data) {
          setAgentsList(response.data.agents)
        }
      } catch (error) {
        console.error('Failed to load agents:', error)
      } finally {
        setAgentsLoading(false)
      }
    }

    loadAgents()
  }, [])

  // Build dynamic menu items based on fetched agents
  const agentMenuItems = agentsList.length > 0
    ? agentsList.map(agent =>
        getItem(
          agent.display_name,
          `/agents/${agent.agent_id}`,
          AGENT_ICON_MAP[agent.agent_id] || DEFAULT_AGENT_ICON
        )
      )
    : [
        // Fallback hardcoded menu
        getItem('Persona Distribution', '/agents/persona_distribution', <UsergroupAddOutlined />),
        getItem('Persona Generator', '/agents/persona_generator', <UserAddOutlined />),
        getItem('Transcript Parser', '/agents/transcript_parser', <FileSearchOutlined />),
        getItem('C2 Message Generator', '/agents/c2_message_generation', <MessageOutlined />),
      ]

  const items: MenuItem[] = [
    getItem('Home', '/', <HomeOutlined />),
    getItem('Agents', 'agents', <RobotOutlined />, agentMenuItems),
    getItem('Workflows', 'workflows', <BranchesOutlined />, [
      getItem('Conversation Simulation', '/workflows/conversation_simulation', <CommentOutlined />),
    ]),
  ]

  // Get the selected keys based on current path
  const getSelectedKeys = () => {
    if (pathname === '/') return ['/']
    return [pathname]
  }

  // Get the open keys for sub-menus
  const getDefaultOpenKeys = () => {
    if (pathname === '/') return []
    
    if (pathname.startsWith('/agents/')) {
      return ['agents']
    }
    if (pathname.startsWith('/workflows/')) {
      return ['workflows']
    }
    return []
  }

  const handleMenuClick: MenuProps['onClick'] = (e) => {
    // Only navigate for actual page routes (starting with /)
    if (e.key.startsWith('/')) {
      router.push(e.key)
    }
  }

  const TimezoneSelector = (
    <Space size="small">
      <Tooltip title="Timezone">
        <GlobalOutlined style={{ color: '#666' }} />
      </Tooltip>
      <Select
        value={timezone}
        onChange={(value: TimezoneOption) => setTimezone(value)}
        size="small"
        style={{ width: 80 }}
        options={[
          { value: 'IST', label: 'IST' },
          { value: 'UTC', label: 'UTC' },
        ]}
      />
    </Space>
  )

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider 
        width={280} 
        collapsible 
        collapsed={collapsed} 
        onCollapse={(value) => setCollapsed(value)}
        style={{ 
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div style={{ 
          height: 32, 
          margin: 16, 
          background: 'rgba(255, 255, 255, 0.2)', 
          borderRadius: 6, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          color: 'white', 
          fontWeight: 'bold', 
          overflow: 'hidden', 
          whiteSpace: 'nowrap' 
        }}>
          {collapsed ? 'MD' : 'Mount Doom'}
        </div>
        <Menu 
          theme="dark" 
          mode="inline"
          selectedKeys={getSelectedKeys()}
          defaultOpenKeys={collapsed ? [] : getDefaultOpenKeys()}
          items={items} 
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout style={{ marginLeft: collapsed ? 80 : 280, transition: 'margin-left 0.2s' }}>
        <Header style={{ 
          padding: '0 24px', 
          background: colorBgContainer, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          zIndex: 1,
          boxShadow: '0 1px 4px rgba(0, 0, 0, 0.08)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              style={{
                fontSize: '16px',
                width: 64,
                height: 64,
                marginRight: 16,
                marginLeft: -24
              }}
            />
            <Title level={4} style={{ margin: 0 }}>{title}</Title>
          </div>
          <Space size="middle">
            {TimezoneSelector}
            {extra && <div>{extra}</div>}
          </Space>
        </Header>
        <Content style={{ margin: '24px 16px 0' }}>
          <div
            style={{
              padding: 24,
              minHeight: 360,
              background: colorBgContainer,
              borderRadius: borderRadiusLG,
            }}
          >
            {description && (
              <Text type="secondary" style={{ display: 'block', marginBottom: 24 }}>
                {description}
              </Text>
            )}
            {children}
          </div>
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          Mount Doom ©{new Date().getFullYear()} - AI Agent Simulation Platform
        </Footer>
      </Layout>
    </Layout>
  )
}
