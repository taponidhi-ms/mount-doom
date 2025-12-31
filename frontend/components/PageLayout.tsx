'use client'

import { ReactNode } from 'react'
import Link from 'next/link'
import { ArrowLeftOutlined } from '@ant-design/icons'
import { Button, Typography } from 'antd'

const { Title, Paragraph } = Typography

interface PageLayoutProps {
  title: string
  description?: string
  showBackButton?: boolean
  children: ReactNode
}

export default function PageLayout({ 
  title, 
  description, 
  showBackButton = false,
  children 
}: PageLayoutProps) {
  return (
    <div style={{ minHeight: '100vh', padding: '32px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {showBackButton && (
          <Link href="/">
            <Button 
              type="text" 
              icon={<ArrowLeftOutlined />}
              style={{ marginBottom: '16px' }}
            >
              Back to Home
            </Button>
          </Link>
        )}
        
        <Title level={1}>{title}</Title>
        {description && (
          <Paragraph style={{ fontSize: '16px', marginBottom: '24px' }}>
            {description}
          </Paragraph>
        )}
        
        {children}
      </div>
    </div>
  )
}
