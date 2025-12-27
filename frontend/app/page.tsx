import Link from 'next/link'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

export default function Home() {
  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-2">Mount Doom</h1>
        <p className="text-muted-foreground mb-8">
          AI Agent Simulation Platform - Multi-agent conversation simulation and prompt generation
        </p>

        <div className="grid gap-6 md:grid-cols-2">
          <Link href="/persona-generation">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <CardTitle>Persona Generation</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Generate personas from simulation prompts using specialized AI agents.
                  Transform your ideas into detailed character profiles.
                </p>
              </CardContent>
            </Card>
          </Link>

          <Link href="/general-prompt">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <CardTitle>General Prompt</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Get responses for any general prompt using LLM models directly.
                  Flexible AI assistance for various tasks.
                </p>
              </CardContent>
            </Card>
          </Link>

          <Link href="/prompt-validator">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <CardTitle>Prompt Validator</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Validate simulation prompts to ensure they meet quality standards.
                  Get feedback on prompt effectiveness.
                </p>
              </CardContent>
            </Card>
          </Link>

          <Link href="/conversation-simulation">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <CardTitle>Conversation Simulation</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Simulate multi-turn conversations between customer service representatives
                  and customers with intelligent orchestration.
                </p>
              </CardContent>
            </Card>
          </Link>
        </div>

        <div className="mt-12 p-6 border rounded-lg bg-muted/50">
          <h2 className="text-xl font-semibold mb-2">About This Platform</h2>
          <p className="text-sm text-muted-foreground">
            This platform leverages Azure AI Projects to provide advanced simulation capabilities.
            Each use case is powered by specialized agents and models, with full tracking of
            tokens used, response times, and conversation history. All interactions are
            automatically stored in Cosmos DB for analysis and retrieval.
          </p>
        </div>
      </div>
    </div>
  )
}
