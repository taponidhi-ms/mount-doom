'use client'

import Link from 'next/link'
import { Card, Typography, Row, Col } from 'antd'

const { Title, Paragraph } = Typography

export default function Home() {
  const features = [
    {
      title: 'Persona Generation',
      href: '/persona-generation',
      description: 'Generate personas from simulation prompts using specialized AI agents. Transform your ideas into detailed character profiles.',
    },
    {
      title: 'General Prompt',
      href: '/general-prompt',
      description: 'Get responses for any general prompt using LLM models directly. Flexible AI assistance for various tasks.',
    },
    {
      title: 'Prompt Validator',
      href: '/prompt-validator',
      description: 'Validate simulation prompts to ensure they meet quality standards. Get feedback on prompt effectiveness.',
    },
    {
      title: 'Conversation Simulation',
      href: '/conversation-simulation',
      description: 'Simulate multi-turn conversations between customer service representatives and customers with intelligent orchestration.',
    },
  ]

  return (
    <div style={{ minHeight: '100vh', padding: '32px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <Title level={1}>Mount Doom</Title>
        <Paragraph style={{ fontSize: '16px', marginBottom: '32px' }}>
          AI Agent Simulation Platform - Multi-agent conversation simulation and prompt generation
        </Paragraph>

        <Row gutter={[16, 16]}>
          {features.map((feature) => (
            <Col xs={24} md={12} key={feature.href}>
              <Link href={feature.href} style={{ textDecoration: 'none' }}>
                <Card 
                  hoverable
                  title={feature.title}
                  style={{ height: '100%' }}
                >
                  <Paragraph>{feature.description}</Paragraph>
                </Card>
              </Link>
            </Col>
          ))}
        </Row>

        <Card 
          style={{ marginTop: '48px' }}
          title="About This Platform"
        >
          <Paragraph>
            This platform leverages Azure AI Projects to provide advanced simulation capabilities.
            Each use case is powered by specialized agents and models, with full tracking of
            tokens used, response times, and conversation history. All interactions are
            automatically stored in Cosmos DB for analysis and retrieval.
          </Paragraph>
        </Card>
      </div>
    </div>
  )
}
