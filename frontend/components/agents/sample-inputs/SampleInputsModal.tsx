'use client'

import { Modal, Card, Typography, Space, Button } from 'antd'
import { BulbOutlined } from '@ant-design/icons'

const { Text, Paragraph } = Typography

interface SampleInput {
  label: string
  value: string
}

interface SampleInputsModalProps {
  open: boolean
  onClose: () => void
  sampleInputs: SampleInput[]
  onSelect: (value: string) => void
  inputLabel?: string
}

export default function SampleInputsModal({
  open,
  onClose,
  sampleInputs,
  onSelect,
  inputLabel = 'Input'
}: SampleInputsModalProps) {
  const handleSelect = (value: string) => {
    onSelect(value)
    onClose()
  }

  return (
    <Modal
      title={
        <Space>
          <BulbOutlined style={{ color: '#1890ff' }} />
          <span>Sample {inputLabel}s</span>
        </Space>
      }
      open={open}
      onCancel={onClose}
      footer={null}
      width={700}
      style={{ top: 40 }}
    >
      <Space direction="vertical" size="middle" style={{ width: '100%', marginTop: 16 }}>
        {sampleInputs.map((sample, index) => (
          <Card
            key={index}
            size="small"
            hoverable
            style={{
              cursor: 'pointer',
              border: '1px solid #e8e8e8',
              transition: 'all 0.3s'
            }}
            onClick={() => handleSelect(sample.value)}
          >
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <Text strong style={{ fontSize: 14, color: '#1890ff' }}>
                {sample.label}
              </Text>
              <Paragraph
                style={{
                  marginBottom: 0,
                  fontSize: 13,
                  color: '#666',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word'
                }}
                ellipsis={{ rows: 3, expandable: true, symbol: 'Show more' }}
              >
                {sample.value}
              </Paragraph>
            </Space>
          </Card>
        ))}
      </Space>
    </Modal>
  )
}
