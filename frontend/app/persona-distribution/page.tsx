'use client'

import { useState } from 'react'
import { Button, Card, Input, Tabs, Table, Space, Typography, message, Spin, Alert } from 'antd'
import { LoadingOutlined, ReloadOutlined, DownloadOutlined } from '@ant-design/icons'
import PageLayout from '@/components/PageLayout'
import { apiClient, PersonaDistributionResponse, BrowseResponse, EvalsDataResponse } from '@/lib/api-client'

const { TextArea } = Input
const { Title, Paragraph, Text } = Typography

export default function PersonaDistributionPage() {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<PersonaDistributionResponse | null>(null)
  const [error, setError] = useState('')
  
  // History state
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyData, setHistoryData] = useState<BrowseResponse | null>(null)
  const [historyError, setHistoryError] = useState('')

  // Evals state
  const [evalsLoading, setEvalsLoading] = useState(false)
  const [evalsData, setEvalsData] = useState<BrowseResponse | null>(null)
  const [evalsError, setEvalsError] = useState('')
  const [selectedRunIds, setSelectedRunIds] = useState<string[]>([])
  const [preparingEvals, setPreparingEvals] = useState(false)
  const [preparedEvals, setPreparedEvals] = useState<EvalsDataResponse | null>(null)

  const loadHistory = async (page: number = 1, pageSize: number = 10) => {
    setHistoryLoading(true)
    setHistoryError('')
    const response = await apiClient.browsePersonaDistributions(page, pageSize)
    setHistoryLoading(false)
    
    if (response.data) {
      setHistoryData(response.data)
    } else if (response.error) {
      setHistoryError(response.error)
      message.error('Failed to load history')
    }
  }

  const loadEvalsHistory = async (page: number = 1, pageSize: number = 10) => {
    setEvalsLoading(true)
    setEvalsError('')
    const response = await apiClient.browsePersonaDistributions(page, pageSize)
    setEvalsLoading(false)
    
    if (response.data) {
      setEvalsData(response.data)
    } else if (response.error) {
      setEvalsError(response.error)
      message.error('Failed to load runs for evals')
    }
  }

  const handlePrepareEvals = async () => {
    if (selectedRunIds.length === 0) {
      message.warning('Please select at least one run to prepare evals')
      return
    }

    setPreparingEvals(true)
    setPreparedEvals(null)

    const response = await apiClient.prepareEvals(selectedRunIds)
    setPreparingEvals(false)

    if (response.data) {
      message.success(response.data.message)
      
      // Fetch the prepared evals data
      const evalsResponse = await apiClient.getLatestEvals()
      if (evalsResponse.data) {
        setPreparedEvals(evalsResponse.data)
      }
    } else if (response.error) {
      message.error('Failed to prepare evals: ' + response.error)
    }
  }

  const downloadJSON = (data: any, filename: string) => {
    const jsonStr = JSON.stringify(data, null, 2)
    const blob = new Blob([jsonStr], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const samplePrompts = [
    "Generate a distribution of 100 calls for a telecom company where 60% are billing inquiries (mostly negative sentiment), 30% are technical support (mixed sentiment), and 10% are new service requests (positive sentiment).",
    "Create a persona distribution for a retail bank's customer service. I need 50 conversations about credit card disputes, 30 about loan applications, and 20 about account balance checks.",
    "Simulate a healthcare provider's appointment line. 40% scheduling new appointments, 40% rescheduling existing ones, and 20% cancelling. Most callers should be anxious or neutral."
  ]

  const handleSubmit = async () => {
    if (!prompt.trim()) {
      message.warning('Please enter a prompt')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    const response = await apiClient.generatePersonaDistribution(prompt)
    setLoading(false)

    if (response.data) {
      setResult(response.data)
      message.success('Persona distribution generated successfully!')
      // Reload history to show the new result
      if (historyData) {
        loadHistory(1)
      }
    } else if (response.error) {
      setError(response.error)
      message.error('Failed to generate persona distribution')
    }
  }

  const columns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (text: string) => new Date(text).toLocaleString(),
      width: 200,
    },
    {
      title: 'Prompt',
      dataIndex: 'prompt',
      key: 'prompt',
      ellipsis: true,
      render: (text: string) => text || 'N/A',
    },
    {
      title: 'Response Preview',
      dataIndex: 'response',
      key: 'response',
      ellipsis: true,
      render: (text: string) => text?.substring(0, 100) + (text?.length > 100 ? '...' : ''),
    },
    {
      title: 'Tokens',
      dataIndex: 'tokens_used',
      key: 'tokens',
      width: 100,
      render: (value: number) => value || 'N/A',
    },
    {
      title: 'Time (ms)',
      dataIndex: 'time_taken_ms',
      key: 'time',
      width: 120,
      render: (value: number) => value ? Math.round(value) : 'N/A',
    },
  ]

  const tabItems = [
    {
      key: 'generate',
      label: 'Generate',
      children: (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Card title="Generate Persona Distribution">
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <Text strong>Simulation Prompt</Text>
                <TextArea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Enter your simulation prompt to generate a persona distribution..."
                  rows={6}
                  style={{ marginTop: 8 }}
                  disabled={loading}
                />
              </div>
              
              <Button 
                type="primary" 
                size="large"
                onClick={handleSubmit}
                loading={loading}
                disabled={!prompt.trim()}
                block
              >
                {loading ? 'Generating...' : 'Generate Persona Distribution'}
              </Button>

              <div style={{ marginTop: 16 }}>
                <Text strong>Sample Prompts</Text>
                <Space direction="vertical" style={{ width: '100%', marginTop: 8 }}>
                  {samplePrompts.map((sample, index) => (
                    <Card key={index} size="small" style={{ background: '#f9f9f9' }}>
                      <Space align="start" style={{ width: '100%', justifyContent: 'space-between' }}>
                        <Text style={{ fontSize: 13, color: '#666' }}>{sample}</Text>
                        <Button 
                          size="small" 
                          type="link" 
                          onClick={() => setPrompt(sample)}
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
            <Card title="Generated Persona Distribution">
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <div>
                  <Text strong>Response:</Text>
                  <Paragraph style={{ 
                    whiteSpace: 'pre-wrap', 
                    background: '#f5f5f5', 
                    padding: 16, 
                    borderRadius: 8,
                    marginTop: 8 
                  }}>
                    {result.response_text}
                  </Paragraph>
                </div>

                {result.parsed_output && (
                  <div>
                    <Text strong>Parsed Output:</Text>
                    <Paragraph>
                      <pre style={{ 
                        background: '#e6f7ff', 
                        padding: '12px', 
                        borderRadius: '4px',
                        whiteSpace: 'pre-wrap',
                        wordWrap: 'break-word'
                      }}>
                        {JSON.stringify(result.parsed_output, null, 2)}
                      </pre>
                    </Paragraph>
                  </div>
                )}

                <Space size="large" wrap>
                  <div>
                    <Text type="secondary">Tokens Used: </Text>
                    <Text strong>{result.tokens_used || 'N/A'}</Text>
                  </div>
                  <div>
                    <Text type="secondary">Time Taken: </Text>
                    <Text strong>{Math.round(result.time_taken_ms)} ms</Text>
                  </div>
                  <div>
                    <Text type="secondary">Model: </Text>
                    <Text strong>{result.agent_details.model_deployment_name}</Text>
                  </div>
                  <div>
                    <Text type="secondary">Agent: </Text>
                    <Text strong>{result.agent_details.agent_name}</Text>
                  </div>
                </Space>
              </Space>
            </Card>
          )}
        </Space>
      ),
    },
    {
      key: 'history',
      label: 'History',
      children: (
        <Card 
          title="History"
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
            rowKey={(record) => record.id || record.timestamp}
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
                <div>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div>
                      <Text strong>Prompt:</Text>
                      <Paragraph>{record.prompt}</Paragraph>
                    </div>
                    <div>
                      <Text strong>Response:</Text>
                      <Paragraph>
                        <pre style={{ 
                          background: '#f5f5f5', 
                          padding: '12px', 
                          borderRadius: '4px',
                          whiteSpace: 'pre-wrap',
                          wordWrap: 'break-word'
                        }}>
                          {record.response}
                        </pre>
                      </Paragraph>
                    </div>
                    {record.parsed_output && (
                      <div>
                        <Text strong>Parsed Output:</Text>
                        <Paragraph>
                          <pre style={{ 
                            background: '#e6f7ff', 
                            padding: '12px', 
                            borderRadius: '4px',
                            whiteSpace: 'pre-wrap',
                            wordWrap: 'break-word'
                          }}>
                            {JSON.stringify(record.parsed_output, null, 2)}
                          </pre>
                        </Paragraph>
                      </div>
                    )}
                  </Space>
                </div>
              ),
            }}
          />
        </Card>
      ),
    },
    {
      key: 'evals',
      label: 'Prepare for Evals',
      children: (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Card 
            title="Select Runs for Evals Preparation"
            extra={
              <Button 
                icon={<ReloadOutlined />} 
                onClick={() => loadEvalsHistory(evalsData?.page || 1, evalsData?.page_size || 10)}
                loading={evalsLoading}
              >
                Reload
              </Button>
            }
          >
            {evalsError && (
              <Alert message="Error" description={evalsError} type="error" showIcon style={{ marginBottom: 16 }} />
            )}
            
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <Alert
                message="About Evals Preparation"
                description="Select multiple persona distribution runs below to combine them into a CXA AI Evals dataset. The system will generate evaluation config and input data files that you can download for use in the CXA AI Evals framework."
                type="info"
                showIcon
                style={{ marginBottom: 16 }}
              />
              
              <Table
                dataSource={evalsData?.items || []}
                columns={columns}
                loading={evalsLoading}
                rowKey={(record) => record.id || record.timestamp}
                rowSelection={{
                  selectedRowKeys: selectedRunIds,
                  onChange: (selectedKeys) => setSelectedRunIds(selectedKeys as string[]),
                  getCheckboxProps: (record) => ({
                    name: record.id,
                  }),
                }}
                pagination={{
                  current: evalsData?.page || 1,
                  pageSize: evalsData?.page_size || 10,
                  total: evalsData?.total_count || 0,
                  showSizeChanger: true,
                  showTotal: (total) => `Total ${total} items`,
                  onChange: (page, pageSize) => loadEvalsHistory(page, pageSize),
                }}
              />
              
              <Button
                type="primary"
                size="large"
                onClick={handlePrepareEvals}
                loading={preparingEvals}
                disabled={selectedRunIds.length === 0}
                block
                style={{ marginTop: 16 }}
              >
                {preparingEvals ? 'Preparing Evals...' : `Prepare Evals from ${selectedRunIds.length} Selected Run(s)`}
              </Button>
            </Space>
          </Card>

          {preparedEvals && (
            <Card title="Prepared Evals Data" style={{ marginTop: 16 }}>
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <Alert
                  message="Evals Prepared Successfully!"
                  description={`Successfully prepared evals from ${preparedEvals.source_run_ids.length} runs with ${preparedEvals.cxa_evals_input_data.length} personas. Download the files below to use in CXA AI Evals framework.`}
                  type="success"
                  showIcon
                />
                
                <Space size="middle" wrap style={{ width: '100%', justifyContent: 'center' }}>
                  <Button
                    type="primary"
                    icon={<DownloadOutlined />}
                    size="large"
                    onClick={() => downloadJSON(preparedEvals.cxa_evals_config, 'cxa_evals_config.json')}
                  >
                    Download Config JSON
                  </Button>
                  
                  <Button
                    type="primary"
                    icon={<DownloadOutlined />}
                    size="large"
                    onClick={() => downloadJSON(preparedEvals.cxa_evals_input_data, 'cxa_evals_input_data.json')}
                  >
                    Download Input Data JSON
                  </Button>
                </Space>

                <div style={{ marginTop: 16 }}>
                  <Text strong>Evals ID:</Text> <Text code>{preparedEvals.evals_id}</Text>
                </div>
                
                <div>
                  <Text strong>Timestamp:</Text> <Text>{new Date(preparedEvals.timestamp).toLocaleString()}</Text>
                </div>
                
                <div>
                  <Text strong>Source Run IDs:</Text>
                  <ul style={{ marginTop: 8 }}>
                    {preparedEvals.source_run_ids.map(id => (
                      <li key={id}><Text code>{id}</Text></li>
                    ))}
                  </ul>
                </div>

                <div>
                  <Text strong>Config Preview:</Text>
                  <pre style={{ 
                    background: '#f5f5f5', 
                    padding: '12px', 
                    borderRadius: '4px',
                    maxHeight: '300px',
                    overflow: 'auto',
                    marginTop: 8
                  }}>
                    {JSON.stringify(preparedEvals.cxa_evals_config, null, 2)}
                  </pre>
                </div>

                <div>
                  <Text strong>Input Data Preview (first 3 personas):</Text>
                  <pre style={{ 
                    background: '#e6f7ff', 
                    padding: '12px', 
                    borderRadius: '4px',
                    maxHeight: '300px',
                    overflow: 'auto',
                    marginTop: 8
                  }}>
                    {JSON.stringify(preparedEvals.cxa_evals_input_data.slice(0, 3), null, 2)}
                  </pre>
                </div>
              </Space>
            </Card>
          )}
        </Space>
      ),
    },
  ]

  return (
    <PageLayout
      title="Persona Distribution Generator"
      description="Generate persona distributions from simulation prompts using the PersonaDistributionGeneratorAgent."
      showBackButton
    >
      <Tabs 
        defaultActiveKey="generate" 
        items={tabItems}
        onChange={(key) => {
          if (key === 'history' && !historyData) {
            loadHistory(1)
          }
          if (key === 'evals' && !evalsData) {
            loadEvalsHistory(1)
          }
        }}
      />
    </PageLayout>
  )
}
