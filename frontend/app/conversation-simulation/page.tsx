'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Loader2, ChevronLeft, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { apiClient, ModelInfo, ConversationSimulationResponse, BrowseResponse } from '@/lib/api-client'

export default function ConversationSimulationPage() {
  const [models, setModels] = useState<ModelInfo[]>([])
  const [selectedModel, setSelectedModel] = useState('gpt-4')
  
  // Persona selection state
  const [usePersona, setUsePersona] = useState(false)
  const [personaList, setPersonaList] = useState<BrowseResponse | null>(null)
  const [selectedPersona, setSelectedPersona] = useState<any>(null)
  const [loadingPersonas, setLoadingPersonas] = useState(false)
  
  // Manual input state
  const [customerIntent, setCustomerIntent] = useState('')
  const [customerSentiment, setCustomerSentiment] = useState('')
  const [conversationSubject, setConversationSubject] = useState('')
  
  const [maxTurns, setMaxTurns] = useState(10)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ConversationSimulationResponse | null>(null)
  const [error, setError] = useState('')
  
  // History state
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyData, setHistoryData] = useState<BrowseResponse | null>(null)
  const [historyPage, setHistoryPage] = useState(1)
  const [historyError, setHistoryError] = useState('')

  useEffect(() => {
    loadModels()
  }, [])

  const loadModels = async () => {
    const response = await apiClient.getModels()
    if (response.data) {
      setModels(response.data.models)
      if (response.data.models.length > 0) {
        setSelectedModel(response.data.models[0].model_deployment_name)
      }
    } else if (response.error) {
      setError(`Failed to load models: ${response.error}`)
    }
  }

  const loadPersonas = async () => {
    setLoadingPersonas(true)
    const response = await apiClient.browsePersonaGenerations(1, 50) // Load first 50 personas
    setLoadingPersonas(false)
    
    if (response.data) {
      setPersonaList(response.data)
    }
  }

  const loadHistory = async (page: number = 1) => {
    setHistoryLoading(true)
    setHistoryError('')
    const response = await apiClient.browseConversationSimulations(page, 10)
    setHistoryLoading(false)
    
    if (response.data) {
      setHistoryData(response.data)
      setHistoryPage(page)
    } else if (response.error) {
      setHistoryError(response.error)
    }
  }

  const handlePersonaToggle = (checked: boolean) => {
    setUsePersona(checked)
    if (checked && !personaList) {
      loadPersonas()
    }
    // Clear the other input method
    if (checked) {
      setCustomerIntent('')
      setCustomerSentiment('')
      setConversationSubject('')
    } else {
      setSelectedPersona(null)
    }
  }

  const handlePersonaSelect = (persona: any) => {
    setSelectedPersona(persona)
    // Try to extract conversation properties from persona response if available
    // For now, we'll just use the persona as is
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    let intent = customerIntent
    let sentiment = customerSentiment
    let subject = conversationSubject
    
    if (usePersona) {
      if (!selectedPersona) {
        setError('Please select a persona')
        return
      }
      // Extract properties from persona if available, otherwise use generic values
      intent = customerIntent || 'Based on persona'
      sentiment = customerSentiment || 'Based on persona'
      subject = conversationSubject || selectedPersona.response?.substring(0, 100) || 'Based on persona'
    } else {
      if (!intent || !sentiment || !subject) {
        setError('Please fill in all customer persona fields')
        return
      }
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
        CustomerIntent: intent,
        CustomerSentiment: sentiment,
        ConversationSubject: subject,
      },
      '', // No conversation_prompt based on requirements
      maxTurns
    )
    setLoading(false)

    if (response.data) {
      setResult(response.data)
      // Reload history to show the new result
      loadHistory(1)
    } else if (response.error) {
      setError(response.error)
    }
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <Link href="/" className="inline-flex items-center text-sm text-gray-600 dark:text-gray-400 hover:text-foreground mb-6">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Home
        </Link>

        <h1 className="text-3xl font-bold mb-2">Conversation Simulation</h1>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Simulate multi-turn conversations between C1Agent (customer service representative) and C2Agent (customer).
        </p>

        <Tabs defaultValue="generate" className="space-y-4">
          <TabsList>
            <TabsTrigger value="generate">Generate</TabsTrigger>
            <TabsTrigger value="history" onClick={() => loadHistory(1)}>History</TabsTrigger>
          </TabsList>

          <TabsContent value="generate" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Configure Simulation</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Select Model</label>
                    <select
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      disabled={loading || models.length === 0}
                      className="w-full px-3 py-2 border rounded-md"
                    >
                      {models.length === 0 ? (
                        <option>No models available</option>
                      ) : (
                        models.map((model) => (
                          <option key={model.model_deployment_name} value={model.model_deployment_name}>
                            {model.display_name} {model.description && `- ${model.description}`}
                          </option>
                        ))
                      )}
                    </select>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                      This model will be used for both C1Agent and C2Agent
                    </p>
                  </div>

                  <div className="border-t pt-4">
                    <div className="flex items-center gap-2 mb-4">
                      <input
                        type="checkbox"
                        id="use-persona"
                        checked={usePersona}
                        onChange={(e) => handlePersonaToggle(e.target.checked)}
                        disabled={loading}
                        className="h-4 w-4"
                      />
                      <label htmlFor="use-persona" className="text-sm font-medium">
                        Use persona from persona generation
                      </label>
                    </div>

                    {usePersona ? (
                      <div>
                        <label className="block text-sm font-medium mb-2">Select Persona</label>
                        {loadingPersonas ? (
                          <div className="flex items-center justify-center py-4">
                            <Loader2 className="h-6 w-6 animate-spin" />
                          </div>
                        ) : personaList && personaList.items.length > 0 ? (
                          <select
                            value={selectedPersona?.id || ''}
                            onChange={(e) => {
                              const persona = personaList.items.find((p: any) => p.id === e.target.value)
                              handlePersonaSelect(persona)
                            }}
                            disabled={loading}
                            className="w-full px-3 py-2 border rounded-md"
                          >
                            <option value="">-- Select a persona --</option>
                            {personaList.items.map((persona: any) => (
                              <option key={persona.id} value={persona.id}>
                                {persona.prompt?.substring(0, 80)}... ({new Date(persona.timestamp).toLocaleDateString()})
                              </option>
                            ))}
                          </select>
                        ) : (
                          <p className="text-sm text-gray-500">No personas available. Generate some first.</p>
                        )}
                        {selectedPersona && (
                          <div className="mt-2 p-3 bg-gray-50 dark:bg-gray-900 rounded-md">
                            <p className="text-sm font-medium mb-1">Selected Persona:</p>
                            <p className="text-xs text-gray-600 dark:text-gray-400 max-h-32 overflow-y-auto">
                              {selectedPersona.response}
                            </p>
                          </div>
                        )}
                      </div>
                    ) : (
                      <>
                        <div>
                          <label className="block text-sm font-medium mb-2">Customer Intent</label>
                          <Input
                            value={customerIntent}
                            onChange={(e) => setCustomerIntent(e.target.value)}
                            placeholder="e.g., Technical Support, Billing Inquiry, Product Return"
                            disabled={loading}
                          />
                        </div>

                        <div className="mt-4">
                          <label className="block text-sm font-medium mb-2">Customer Sentiment</label>
                          <Input
                            value={customerSentiment}
                            onChange={(e) => setCustomerSentiment(e.target.value)}
                            placeholder="e.g., Frustrated, Happy, Confused, Angry"
                            disabled={loading}
                          />
                        </div>

                        <div className="mt-4">
                          <label className="block text-sm font-medium mb-2">Conversation Subject</label>
                          <Input
                            value={conversationSubject}
                            onChange={(e) => setConversationSubject(e.target.value)}
                            placeholder="e.g., Product Issue, Account Problem, Feature Request"
                            disabled={loading}
                          />
                        </div>
                      </>
                    )}
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
                    disabled={loading || !selectedModel}
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

            {result && (
              <Card>
                <CardHeader>
                  <CardTitle>Conversation Result</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="font-medium">Status:</span> {result.conversation_status}
                      </div>
                      <div>
                        <span className="font-medium">Total Tokens:</span> {result.total_tokens_used || 'N/A'}
                      </div>
                      <div>
                        <span className="font-medium">Time Taken:</span> {Math.round(result.total_time_taken_ms)} ms
                      </div>
                      <div>
                        <span className="font-medium">Messages:</span> {result.conversation_history.length}
                      </div>
                    </div>
                    
                    <div className="border-t pt-4">
                      <h4 className="font-medium mb-3">Conversation History</h4>
                      <div className="space-y-3">
                        {result.conversation_history.map((msg, idx) => (
                          <div key={idx} className="border-l-4 border-gray-300 pl-3">
                            <div className="text-sm font-medium text-gray-700 dark:text-gray-300">
                              {msg.agent_name} {msg.tokens_used && `(${msg.tokens_used} tokens)`}
                            </div>
                            <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                              {msg.message}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="history" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Past Simulations</CardTitle>
              </CardHeader>
              <CardContent>
                {historyLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="h-8 w-8 animate-spin" />
                  </div>
                ) : historyError ? (
                  <div className="p-3 bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-400 rounded-md text-sm">
                    {historyError}
                  </div>
                ) : historyData && historyData.items.length > 0 ? (
                  <>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Timestamp</TableHead>
                          <TableHead>Subject</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Messages</TableHead>
                          <TableHead>Tokens</TableHead>
                          <TableHead>Time (ms)</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {historyData.items.map((item: any, idx: number) => (
                          <TableRow key={item.id || idx}>
                            <TableCell className="text-sm">
                              {new Date(item.timestamp).toLocaleString()}
                            </TableCell>
                            <TableCell className="max-w-xs truncate text-sm">
                              {item.conversation_properties?.ConversationSubject || 'N/A'}
                            </TableCell>
                            <TableCell className="text-sm">{item.conversation_status}</TableCell>
                            <TableCell className="text-sm">{item.conversation_history?.length || 0}</TableCell>
                            <TableCell className="text-sm">{item.total_tokens_used || 'N/A'}</TableCell>
                            <TableCell className="text-sm">{Math.round(item.total_time_taken_ms || 0)}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                    
                    <div className="flex items-center justify-between mt-4">
                      <div className="text-sm text-gray-600 dark:text-gray-400">
                        Page {historyData.page} of {historyData.total_pages} ({historyData.total_count} total)
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          disabled={!historyData.has_previous || historyLoading}
                          onClick={() => loadHistory(historyPage - 1)}
                        >
                          <ChevronLeft className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          disabled={!historyData.has_next || historyLoading}
                          onClick={() => loadHistory(historyPage + 1)}
                        >
                          <ChevronRight className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    No past simulations found
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
