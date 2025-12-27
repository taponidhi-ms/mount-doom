'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { ResultDisplay } from '@/components/result-display'
import { apiClient, AgentInfo, ConversationSimulationResponse } from '@/lib/api-client'

export default function ConversationSimulationPage() {
  const [agents, setAgents] = useState<AgentInfo[]>([])
  const [c1Agent, setC1Agent] = useState('')
  const [c2Agent, setC2Agent] = useState('')
  const [customerIntent, setCustomerIntent] = useState('')
  const [customerSentiment, setCustomerSentiment] = useState('')
  const [conversationSubject, setConversationSubject] = useState('')
  const [maxTurns, setMaxTurns] = useState(10)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ConversationSimulationResponse | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    loadAgents()
  }, [])

  const loadAgents = async () => {
    const response = await apiClient.getConversationAgents()
    if (response.data) {
      setAgents(response.data.agents)
      // Find C1 and C2 agents
      const c1 = response.data.agents.find(a => a.agent_name.includes('C1'))
      const c2 = response.data.agents.find(a => a.agent_name.includes('C2'))
      if (c1) setC1Agent(c1.agent_id)
      if (c2) setC2Agent(c2.agent_id)
    } else if (response.error) {
      setError(`Failed to load agents: ${response.error}`)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!c1Agent || !c2Agent || !customerIntent || !customerSentiment || !conversationSubject) {
      setError('Please fill in all required fields')
      return
    }

    if (maxTurns < 1 || maxTurns > 20) {
      setError('Max turns must be between 1 and 20')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    const response = await apiClient.simulateConversation(
      c1Agent,
      c2Agent,
      {
        CustomerIntent: customerIntent,
        CustomerSentiment: customerSentiment,
        ConversationSubject: conversationSubject,
      },
      maxTurns
    )
    setLoading(false)

    if (response.data) {
      setResult(response.data)
    } else if (response.error) {
      setError(response.error)
    }
  }

  // Filter agents for C1 and C2
  const c1Agents = agents.filter(a => a.agent_name.includes('C1') || a.agent_name.includes('Representative'))
  const c2Agents = agents.filter(a => a.agent_name.includes('C2') || a.agent_name.includes('Customer'))

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <Link href="/" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-6">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Home
        </Link>

        <h1 className="text-3xl font-bold mb-2">Conversation Simulation</h1>
        <p className="text-muted-foreground mb-6">
          Simulate multi-turn conversations between customer service representatives and customers.
        </p>

        <Card>
          <CardHeader>
            <CardTitle>Configure Simulation</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    C1 Agent (Customer Service Rep)
                  </label>
                  <Select
                    value={c1Agent}
                    onChange={(e) => setC1Agent(e.target.value)}
                    disabled={loading || c1Agents.length === 0}
                  >
                    {c1Agents.length === 0 ? (
                      <option>No C1 agents available</option>
                    ) : (
                      c1Agents.map((agent) => (
                        <option key={agent.agent_id} value={agent.agent_id}>
                          {agent.agent_name}
                        </option>
                      ))
                    )}
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    C2 Agent (Customer)
                  </label>
                  <Select
                    value={c2Agent}
                    onChange={(e) => setC2Agent(e.target.value)}
                    disabled={loading || c2Agents.length === 0}
                  >
                    {c2Agents.length === 0 ? (
                      <option>No C2 agents available</option>
                    ) : (
                      c2Agents.map((agent) => (
                        <option key={agent.agent_id} value={agent.agent_id}>
                          {agent.agent_name}
                        </option>
                      ))
                    )}
                  </Select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Customer Intent</label>
                <Input
                  value={customerIntent}
                  onChange={(e) => setCustomerIntent(e.target.value)}
                  placeholder="e.g., Technical Support, Billing Inquiry, Product Return"
                  disabled={loading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Customer Sentiment</label>
                <Input
                  value={customerSentiment}
                  onChange={(e) => setCustomerSentiment(e.target.value)}
                  placeholder="e.g., Frustrated, Happy, Confused, Angry"
                  disabled={loading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Conversation Subject</label>
                <Input
                  value={conversationSubject}
                  onChange={(e) => setConversationSubject(e.target.value)}
                  placeholder="e.g., Product Issue, Account Problem, Feature Request"
                  disabled={loading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Max Turns (1-20)
                </label>
                <Input
                  type="number"
                  min={1}
                  max={20}
                  value={maxTurns}
                  onChange={(e) => setMaxTurns(parseInt(e.target.value) || 10)}
                  disabled={loading}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Maximum number of conversation turns allowed
                </p>
              </div>

              {error && (
                <div className="p-3 bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-400 rounded-md text-sm">
                  {error}
                </div>
              )}

              <Button
                type="submit"
                disabled={
                  loading ||
                  !c1Agent ||
                  !c2Agent ||
                  !customerIntent ||
                  !customerSentiment ||
                  !conversationSubject
                }
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Simulating Conversation...
                  </>
                ) : (
                  'Start Simulation'
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {result && <ResultDisplay result={result} title="Conversation Simulation Result" />}
      </div>
    </div>
  )
}
