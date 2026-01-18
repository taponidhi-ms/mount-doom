'use client'

import Link from 'next/link'
import { Card, Typography, Row, Col, theme } from 'antd'
import { 
  UsergroupAddOutlined, 
  UserAddOutlined, 
  MessageOutlined, 
  CommentOutlined,
  FileSearchOutlined,
  ArrowRightOutlined
} from '@ant-design/icons'
import PageLayout from '@/components/PageLayout'

const { Title, Paragraph, Text } = Typography

export default function Home() {
  const {
    token: { colorPrimary, colorBgContainer, colorBorderSecondary },
  } = theme.useToken();

  const features = [
    {
      title: 'Persona Distribution Generator',
      href: '/agents/persona_distribution',
      icon: <UsergroupAddOutlined style={{ fontSize: '24px', color: colorPrimary }} />,
      description: 'Generate persona distributions from simulation prompts using specialized AI agents. Transform your ideas into structured conversation parameters.',
    },
    {
      title: 'Persona Generator',
      href: '/agents/persona_generator',
      icon: <UserAddOutlined style={{ fontSize: '24px', color: colorPrimary }} />,
      description: 'Generate exact customer personas with specific intents, sentiments, subjects, and metadata. Perfect for creating detailed scenarios.',
    },
    {
      title: 'Transcript Parser',
      href: '/agents/transcript_parser',
      icon: <FileSearchOutlined style={{ fontSize: '24px', color: colorPrimary }} />,
      description: 'Parse customer–representative transcripts to extract intent, subject, and sentiment.',
    },
    {
      title: 'Conversation Simulation',
      href: '/workflows/conversation_simulation',
      icon: <CommentOutlined style={{ fontSize: '24px', color: colorPrimary }} />,
      description: 'Simulate multi-turn conversations between customer service representatives and customers with intelligent orchestration.',
    },
    {
      title: 'C2 Message Generation',
      href: '/agents/c2_message_generation',
      icon: <MessageOutlined style={{ fontSize: '24px', color: colorPrimary }} />,
      description: 'Generate customer (C2) messages for conversation simulations using AI agents.',
    },
  ]

  return (
    <PageLayout
      title="Mount Doom"
      description="AI Agent Simulation Platform - Multi-agent conversation simulation and prompt generation"
    >
      <Row gutter={[24, 24]}>
        {features.map((feature) => (
          <Col xs={24} md={12} lg={8} key={feature.href}>
            <Link href={feature.href} style={{ textDecoration: 'none' }}>
              <Card 
                hoverable
                style={{
                  height: '100%',
                  borderColor: colorBorderSecondary,
                  display: 'flex',
                  flexDirection: 'column'
                }}
                styles={{ body: { flex: 1, display: 'flex', flexDirection: 'column' } }}
              >
                <div style={{ marginBottom: 16 }}>
                  {feature.icon}
                </div>
                <Title level={4} style={{ marginTop: 0, marginBottom: 12 }}>
                  {feature.title}
                </Title>
                <Paragraph type="secondary" style={{ flex: 1, marginBottom: 16 }}>
                  {feature.description}
                </Paragraph>
                <div style={{ display: 'flex', alignItems: 'center', color: colorPrimary }}>
                  <Text strong style={{ color: 'inherit', marginRight: 8 }}>Try it out</Text>
                  <ArrowRightOutlined />
                </div>
              </Card>
            </Link>
          </Col>
        ))}
      </Row>

      <Card 
        style={{ marginTop: '48px', background: '#f8f9fa', border: 'none' }}
        title={<Title level={4} style={{ margin: 0 }}>About This Platform</Title>}
      >
        <Paragraph style={{ fontSize: '15px', color: '#555' }}>
          This platform leverages Azure AI Projects to provide advanced simulation capabilities.
          Each use case is powered by specialized agents and models, with full tracking of
          tokens used, response times, and conversation history. All interactions are
          automatically stored in Cosmos DB for analysis and retrieval.
        </Paragraph>
      </Card>
    </PageLayout>
  )
}
