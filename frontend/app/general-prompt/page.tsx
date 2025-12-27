'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Select } from '@/components/ui/select'
import { ResultDisplay } from '@/components/result-display'
import { apiClient, ModelInfo, GeneralPromptResponse } from '@/lib/api-client'

export default function GeneralPromptPage() {
  const [models, setModels] = useState<ModelInfo[]>([])
  const [selectedModel, setSelectedModel] = useState('')
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<GeneralPromptResponse | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    loadModels()
  }, [])

  const loadModels = async () => {
    const response = await apiClient.getModels()
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
    if (!selectedModel || !prompt.trim()) {
      setError('Please select a model and enter a prompt')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    const response = await apiClient.generateResponse(selectedModel, prompt)
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

        <h1 className="text-3xl font-bold mb-2">General Prompt</h1>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Get responses for any general prompt using LLM models directly.
        </p>

        <Card>
          <CardHeader>
            <CardTitle>Configure Prompt</CardTitle>
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
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Prompt</label>
                <Textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Enter your prompt..."
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
                  'Generate Response'
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {result && <ResultDisplay result={result} title="Response" />}
      </div>
    </div>
  )
}
