'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { ResultDisplay } from '@/components/result-display'
import { apiClient, ModelInfo, ConversationSimulationResponse } from '@/lib/api-client'

export default function ConversationSimulationPage() {
  const [models, setModels] = useState<ModelInfo[]>([])
  const [selectedModel, setSelectedModel] = useState('gpt-4')
  const [customerIntent, setCustomerIntent] = useState('')
  const [customerSentiment, setCustomerSentiment] = useState('')
  const [conversationSubject, setConversationSubject] = useState('')
  const [maxTurns, setMaxTurns] = useState(10)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ConversationSimulationResponse | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    loadModels()
  }, [])

  const loadModels = async () => {
    const response = await apiClient.getConversationModels()
    if (response.data) {
      setModels(response.data.models)
      if (response.data.models.length > 0) {
        setSelectedModel(response.data.models[0].model_id)
      }
    } else if (response.error) {
      setError(`Failed to load models: ${response.error}`)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedModel || !customerIntent || !customerSentiment || !conversationSubject) {
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
      {
        CustomerIntent: customerIntent,
        CustomerSentiment: customerSentiment,
        ConversationSubject: conversationSubject,
      },
      selectedModel,
      maxTurns
    )
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
        <Link href="/" className="inline-flex items-center text-sm text-gray-600 dark:text-gray-400 hover:text-foreground mb-6">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Home
        </Link>

        <h1 className="text-3xl font-bold mb-2">Conversation Simulation</h1>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Simulate multi-turn conversations between C1Agent (customer service representative) and C2Agent (customer).
        </p>

        <Card>
          <CardHeader>
            <CardTitle>Configure Simulation</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Select Model</label>
                <Select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  disabled={loading || models.length === 0}
                >
                  {models.length === 0 ? (
                    <option>No models available</option>
                  ) : (
                    models.map((model) => (
                      <option key={model.model_id} value={model.model_id}>
                        {model.model_name} {model.description && `- ${model.description}`}
                      </option>
                    ))
                  )}
                </Select>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  This model will be used for both C1Agent and C2Agent
                </p>
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
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
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
                  !selectedModel ||
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
