"""
Shared sample inputs for simulation-related agents.

This module contains a comprehensive set of sample prompts that are used by multiple agents:
- Simulation Prompt Agent
- Persona Distribution Generator Agent
- Persona Generator Agent

These prompts cover various domains, intents, sentiments, and behaviors for evaluation purposes.
"""

from typing import List, Dict, Any


# Comprehensive sample inputs for simulation-related agents
SIMULATION_SAMPLE_INPUTS: List[Dict[str, Any]] = [
    {
        "label": 'Multi-Intent with Behavior Mix',
        "value": 'Simulate realistic phone conversations for these intents: billing inquiry, password reset, order status, and product return. For each intent, generate a mix of caller personas: 40% calm/clear, 30% confused/needing clarification, 20% frustrated/raised-voice, and 10% mildly abusive or impatient. Include variations in phrasing, interruptions, and multi-turn clarifications. Execute these conversations against the configured Voice Agent and routing, calling the contact center number +1-800-555-0100 for each simulated interaction. Return the default KPI scorecard',
        "category": 'Valid',
        "tags": ['behavior-mix', 'billing', 'calm', 'confused', 'frustrated', 'impatient', 'inquiry', 'multi-intent', 'multi-turn', 'order-status', 'password-reset', 'patient', 'product-return']
    },
    {
        "label": 'Commercial Banking Workstream Test',
        "value": "I've updated my Voice Agent for the Commercial Banking workstream. Please simulate phone conversations to test the against all possible customer queries—make sure the scenarios cover a wide range of intents and varied customer behaviours, including calm, frustrated, and others. You can call the contact center number at +1-812-415-2345.",
        "category": 'Valid',
        "tags": ['banking', 'calm', 'commercial-banking', 'frustrated']
    },
    {
        "label": 'Telecom Workstream with Specific Intents',
        "value": 'I have a workstream tied to the phone number: +1-545-467-4683. Incoming customer calls route into multiple queues and are then assigned to service representatives. Customers calling this number typically raise Telecom-related issues such as Delayed delivery, New connection, Setup issues, and other support queries. Please simulate at least 20 voice calls covering these intents (with varied customer behaviours) and report the KPIs for each simulated conversation as well as an overall summary.',
        "category": 'Valid',
        "tags": ['connection', 'delivery', 'service', 'setup', 'support', 'telecom']
    },
    {
        "label": 'Historical Conversation IDs Transcript-Based',
        "value": "I've made a few updates to the workstream associated with the phone number +1-564-653-4654. Below is a set of 10 distinct conversation IDs that were previously routed and handled by this contact center. Review each of these conversations and simulate new conversations of the same type to evaluate whether there is any KPI impact. Please do not replay the historical calls—instead, extract the core customer problem or intent and behaviours from them and generate fresh synthetic conversations. If any customer details are required during simulation, you may pull them from the original transcripts of these historical conversations. The 10 historical conversation IDs are: a3f9d2b0-47c1-4e6e-9b52-ec7adf91c3a4 c87b11fe-0a9d-4e2e-8f33-54b2cba61f8c f1290e7d-92ab-45cc-bc01-7de4f6d93b55 d54a7e1c-3fef-49c8-a202-9b441cb89e61 b690ff42-07d8-4d26-9c8a-0a3d3ea1fbf0 e23c9bd9-5d2c-4c94-b85c-92b8b51ad813 9af44d0a-8d6b-4eb2-8d39-001f2b7b0e72 7c91be6e-6fda-4e17-8e0b-5d414dce92f1 06df3c11-1c2e-49a1-9bb1-3846b6924c0e fb8e5b7d-2ec0-4f7a-9214-a9e6c64d0d48",
        "category": 'Valid',
        "tags": ['conversation-id', 'historical', 'transcript-based']
    },
    {
        "label": 'Load Test with 50 Concurrent Calls',
        "value": 'I want to load-test my workstream using the phone number +1-456-465-6545 with 50 concurrent inbound voice calls. The calls can be related to any type of customer issue. At the end of the simulation, show me the KPI scorecard.',
        "category": 'Valid',
        "tags": ['load-test']
    },
    {
        "label": 'Specific Issue Validation - Contoso Flowers',
        "value": "I suspect my voice agent isn't correctly handling New Order and Refund queries for Contoso Flowers customers. Can you validate whether this issue is real?",
        "category": 'Valid',
        "tags": ['refund']
    },
    {
        "label": 'Historical Transcripts from Genesys',
        "value": "Attached are eight historical transcripts from my previous Genesys contact center. Please review these transcripts and simulate similar conversations on the phone number +1 524-556-3526. Share the bot's containment rate, conversation wait times, and handle times at the end of the simulation.",
        "category": 'Valid',
        "tags": ['historical']
    },
    {
        "label": 'General Contact Center Setup Test',
        "value": 'Test my entire contact center setup and tell me if there is any problem',
        "category": 'Valid',
        "tags": ['setup']
    },
    {
        "label": 'Out of Scope - Singing',
        "value": 'Can you sing a song calling the phone number +1-545-454-5457',
        "category": 'Valid',
        "tags": []
    },
    {
        "label": 'Chat Workstream Test',
        "value": 'Please test the ContosoChat workstream. The chat app ID is b09a747c-3f24-4161-a11c-dca176ece9e9',
        "category": 'Valid',
        "tags": []
    },
    {
        "label": 'Multi-Intent with KPI Metrics',
        "value": 'Simulate realistic phone conversations for these intents: billing inquiry, password reset, order status, and product return. For each intent, generate a mix of caller personas. Execute all simulated calls against the configured Voice Agent and routing by dialing +1-800-555-0100 for every interaction. At the end of the simulation, provide a KPI scorecard that includes: session rejection rate, number of transfers between representatives, and the count of representatives who accepted the conversations.',
        "category": 'Valid',
        "tags": ['billing', 'inquiry', 'kpi-metrics', 'multi-intent', 'order-status', 'password-reset', 'product-return']
    },
    {
        "label": 'E-commerce Returns and Exchanges',
        "value": 'Generate 30 customer support conversations for an e-commerce platform. The distribution should be: 45% product returns (negative sentiment), 25% shipping inquiries (neutral sentiment), 20% refund questions (frustrated sentiment), and 10% general inquiries (positive sentiment). Route calls to +1-888-300-1000.',
        "category": 'Valid',
        "tags": ['frustrated', 'neutral', 'positive', 'product-return', 'refund', 'support']
    },
    {
        "label": 'Healthcare Appointment Scheduling',
        "value": "Create a simulation for a healthcare provider's scheduling system. Generate 50 calls with the following distribution: 35% appointment scheduling (calm/patient), 25% appointment rescheduling (neutral/busy), 20% appointment cancellation (frustrated/rushed), 15% insurance questions (confused/cautious), and 5% emergency callbacks (urgent/stressed). Call the clinic at +1-617-555-2000.",
        "category": 'Valid',
        "tags": ['appointment', 'calm', 'cancellation', 'confused', 'frustrated', 'healthcare', 'insurance', 'neutral', 'patient', 'scheduling', 'stressed', 'urgent']
    },
    {
        "label": 'Utility Company Billing Issues',
        "value": 'Simulate 40 inbound calls for a utility company on the number +1-713-555-4500. Include these intents: 50% billing disputes (mostly angry customers), 25% service disconnection prevention (panicked), 15% meter reading questions (neutral), and 10% account setup (helpful/polite). Prioritize realistic interruptions and hold-time scenarios.',
        "category": 'Valid',
        "tags": ['angry', 'billing', 'connection', 'dispute', 'isp', 'neutral', 'panicked', 'service', 'setup', 'utility']
    },
    {
        "label": 'SaaS Product Support Mix',
        "value": "I've deployed version 3.2 of our support chatbot for our SaaS platform. Please generate 60 conversations with the following distribution: 40% technical issues (frustrated developers), 30% license/billing questions (impatient CFOs), 20% feature usage questions (curious/interested), and 10% onboarding help (new users, patient). Direct calls to +1-415-555-8000.",
        "category": 'Valid',
        "tags": ['billing', 'frustrated', 'impatient', 'onboarding', 'patient', 'saas', 'support']
    },
    {
        "label": 'Insurance Claims Processing',
        "value": 'Create a simulation for an insurance claims center at +1-305-555-7700. Generate 75 calls covering: 40% new claim submissions (anxious/stressed), 30% claim status updates (neutral/business-like), 20% claim denial appeals (angry/determined), and 10% general information (polite/friendly). Include hold times and transfer scenarios.',
        "category": 'Valid',
        "tags": ['angry', 'anxious', 'claim', 'determined', 'insurance', 'neutral', 'stressed']
    },
    {
        "label": 'Retail Store Operations',
        "value": 'Simulate phone inquiries for a major retail chain at +1-212-555-3333. Generate 100 calls: 35% inventory checks (neutral), 30% price matching questions (budget-conscious/firm), 20% return authorizations (frustrated), 10% special order inquiries (patient/thoughtful), and 5% employee-related callbacks (neutral/professional).',
        "category": 'Valid',
        "tags": ['frustrated', 'inventory', 'neutral', 'patient', 'retail']
    },
    {
        "label": 'Food Delivery Platform Support',
        "value": 'Create 50 customer support conversations for a food delivery app calling +1-206-555-9000. Distribution: 40% order issues (hangry/impatient), 25% driver location questions (slightly anxious), 20% payment problems (confused/frustrated), 10% account access issues (tech-struggling), and 5% refund requests (resigned/tired).',
        "category": 'Valid',
        "tags": ['angry', 'anxious', 'confused', 'delivery', 'food-delivery', 'frustrated', 'impatient', 'patient', 'payment', 'refund', 'support']
    },
    {
        "label": 'Mortgage and Lending Services',
        "value": "Generate 45 conversations for a mortgage company's call center at +1-505-555-6600. Include: 35% application status inquiries (hopeful/optimistic), 30% rate lock questions (analytical/comparing), 20% documentation requests (overwhelmed/scattered), and 15% refinancing inquiries (calculated/business-like). Track sentiment shifts throughout conversations.",
        "category": 'Valid',
        "tags": ['application', 'documentation', 'hopeful', 'mortgage', 'service']
    },
    {
        "label": 'Travel and Hospitality Reservations',
        "value": 'Simulate 80 booking and support calls to +1-415-555-1200 for a travel booking platform. Distribution: 40% booking modifications (uncertain/changing minds), 30% reservation confirmations (relieved), 15% cancellations with reason tracking (regretful/upset), and 15% upgrade requests (hopeful). Include multi-call scenarios.',
        "category": 'Valid',
        "tags": ['cancellation', 'hopeful', 'modification', 'regretful', 'relieved', 'reservation', 'support', 'travel', 'upgrade', 'upset']
    },
    {
        "label": 'Mobile Network Operator Churn Prevention',
        "value": "I need to test our churn prevention team's effectiveness. Generate 35 calls to +1-512-555-8900 where customers are already frustrated: 50% about high bills (angry), 30% about poor service quality (frustrated), and 20% threatening to switch carriers (determined to leave). Mix in a few retention successes.",
        "category": 'Valid',
        "tags": ['angry', 'churn', 'determined', 'frustrated', 'mobile-network', 'service']
    },
    {
        "label": 'Bank Account Services',
        "value": "Create a simulation for a retail bank's main number +1-212-555-1234. Generate 55 conversations: 30% password/account access (stressed), 25% suspicious transaction reports (alarmed), 20% balance inquiries and account info (routine), 15% loan inquiries (hopeful), and 10% fraud investigations (worried). Include security question scenarios.",
        "category": 'Valid',
        "tags": ['fraud', 'hopeful', 'loan', 'retail', 'service', 'stressed', 'worried']
    },
    {
        "label": 'Customer Onboarding - B2B',
        "value": 'Generate 40 conversations for enterprise customer onboarding at +1-617-555-5050. Distribution: 45% technical setup questions (confused but patient), 35% user permissions and access (frustrated by complexity), 15% billing and contracts (cautious/reviewing), and 5% escalations (angry). Track successful handoffs.',
        "category": 'Valid',
        "tags": ['angry', 'billing', 'confused', 'enterprise', 'escalation', 'frustrated', 'onboarding', 'patient', 'setup']
    },
    {
        "label": 'Automotive Dealership Service',
        "value": 'Simulate 60 service department calls to +1-480-555-3000. Include: 40% service appointment scheduling (neutral/busy), 25% warranty questions (concerned), 20% repair disputes/complaints (frustrated), 10% trade-in inquiries (interested), and 5% recall notifications (worried). Add variations in vehicle types.',
        "category": 'Valid',
        "tags": ['appointment', 'automotive', 'dispute', 'frustrated', 'isp', 'neutral', 'scheduling', 'service', 'worried']
    },
    {
        "label": 'Student Loan Repayment Support',
        "value": 'Create 50 conversations for a student loan servicer at +1-617-555-7777. Distribution: 35% deferment/forbearance requests (stressed about finances), 30% payment plan questions (confused about options), 20% income-driven repayment setup (methodical/careful), and 15% loan consolidation inquiries (analytical). Include first-time caller scenarios.',
        "category": 'Valid',
        "tags": ['confused', 'loan', 'payment', 'service', 'setup', 'stressed', 'student-loan', 'support']
    },
    {
        "label": 'Enterprise Software Support Escalations',
        "value": "Generate 30 conversations for a B2B software company's support line +1-408-555-9000. Distribution: 50% system down/critical issues (panic/urgent), 30% configuration/integration help (technical/patient), 15% licensing and contract questions (businesslike), and 5% professional services inquiries (exploratory). Track escalation patterns.",
        "category": 'Valid',
        "tags": ['enterprise', 'escalation', 'patient', 'service', 'support', 'urgent']
    },
    {
        "label": 'Government Benefits Verification',
        "value": 'Simulate 45 calls to a government services line at +1-202-555-5000. Include: 40% benefit application status (anxious/dependent), 30% documentation submission questions (confused by requirements), 20% eligibility clarification (concerned about approval), and 10% language line transfers (patient translators needed). Track hold times.',
        "category": 'Valid',
        "tags": ['anxious', 'application', 'confused', 'documentation', 'government', 'patient', 'service', 'verification']
    },
    {
        "label": 'Real Estate Inquiry and Qualification',
        "value": 'Create 55 real estate inquiry calls to +1-786-555-4000. Distribution: 35% property inquiry (interested/shopping), 30% viewing/showing requests (excited), 20% price negotiation follow-ups (business-like), 10% financing questions (cautious), and 5% complaint callbacks (upset with agent). Include multiple property scenarios.',
        "category": 'Valid',
        "tags": ['excited', 'inquiry', 'qualification', 'real-estate', 'upset']
    },
    {
        "label": 'Gym and Fitness Membership',
        "value": 'Generate 40 calls to a fitness center chain at +1-720-555-2000. Include: 35% membership sign-up interest (enthusiastic), 25% billing/subscription questions (frustrated or budget-conscious), 20% class schedule and trainer inquiries (organized), 15% cancellation requests (regretful/unmotivated), and 5% complaint resolutions (upset). Track cancellation prevention success.',
        "category": 'Valid',
        "tags": ['billing', 'cancellation', 'fitness', 'frustrated', 'gym', 'membership', 'regretful', 'upset']
    },
    {
        "label": 'Pharmaceutical Customer Service',
        "value": 'Simulate 50 calls for a pharmaceutical customer service line at +1-844-555-1111. Distribution: 40% side effects and medication questions (worried/concerned), 30% prescription refill issues (urgent/routine), 20% insurance and coverage questions (frustrated), and 10% adverse event reporting (alarmed). Include medical sensitivity and privacy considerations.',
        "category": 'Valid',
        "tags": ['adverse-event', 'frustrated', 'insurance', 'pharmaceutical', 'refill', 'service', 'urgent', 'worried']
    },
    {
        "label": 'Transcript-Based with Historical IDs',
        "value": "I've reviewed the following historical conversation IDs from our system and need to simulate similar interactions. Please analyze these conversations: a3f9d2b0-47c1-4e6e-9b52-ec7adf91c3a4 c87b11fe-0a9d-4e2e-8f33-54b2cba61f8c f1290e7d-92ab-45cc-bc01-7de4f6d93b55 d54a7e1c-3fef-49c8-a202-9b441cb89e61. Extract the intents and customer behaviors from these historical conversations and generate fresh synthetic conversations based on the patterns you observe.",
        "category": 'Invalid',
        "tags": ['conversation-id', 'historical', 'transcript-based']
    },
    {
        "label": 'Transcript-Based with Transcript Reference',
        "value": 'Attached are the transcripts from my previous contact center. Please review these conversation transcripts and simulate new conversations that follow the same patterns. Focus on customer sentiment and intent extraction from the historical data.',
        "category": 'Invalid',
        "tags": ['historical', 'transcript-based']
    },
    {
        "label": 'Transcript-Based Explicit Mention',
        "value": 'I need to simulate based on transcript #5678. Can you extract the customer intent and sentiment profile from the historical transcript and generate similar conversations for testing?',
        "category": 'Invalid',
        "tags": ['historical', 'transcript-based']
    },
    {
        "label": 'Mixed Valid and Invalid - Transcript Reference',
        "value": 'Review these historical conversations: 9af44d0a-8d6b-4eb2-8d39-001f2b7b0e72 7c91be6e-6fda-4e17-8e0b-5d414dce92f1. Extract the core customer problems and behaviors, then generate fresh synthetic conversations of the same type to test against the updated version of my contact center.',
        "category": 'Invalid',
        "tags": ['historical']
    },
    {
        "label": 'Transcript-Based with Previous Calls',
        "value": 'I have data from 15 previous calls that were handled by our contact center. Please review these existing conversation IDs and use them as a basis to simulate new conversations with similar intents and customer behaviors.',
        "category": 'Invalid',
        "tags": ['conversation-id', 'transcript-based']
    },
    {
        "label": 'ISP Technical Support',
        "value": 'Simulate 20 calls for ISP router setup issues to +1-800-123-4567. Mix 50% technical (neutral), 30% connection failure (angry), 20% general questions.',
        "category": 'Valid',
        "tags": ['angry', 'connection', 'isp', 'neutral', 'setup', 'support', 'technical-support']
    },
    {
        "label": 'Credit Card Fraud Audit',
        "value": 'Generate 15 credit card fraud report calls. 80% panicked/anxious, 20% methodical. Call center: +1-212-999-8888.',
        "category": 'Valid',
        "tags": ['anxious', 'credit-card', 'fraud', 'panicked']
    },
    {
        "label": 'Hotel Booking Modification',
        "value": 'Simulate 25 calls to hotel reservation line +1-407-555-0199. Focus on date changes (nervous), upgrades (excited), and cancellations (disappointed).',
        "category": 'Valid',
        "tags": ['cancellation', 'excited', 'hotel', 'modification', 'reservation', 'upgrade']
    },
    {
        "label": 'University Admissions Help',
        "value": 'Create 60 calls for university admissions +1-617-555-0200. Topics: Application status (anxious), scholarship info (hopeful), deadline extension (desperate).',
        "category": 'Valid',
        "tags": ['anxious', 'application', 'hopeful', 'university']
    },
    {
        "label": 'Pet Insurance Claims',
        "value": 'Generate 30 calls for pet insurance +1-888-738-9999. 40% new claim (worried), 30% coverage check (curious), 30% claim denial (angry).',
        "category": 'Valid',
        "tags": ['angry', 'claim', 'insurance', 'pet-insurance', 'worried']
    },
    {
        "label": 'Single Historical ID Replay',
        "value": 'Replay the scenario from ID: 6ba7b810-9dad-11d1-80b4-00c04fd430c8 exactly.',
        "category": 'Invalid',
        "tags": ['historical']
    },
    {
        "label": 'Batch Historical IDs',
        "value": 'Analyze these calls: 123e4567-e89b-12d3-a456-426614174000, 223e4567-e89b-12d3-a456-426614174001 and gen new ones.',
        "category": 'Invalid',
        "tags": ['historical']
    },
    {
        "label": 'Transcript Analysis',
        "value": 'Review the attached transcript file and create a simulation based on it.',
        "category": 'Invalid',
        "tags": []
    },
    {
        "label": 'Previous Call Data',
        "value": 'Use the previous 10 calls from the database to model the new simulation.',
        "category": 'Invalid',
        "tags": []
    },
    {
        "label": 'GUID Reference',
        "value": 'Simulate a conversation mirroring ID: 550e8400-e29b-41d4-a716-446655440000.',
        "category": 'Invalid',
        "tags": []
    },
    {
        "label": 'Weather Inquiry',
        "value": 'What is the weather like in Seattle today?',
        "category": 'Irrelevant',
        "tags": ['inquiry']
    },
    {
        "label": 'Recipe Request',
        "value": 'Can you give me a recipe for chocolate chip cookies?',
        "category": 'Irrelevant',
        "tags": []
    },
    {
        "label": 'Coding Task',
        "value": 'Write a Python script to sort a list of numbers.',
        "category": 'Irrelevant',
        "tags": []
    },
    {
        "label": 'Personal Assistant',
        "value": 'Remind me to buy milk at 5 PM.',
        "category": 'Irrelevant',
        "tags": []
    },
    {
        "label": 'Abusive Content',
        "value": 'You are stupid and useless. I hate this service.',
        "category": 'Irrelevant',
        "tags": ['service']
    },
]
