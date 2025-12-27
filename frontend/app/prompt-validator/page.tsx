'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Select } from '@/components/ui/select'
import { ResultDisplay } from '@/components/result-display'
import { apiClient, AgentInfo, PromptValidatorResponse } from '@/lib/api-client'

export default function PromptValidatorPage() {
  const [agents, setAgents] = useState<AgentInfo[]>([])
  const [selectedAgent, setSelectedAgent] = useState('')
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<PromptValidatorResponse | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    loadAgents()
  }, [])

  const loadAgents = async () => {
    const response = await apiClient.getValidatorAgents()
    if (response.data) {
      setAgents(response.data.agents)
      if (response.data.agents.length > 0) {
        setSelectedAgent(response.data.agents[0].agent_id)
      }
    } else if (response.error) {
      setError(`Failed to load agents: ${response.error}`)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedAgent || !prompt.trim()) {
      setError('Please select an agent and enter a prompt')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    const response = await apiClient.validatePrompt(selectedAgent, prompt)
    setLoading(false)

    if (response.data) {
      setResult(response.data)
    } else if (response.error) {
      setError(response.error)
    }
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <Link href="/" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-6">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Home
        </Link>

        <h1 className="text-3xl font-bold mb-2">Prompt Validator</h1>
        <p className="text-muted-foreground mb-6">
          Validate simulation prompts to ensure they meet quality standards.
        </p>

        <Card>
          <CardHeader>
            <CardTitle>Configure Validation</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Select Agent</label>
                <Select
                  value={selectedAgent}
                  onChange={(e) => setSelectedAgent(e.target.value)}
                  disabled={loading || agents.length === 0}
                >
                  {agents.length === 0 ? (
                    <option>No agents available</option>
                  ) : (
                    agents.map((agent) => (
                      <option key={agent.agent_id} value={agent.agent_id}>
                        {agent.agent_name} {agent.description && `- ${agent.description}`}
                      </option>
                    ))
                  )}
                </Select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Prompt to Validate</label>
                <Textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Enter the simulation prompt you want to validate..."
                  rows={6}
                  disabled={loading}
                />
              </div>

              {error && (
                <div className="p-3 bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-400 rounded-md text-sm">
                  {error}
                </div>
              )}

              <Button type="submit" disabled={loading || !selectedAgent || !prompt.trim()}>
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Validating...
                  </>
                ) : (
                  'Validate Prompt'
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {result && <ResultDisplay result={result} title="Validation Result" />}
      </div>
    </div>
  )
}
