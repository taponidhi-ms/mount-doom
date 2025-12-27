'use client'

import { Copy, Check } from 'lucide-react'
import { useState } from 'react'
import { Button } from './ui/button'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'

interface ResultDisplayProps {
  result: any
  title?: string
}

export function ResultDisplay({ result, title = "Result" }: ResultDisplayProps) {
  const [copied, setCopied] = useState(false)

  const copyToClipboard = () => {
    navigator.clipboard.writeText(JSON.stringify(result, null, 2))
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (!result) return null

  return (
    <Card className="mt-6">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>{title}</CardTitle>
        <Button
          variant="outline"
          size="sm"
          onClick={copyToClipboard}
          className="flex items-center gap-2"
        >
          {copied ? (
            <>
              <Check className="h-4 w-4" />
              Copied!
            </>
          ) : (
            <>
              <Copy className="h-4 w-4" />
              Copy JSON
            </>
          )}
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Response Text */}
          {result.response_text && (
            <div>
              <h3 className="font-semibold mb-2">Response:</h3>
              <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-md whitespace-pre-wrap">
                {result.response_text}
              </div>
            </div>
          )}

          {/* Conversation History */}
          {result.conversation_history && (
            <div>
              <h3 className="font-semibold mb-2">Conversation History:</h3>
              <div className="space-y-2">
                {result.conversation_history.map((msg: any, idx: number) => (
                  <div
                    key={idx}
                    className={`p-3 rounded-md ${
                      msg.role === 'C1Agent'
                        ? 'bg-blue-50 dark:bg-blue-950'
                        : 'bg-green-50 dark:bg-green-950'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-sm">
                        {msg.role === 'C1Agent' ? '🎧 Customer Service Rep' : '👤 Customer'}
                      </span>
                      <span className="text-xs text-gray-600 dark:text-gray-400">
                        {msg.time_taken_ms.toFixed(0)}ms
                        {msg.tokens_used && ` • ${msg.tokens_used} tokens`}
                      </span>
                    </div>
                    <p className="text-sm">{msg.message}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-100 dark:bg-gray-800 rounded-md">
            {result.tokens_used !== undefined && (
              <div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Tokens Used</div>
                <div className="text-lg font-semibold">{result.tokens_used || 'N/A'}</div>
              </div>
            )}
            {result.total_tokens_used !== undefined && (
              <div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Total Tokens</div>
                <div className="text-lg font-semibold">{result.total_tokens_used || 'N/A'}</div>
              </div>
            )}
            {result.time_taken_ms !== undefined && (
              <div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Time Taken</div>
                <div className="text-lg font-semibold">{result.time_taken_ms.toFixed(0)}ms</div>
              </div>
            )}
            {result.total_time_taken_ms !== undefined && (
              <div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Total Time</div>
                <div className="text-lg font-semibold">
                  {(result.total_time_taken_ms / 1000).toFixed(2)}s
                </div>
              </div>
            )}
            {result.start_time && (
              <div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Start Time</div>
                <div className="text-sm font-mono">
                  {new Date(result.start_time).toLocaleTimeString()}
                </div>
              </div>
            )}
            {result.end_time && (
              <div>
                <div className="text-xs text-gray-600 dark:text-gray-400">End Time</div>
                <div className="text-sm font-mono">
                  {new Date(result.end_time).toLocaleTimeString()}
                </div>
              </div>
            )}
            {result.conversation_status && (
              <div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Status</div>
                <div className="text-lg font-semibold">{result.conversation_status}</div>
              </div>
            )}
          </div>

          {/* Full JSON */}
          <details>
            <summary className="cursor-pointer text-sm font-semibold mb-2">
              View Full JSON
            </summary>
            <pre className="p-4 bg-gray-100 dark:bg-gray-800 rounded-md text-xs overflow-auto max-h-96">
              {JSON.stringify(result, null, 2)}
            </pre>
          </details>
        </div>
      </CardContent>
    </Card>
  )
}
