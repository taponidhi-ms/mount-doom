'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Loader2, ChevronLeft, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { ResultDisplay } from '@/components/result-display'
import { apiClient, ModelInfo, PersonaGenerationResponse, BrowseResponse } from '@/lib/api-client'

export default function PersonaGenerationPage() {
  const [models, setModels] = useState<ModelInfo[]>([])
  const [selectedModel, setSelectedModel] = useState('gpt-4')
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<PersonaGenerationResponse | null>(null)
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

  const loadHistory = async (page: number = 1) => {
    setHistoryLoading(true)
    setHistoryError('')
    const response = await apiClient.browsePersonaGenerations(page, 10)
    setHistoryLoading(false)
    
    if (response.data) {
      setHistoryData(response.data)
      setHistoryPage(page)
    } else if (response.error) {
      setHistoryError(response.error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedModel || !prompt.trim()) {
      setError('Please select a model and enter a prompt')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    const response = await apiClient.generatePersona(prompt, selectedModel)
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

        <h1 className="text-3xl font-bold mb-2">Persona Generation</h1>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Generate personas from simulation prompts using the PersonaAgent with your choice of AI model.
        </p>

        <Tabs defaultValue="generate" className="space-y-4">
          <TabsList>
            <TabsTrigger value="generate">Generate</TabsTrigger>
            <TabsTrigger value="history" onClick={() => loadHistory(1)}>History</TabsTrigger>
          </TabsList>

          <TabsContent value="generate" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Configure Generation</CardTitle>
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
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Prompt</label>
                    <Textarea
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      placeholder="Enter your simulation prompt for persona generation..."
                      rows={6}
                      disabled={loading}
                    />
                  </div>

                  {error && (
                    <div className="p-3 bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-400 rounded-md text-sm">
                      {error}
                    </div>
                  )}

                  <Button type="submit" disabled={loading || !selectedModel || !prompt.trim()}>
                    {loading ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      'Generate Persona'
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>

            {result && <ResultDisplay result={result} title="Generated Persona" />}
          </TabsContent>

          <TabsContent value="history" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Past Generations</CardTitle>
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
                          <TableHead>Prompt</TableHead>
                          <TableHead>Response</TableHead>
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
                              {item.prompt}
                            </TableCell>
                            <TableCell className="max-w-md truncate text-sm">
                              {item.response}
                            </TableCell>
                            <TableCell className="text-sm">{item.tokens_used || 'N/A'}</TableCell>
                            <TableCell className="text-sm">{Math.round(item.time_taken_ms || 0)}</TableCell>
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
                    No past generations found
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
