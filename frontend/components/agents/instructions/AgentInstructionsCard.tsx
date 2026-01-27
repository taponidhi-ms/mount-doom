'use client'

import { useState } from 'react'
import { Card, Button, Space, Typography } from 'antd'
import { InfoCircleOutlined } from '@ant-design/icons'

const { Text } = Typography

interface AgentInstructionsCardProps {
  instructions: string
}

export default function AgentInstructionsCard({ instructions }: AgentInstructionsCardProps) {
  const [showInstructions, setShowInstructions] = useState(false)

  return (
    <Card
      title={
        <Space>
          <InfoCircleOutlined />
          <span>Agent Instructions</span>
        </Space>
      }
      extra={
        <Button type="text" onClick={() => setShowInstructions(!showInstructions)}>
          {showInstructions ? 'Hide' : 'Show'}
        </Button>
      }
      size="small"
    >
      {showInstructions ? (
        <pre
          style={{
            whiteSpace: 'pre-wrap',
            wordWrap: 'break-word',
            background: '#f5f5f5',
            padding: 12,
            borderRadius: 8,
            maxHeight: 400,
            overflow: 'auto',
            fontSize: 12,
            margin: 0,
          }}
        >
          {instructions}
        </pre>
      ) : (
        <Text type="secondary">Click &quot;Show&quot; to view the agent&apos;s instruction set</Text>
      )}
    </Card>
  )
}
