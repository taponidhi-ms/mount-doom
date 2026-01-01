'use client'

import { useState } from 'react'
import { Button, Card, Input, Tabs, Table, Space, Typography, message, Alert, Collapse, Tag, Upload, Progress } from 'antd'
import { UploadOutlined, ReloadOutlined } from '@ant-design/icons'
import PageLayout from '@/components/PageLayout'
import { apiClient, ConversationSimulationResponse, BrowseResponse, ConversationMessage } from '@/lib/api-client'

const { TextArea } = Input
const { Paragraph, Text, Title } = Typography
const { Panel } = Collapse

interface BatchItem {
  key: string;
  customerIntent: string;
  customerSentiment: string;
  conversationSubject: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: ConversationSimulationResponse;
  error?: string;
}

export default function ConversationSimulationPage() {
  const [customerIntent, setCustomerIntent] = useState('')
  const [customerSentiment, setCustomerSentiment] = useState('')
  const [conversationSubject, setConversationSubject] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ConversationSimulationResponse | null>(null)
  const [error, setError] = useState('')
  
  // History state
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyData, setHistoryData] = useState<BrowseResponse | null>(null)
  const [historyError, setHistoryError] = useState('')

  // Batch Simulation State
  const [batchItems, setBatchItems] = useState<BatchItem[]>([])
  const [batchLoading, setBatchLoading] = useState(false)
  const [batchProgress, setBatchProgress] = useState(0)
  const [currentBatchIndex, setCurrentBatchIndex] = useState(-1)

  const handleFileUpload = (file: File) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target?.result as string)
        let personas = []
        
        if (Array.isArray(json)) {
          personas = json
        } else if (json.CustomerPersonas && Array.isArray(json.CustomerPersonas)) {
          personas = json.CustomerPersonas
        } else {
          message.error('Invalid JSON format. Expected array or object with CustomerPersonas array.')
          return
        }

        const items: BatchItem[] = personas.map((p: any, index: number) => ({
          key: `batch-${index}-${Date.now()}`,
          customerIntent: p.CustomerIntent || p.customerIntent || '',
          customerSentiment: p.CustomerSentiment || p.customerSentiment || '',
          conversationSubject: p.ConversationSubject || p.conversationSubject || '',
          status: 'pending' as const
        })).filter((item: BatchItem) => item.customerIntent && item.customerSentiment && item.conversationSubject)

        if (items.length === 0) {
          message.warning('No valid personas found in file.')
          return
        }

        setBatchItems(items)
        setBatchProgress(0)
        setCurrentBatchIndex(-1)
        message.success(`Loaded ${items.length} personas.`)
      } catch (err) {
        message.error('Failed to parse JSON file.')
        console.error(err)
      }
    }
    reader.readAsText(file)
    return false // Prevent upload
  }

  const runBatchSimulation = async () => {
    if (batchItems.length === 0) return
    
    setBatchLoading(true)
    setBatchProgress(0)
    
    const newItems = [...batchItems]
    
    for (let i = 0; i < newItems.length; i++) {
      setCurrentBatchIndex(i)
      newItems[i].status = 'running'
      setBatchItems([...newItems])
      
      try {
        const response = await apiClient.simulateConversation(
          newItems[i].customerIntent,
          newItems[i].customerSentiment,
          newItems[i].conversationSubject
        )
        
        if (response.data) {
          newItems[i].status = 'completed'
          newItems[i].result = response.data
        } else {
          newItems[i].status = 'failed'
          newItems[i].error = response.error || 'Unknown error'
        }
      } catch (err) {
        newItems[i].status = 'failed'
        newItems[i].error = 'Exception occurred'
      }
      
      setBatchItems([...newItems])
      setBatchProgress(Math.round(((i + 1) / newItems.length) * 100))
    }
    
    setBatchLoading(false)
    setCurrentBatchIndex(-1)
    message.success('Batch simulation completed!')
    
    // Refresh history if we're on that tab or to keep it updated
    if (historyData) {
      loadHistory(1)
    }
  }

  const loadHistory = async (page: number = 1, pageSize: number = 10) => {
    setHistoryLoading(true)
    setHistoryError('')
    const response = await apiClient.browseConversationSimulations(page, pageSize)
    setHistoryLoading(false)
    
    if (response.data) {
      setHistoryData(response.data)
    } else if (response.error) {
      setHistoryError(response.error)
      message.error('Failed to load history')
    }
  }

  const sampleConfigs = [
    {
      intent: "Technical Support",
      sentiment: "Frustrated",
      subject: "Internet connection keeps dropping every 10 minutes"
    },
    {
      intent: "Billing Inquiry",
      sentiment: "Confused",
      subject: "Unexpected charge of $50 on the monthly statement"
    },
    {
      intent: "Product Return",
      sentiment: "Neutral",
      subject: "Returning a pair of shoes that are the wrong size"
    }
  ]

  const handleSubmit = async () => {
    // Validate fields and provide specific feedback
    const missing = []
    if (!customerIntent.trim()) missing.push('Customer Intent')
    if (!customerSentiment.trim()) missing.push('Customer Sentiment')
    if (!conversationSubject.trim()) missing.push('Conversation Subject')
    
    if (missing.length > 0) {
      message.warning(`Please fill in: ${missing.join(', ')}`)
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    const response = await apiClient.simulateConversation(
      customerIntent,
      customerSentiment,
      conversationSubject
    )
    setLoading(false)

    if (response.data) {
      setResult(response.data)
      message.success('Conversation simulated successfully!')
      if (historyData) {
        loadHistory(1)
      }
    } else if (response.error) {
      setError(response.error)
      message.error('Failed to simulate conversation')
    }
  }

  const renderConversationHistory = (history: ConversationMessage[]) => {
    return (
      <Space direction="vertical" size="small" style={{ width: '100%' }}>
        {history.map((msg, index) => {
          const isSystem = msg.agent_name === 'System';
          const isC1 = msg.agent_name === 'C1Agent';
          
          // Determine background color
          let bgColor = '#ffffff';
          if (isC1) bgColor = '#e6f7ff'; // Blue for C1
          else if (!isSystem) bgColor = '#f6ffed'; // Green for C2
          
          // Determine tag color
          let tagColor = 'default';
          if (isC1) tagColor = 'blue';
          else if (!isSystem) tagColor = 'green';

          return (
            <Card 
              key={index} 
              size="small"
              style={{ 
                background: bgColor,
                border: isSystem ? 'none' : undefined,
                boxShadow: isSystem ? 'none' : undefined
              }}
              bodyStyle={isSystem ? { padding: '4px 0', fontStyle: 'italic', color: '#888', textAlign: 'center' } : undefined}
            >
              {isSystem ? (
                <Text type="secondary" italic style={{ fontSize: 12 }}>
                  {msg.message}
                </Text>
              ) : (
                <Space direction="vertical" size="small" style={{ width: '100%' }}>
                  <div>
                    <Tag color={tagColor}>
                      {msg.agent_name}
                    </Tag>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </Text>
                  </div>
                  <Text>{msg.message}</Text>
                </Space>
              )}
            </Card>
          );
        })}
      </Space>
    )
  }

  const columns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (text: string) => new Date(text).toLocaleString(),
      width: 180,
    },
    {
      title: 'Intent',
      dataIndex: 'conversation_properties',
      key: 'intent',
      width: 150,
      ellipsis: true,
      render: (props: any) => props?.CustomerIntent || 'N/A',
    },
    {
      title: 'Sentiment',
      dataIndex: 'conversation_properties',
      key: 'sentiment',
      width: 120,
      render: (props: any) => props?.CustomerSentiment || 'N/A',
    },
    {
      title: 'Subject',
      dataIndex: 'conversation_properties',
      key: 'subject',
      ellipsis: true,
      render: (props: any) => props?.ConversationSubject || 'N/A',
    },
    {
      title: 'Status',
      dataIndex: 'conversation_status',
      key: 'status',
      width: 120,
      render: (status: string) => (
        <Tag color={status === 'Completed' ? 'green' : 'orange'}>
          {status}
        </Tag>
      ),
    },
    {
      title: 'Messages',
      dataIndex: 'conversation_history',
      key: 'messages',
      width: 100,
      render: (history: any[]) => history?.length || 0,
    },
    {
      title: 'Tokens',
      dataIndex: 'total_tokens_used',
      key: 'tokens',
      width: 100,
      render: (value: number) => value || 'N/A',
    },
  ]

  const batchColumns = [
    {
      title: 'Intent',
      dataIndex: 'customerIntent',
      key: 'intent',
      width: 150,
      ellipsis: true,
    },
    {
      title: 'Sentiment',
      dataIndex: 'customerSentiment',
      key: 'sentiment',
      width: 120,
    },
    {
      title: 'Subject',
      dataIndex: 'conversationSubject',
      key: 'subject',
      ellipsis: true,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => {
        let color = 'default';
        if (status === 'running') color = 'processing';
        if (status === 'completed') color = 'success';
        if (status === 'failed') color = 'error';
        return <Tag color={color}>{status.toUpperCase()}</Tag>;
      },
    },
    {
      title: 'Result',
      key: 'result',
      width: 150,
      render: (_: any, record: BatchItem) => {
        if (record.status === 'completed' && record.result) {
          return (
            <Space direction="vertical" size={0}>
              <Text type="secondary" style={{ fontSize: 12 }}>{record.result.conversation_history.length} msgs</Text>
            </Space>
          );
        }
        if (record.status === 'failed') {
          return <Text type="danger" style={{ fontSize: 12 }}>{record.error}</Text>;
        }
        return '-';
      }
    }
  ];

  const tabItems = [
    {
      key: 'simulate',
      label: 'Simulate',
      children: (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Card title="Conversation Configuration">
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <Text strong>Customer Intent</Text>
                <Input
                  value={customerIntent}
                  onChange={(e) => setCustomerIntent(e.target.value)}
                  placeholder="e.g., Technical Support, Billing Inquiry, Product Return"
                  style={{ marginTop: 8 }}
                  disabled={loading}
                  size="large"
                />
              </div>

              <div>
                <Text strong>Customer Sentiment</Text>
                <Input
                  value={customerSentiment}
                  onChange={(e) => setCustomerSentiment(e.target.value)}
                  placeholder="e.g., Frustrated, Happy, Confused, Angry"
                  style={{ marginTop: 8 }}
                  disabled={loading}
                  size="large"
                />
              </div>

              <div>
                <Text strong>Conversation Subject</Text>
                <Input
                  value={conversationSubject}
                  onChange={(e) => setConversationSubject(e.target.value)}
                  placeholder="e.g., Product Defect, Service Cancellation, Account Issue"
                  style={{ marginTop: 8 }}
                  disabled={loading}
                  size="large"
                />
              </div>
              
              <Alert 
                message="Note" 
                description="Conversations will run up to 20 turns or until completion is detected by the agents (e.g. 'I will end this call now')."
                type="info" 
                showIcon 
              />

              <Button 
                type="primary" 
                size="large"
                onClick={handleSubmit}
                loading={loading}
                disabled={!customerIntent.trim() || !customerSentiment.trim() || !conversationSubject.trim()}
                block
              >
                {loading ? 'Simulating...' : 'Start Simulation'}
              </Button>

              <div style={{ marginTop: 16 }}>
                <Text strong>Sample Configurations</Text>
                <Space direction="vertical" style={{ width: '100%', marginTop: 8 }}>
                  {sampleConfigs.map((sample, index) => (
                    <Card key={index} size="small" style={{ background: '#f9f9f9' }}>
                      <Space align="start" style={{ width: '100%', justifyContent: 'space-between' }}>
                        <Space direction="vertical" size={0}>
                          <Text style={{ fontSize: 13 }}><Text strong>Intent:</Text> {sample.intent}</Text>
                          <Text style={{ fontSize: 13 }}><Text strong>Sentiment:</Text> {sample.sentiment}</Text>
                          <Text style={{ fontSize: 13 }}><Text strong>Subject:</Text> {sample.subject}</Text>
                        </Space>
                        <Button 
                          size="small" 
                          type="link" 
                          onClick={() => {
                            setCustomerIntent(sample.intent)
                            setCustomerSentiment(sample.sentiment)
                            setConversationSubject(sample.subject)
                          }}
                          style={{ padding: 0, marginLeft: 8 }}
                        >
                          Try it
                        </Button>
                      </Space>
                    </Card>
                  ))}
                </Space>
              </div>

              {error && (
                <Alert message="Error" description={error} type="error" showIcon />
              )}
            </Space>
          </Card>

          {result && (
            <Card title="Simulation Results">
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <Space size="large" wrap>
                  <div>
                    <Text type="secondary">Status: </Text>
                    <Tag color={result.conversation_status === 'Completed' ? 'green' : 'orange'}>
                      {result.conversation_status}
                    </Tag>
                  </div>
                  <div>
                    <Text type="secondary">Total Messages: </Text>
                    <Text strong>{result.conversation_history.length}</Text>
                  </div>
                  <div>
                    <Text type="secondary">Time Taken: </Text>
                    <Text strong>{Math.round(result.total_time_taken_ms)} ms</Text>
                  </div>
                </Space>

                <div>
                  <Text strong style={{ fontSize: 16 }}>Conversation History</Text>
                  <div style={{ marginTop: 16 }}>
                    {renderConversationHistory(result.conversation_history)}
                  </div>
                </div>
              </Space>
            </Card>
          )}
        </Space>
      ),
    },
    {
      key: 'batch',
      label: 'Batch Simulation',
      children: (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Card title="Batch Processing">
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <Alert
                message="Upload Personas"
                description="Upload a JSON file containing a list of personas (CustomerIntent, CustomerSentiment, ConversationSubject). The simulation will run for each persona sequentially."
                type="info"
                showIcon
              />
              
              <Space>
                <Upload 
                  beforeUpload={handleFileUpload} 
                  showUploadList={false}
                  accept=".json"
                >
                  <Button icon={<UploadOutlined />} size="large" disabled={batchLoading}>
                    Upload JSON File
                  </Button>
                </Upload>
                
                <Button 
                  type="primary" 
                  size="large" 
                  onClick={runBatchSimulation}
                  disabled={batchItems.length === 0 || batchLoading}
                  loading={batchLoading}
                >
                  {batchLoading ? 'Running Batch...' : 'Start Batch Simulation'}
                </Button>
              </Space>

              {batchLoading && (
                <div style={{ marginTop: 16 }}>
                  <Text>Processing item {currentBatchIndex + 1} of {batchItems.length}</Text>
                  <Progress percent={batchProgress} status="active" />
                </div>
              )}
            </Space>
          </Card>

          {batchItems.length > 0 && (
            <Card title={`Loaded Personas (${batchItems.length})`}>
              <Table
                dataSource={batchItems}
                columns={batchColumns}
                pagination={{ pageSize: 10 }}
                expandable={{
                  expandedRowRender: (record) => (
                    <div style={{ padding: 16 }}>
                      {record.result ? (
                        <Space direction="vertical" size="small" style={{ width: '100%' }}>
                          <Text strong>Conversation Result:</Text>
                          <Space size="large">
                            <Tag color={record.result.conversation_status === 'Completed' ? 'green' : 'orange'}>
                              {record.result.conversation_status}
                            </Tag>
                            <Text>Time: {Math.round(record.result.total_time_taken_ms)}ms</Text>
                          </Space>
                          <div style={{ marginTop: 8 }}>
                            {renderConversationHistory(record.result.conversation_history)}
                          </div>
                        </Space>
                      ) : (
                        <Text type="secondary">No result available yet.</Text>
                      )}
                    </div>
                  ),
                }}
              />
            </Card>
          )}
        </Space>
      )
    },
    {
      key: 'history',
      label: 'History',
      children: (
        <Card 
          title="Simulation History"
          extra={
            <Button 
              icon={<ReloadOutlined />} 
              onClick={() => loadHistory(historyData?.page || 1, historyData?.page_size || 10)}
              loading={historyLoading}
            >
              Reload
            </Button>
          }
        >
          {historyError && (
            <Alert message="Error" description={historyError} type="error" showIcon style={{ marginBottom: 16 }} />
          )}
          
          <Table
            dataSource={historyData?.items || []}
            columns={columns}
            loading={historyLoading}
            rowKey={(record) => record.id || record.start_time}
            pagination={{
              current: historyData?.page || 1,
              pageSize: historyData?.page_size || 10,
              total: historyData?.total_count || 0,
              showSizeChanger: true,
              showTotal: (total) => `Total ${total} items`,
              onChange: (page, pageSize) => loadHistory(page, pageSize),
            }}
            expandable={{
              expandedRowRender: (record) => (
                <div style={{ padding: 16 }}>
                  {record.conversation_history && renderConversationHistory(record.conversation_history)}
                </div>
              ),
            }}
          />
        </Card>
      ),
    },
  ]

  return (
    <PageLayout
      title="Conversation Simulation"
      description="Simulate multi-turn conversations between customer service representatives and customers."
      showBackButton
    >
      <Tabs 
        defaultActiveKey="simulate" 
        items={tabItems}
        onChange={(key) => {
          if (key === 'history' && !historyData) {
            loadHistory(1)
          }
        }}
      />
    </PageLayout>
  )
}
