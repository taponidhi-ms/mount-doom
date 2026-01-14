'use client'

import { ReactNode, useState } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { 
  HomeOutlined, 
  UsergroupAddOutlined, 
  UserAddOutlined, 
  MessageOutlined, 
  CheckCircleOutlined, 
  CommentOutlined,
  FileSearchOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined
} from '@ant-design/icons'
import { Button, Typography, Layout, Menu, theme } from 'antd'

const { Title, Paragraph } = Typography
const { Header, Content, Footer, Sider } = Layout

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
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const items = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: 'Home',
    },
    {
      key: '/persona-distribution',
      icon: <UsergroupAddOutlined />,
      label: 'Persona Distribution',
    },
    {
      key: '/persona-generator',
      icon: <UserAddOutlined />,
      label: 'Persona Generator',
    },
    {
      key: '/general-prompt',
      icon: <MessageOutlined />,
      label: 'General Prompt',
    },
    {
      key: '/transcript-parser',
      icon: <FileSearchOutlined />,
      label: 'Transcript Parser',
    },
    {
      key: '/prompt-validator',
      icon: <CheckCircleOutlined />,
      label: 'Prompt Validator',
    },
    {
      key: '/conversation-simulation',
      icon: <CommentOutlined />,
      label: 'Conversation Simulation',
    },
    {
      key: '/conversation-simulation-v2',
      icon: <CommentOutlined />,
      label: 'Conversation Simulation V2',
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={300} collapsible collapsed={collapsed} onCollapse={(value) => setCollapsed(value)}>
        <div style={{ height: 32, margin: 16, background: 'rgba(255, 255, 255, 0.2)', borderRadius: 6, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold', overflow: 'hidden', whiteSpace: 'nowrap' }}>
          {collapsed ? 'MD' : 'Mount Doom'}
        </div>
        <Menu 
          theme="dark" 
          defaultSelectedKeys={[pathname]} 
          selectedKeys={[pathname]}
          mode="inline" 
          items={items} 
          onClick={({ key }) => router.push(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: '0 24px', background: colorBgContainer, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
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
          {extra && <div>{extra}</div>}
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
              <Paragraph style={{ fontSize: '16px', marginBottom: '24px' }}>
                {description}
              </Paragraph>
            )}
            {children}
          </div>
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          Mount Doom ©{new Date().getFullYear()} Created by AI Agent
        </Footer>
      </Layout>
    </Layout>
  )
}
