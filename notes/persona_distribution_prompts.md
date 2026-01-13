# Persona Distribution Test Prompts (30 Total)

## Existing Prompts (12)

### 1. Multi-Intent with Behavior Mix
Simulate realistic phone conversations for these intents: billing inquiry, password reset, order status, and product return. For each intent, generate a mix of caller personas: 40% calm/clear, 30% confused/needing clarification, 20% frustrated/raised-voice, and 10% mildly abusive or impatient. Include variations in phrasing, interruptions, and multi-turn clarifications. Execute these conversations against the configured Voice Agent and routing, calling the contact center number +1-800-555-0100 for each simulated interaction. Return the default KPI scorecard

### 2. Commercial Banking Workstream Test
I've updated my Voice Agent for the Commercial Banking workstream. Please simulate phone conversations to test the against all possible customer queries—make sure the scenarios cover a wide range of intents and varied customer behaviours, including calm, frustrated, and others. You can call the contact center number at +1-812‑415‑2345.

### 3. Telecom Workstream with Specific Intents
I have a workstream tied to the phone number: +1-545-467-4683. Incoming customer calls route into multiple queues and are then assigned to service representatives. Customers calling this number typically raise Telecom-related issues such as Delayed delivery, New connection, Setup issues, and other support queries. Please simulate at least 20 voice calls covering these intents (with varied customer behaviours) and report the KPIs for each simulated conversation as well as an overall summary.

### 4. Historical Conversation IDs Transcript-Based
I've made a few updates to the workstream associated with the phone number +1-564-653-4654. Below is a set of 10 distinct conversation IDs that were previously routed and handled by this contact center. Review each of these conversations and simulate new conversations of the same type to evaluate whether there is any KPI impact. Please do not replay the historical calls—instead, extract the core customer problem or intent and behaviours from them and generate fresh synthetic conversations. If any customer details are required during simulation, you may pull them from the original transcripts of these historical conversations. The 10 historical conversation IDs are: a3f9d2b0-47c1-4e6e-9b52-ec7adf91c3a4 c87b11fe-0a9d-4e2e-8f33-54b2cba61f8c f1290e7d-92ab-45cc-bc01-7de4f6d93b55 d54a7e1c-3fef-49c8-a202-9b441cb89e61 b690ff42-07d8-4d26-9c8a-0a3d3ea1fbf0 e23c9bd9-5d2c-4c94-b85c-92b8b51ad813 9af44d0a-8d6b-4eb2-8d39-001f2b7b0e72 7c91be6e-6fda-4e17-8e0b-5d414dce92f1 06df3c11-1c2e-49a1-9bb1-3846b6924c0e fb8e5b7d-2ec0-4f7a-9214-a9e6c64d0d48

### 5. Load Test with 50 Concurrent Calls
I want to load‑test my workstream using the phone number +1-456-465-6545 with 50 concurrent inbound voice calls. The calls can be related to any type of customer issue. At the end of the simulation, show me the KPI scorecard.

### 6. Specific Issue Validation - Contoso Flowers
I suspect my voice agent isn't correctly handling New Order and Refund queries for Contoso Flowers customers. Can you validate whether this issue is real?

### 7. Historical Transcripts from Genesys
Attached are eight historical transcripts from my previous Genesys contact center. Please review these transcripts and simulate similar conversations on the phone number +1 524‑556‑3526. Share the bot's containment rate, conversation wait times, and handle times at the end of the simulation.

### 8. General Contact Center Setup Test
Test my entire contact center setup and tell me if there is any problem

### 9. Out of Scope - Singing
Can you sing a song calling the phone number +1-545-454-5457

### 10. Chat Workstream Test
Please test the ContosoChat workstream. The chat app ID is b09a747c-3f24-4161-a11c-dca176ece9e9

### 11. Multi-Intent with KPI Metrics
Simulate realistic phone conversations for these intents: billing inquiry, password reset, order status, and product return. For each intent, generate a mix of caller personas. Execute all simulated calls against the configured Voice Agent and routing by dialing +1‑800‑555‑0100 for every interaction. At the end of the simulation, provide a KPI scorecard that includes: session rejection rate, number of transfers between representatives, and the count of representatives who accepted the conversations.

### 12. E-commerce Returns and Exchanges
Generate 30 customer support conversations for an e-commerce platform. The distribution should be: 45% product returns (negative sentiment), 25% shipping inquiries (neutral sentiment), 20% refund questions (frustrated sentiment), and 10% general inquiries (positive sentiment). Route calls to +1-888-300-1000.

---

## Additional Prompts (18 New)

### 13. Healthcare Appointment Scheduling
Create a simulation for a healthcare provider's scheduling system. Generate 50 calls with the following distribution: 35% appointment scheduling (calm/patient), 25% appointment rescheduling (neutral/busy), 20% appointment cancellation (frustrated/rushed), 15% insurance questions (confused/cautious), and 5% emergency callbacks (urgent/stressed). Call the clinic at +1-617-555-2000.

### 14. Utility Company Billing Issues
Simulate 40 inbound calls for a utility company on the number +1-713-555-4500. Include these intents: 50% billing disputes (mostly angry customers), 25% service disconnection prevention (panicked), 15% meter reading questions (neutral), and 10% account setup (helpful/polite). Prioritize realistic interruptions and hold-time scenarios.

### 15. SaaS Product Support Mix
I've deployed version 3.2 of our support chatbot for our SaaS platform. Please generate 60 conversations with the following distribution: 40% technical issues (frustrated developers), 30% license/billing questions (impatient CFOs), 20% feature usage questions (curious/interested), and 10% onboarding help (new users, patient). Direct calls to +1-415-555-8000.

### 16. Insurance Claims Processing
Create a simulation for an insurance claims center at +1-305-555-7700. Generate 75 calls covering: 40% new claim submissions (anxious/stressed), 30% claim status updates (neutral/business-like), 20% claim denial appeals (angry/determined), and 10% general information (polite/friendly). Include hold times and transfer scenarios.

### 17. Retail Store Operations
Simulate phone inquiries for a major retail chain at +1-212-555-3333. Generate 100 calls: 35% inventory checks (neutral), 30% price matching questions (budget-conscious/firm), 20% return authorizations (frustrated), 10% special order inquiries (patient/thoughtful), and 5% employee-related callbacks (neutral/professional).

### 18. Food Delivery Platform Support
Create 50 customer support conversations for a food delivery app calling +1-206-555-9000. Distribution: 40% order issues (hangry/impatient), 25% driver location questions (slightly anxious), 20% payment problems (confused/frustrated), 10% account access issues (tech-struggling), and 5% refund requests (resigned/tired).

### 19. Mortgage and Lending Services
Generate 45 conversations for a mortgage company's call center at +1-505-555-6600. Include: 35% application status inquiries (hopeful/optimistic), 30% rate lock questions (analytical/comparing), 20% documentation requests (overwhelmed/scattered), and 15% refinancing inquiries (calculated/business-like). Track sentiment shifts throughout conversations.

### 20. Travel and Hospitality Reservations
Simulate 80 booking and support calls to +1-415-555-1200 for a travel booking platform. Distribution: 40% booking modifications (uncertain/changing minds), 30% reservation confirmations (relieved), 15% cancellations with reason tracking (regretful/upset), and 15% upgrade requests (hopeful). Include multi-call scenarios.

### 21. Mobile Network Operator Churn Prevention
I need to test our churn prevention team's effectiveness. Generate 35 calls to +1-512-555-8900 where customers are already frustrated: 50% about high bills (angry), 30% about poor service quality (frustrated), and 20% threatening to switch carriers (determined to leave). Mix in a few retention successes.

### 22. Bank Account Services
Create a simulation for a retail bank's main number +1-212-555-1234. Generate 55 conversations: 30% password/account access (stressed), 25% suspicious transaction reports (alarmed), 20% balance inquiries and account info (routine), 15% loan inquiries (hopeful), and 10% fraud investigations (worried). Include security question scenarios.

### 23. Customer Onboarding - B2B
Generate 40 conversations for enterprise customer onboarding at +1-617-555-5050. Distribution: 45% technical setup questions (confused but patient), 35% user permissions and access (frustrated by complexity), 15% billing and contracts (cautious/reviewing), and 5% escalations (angry). Track successful handoffs.

### 24. Automotive Dealership Service
Simulate 60 service department calls to +1-480-555-3000. Include: 40% service appointment scheduling (neutral/busy), 25% warranty questions (concerned), 20% repair disputes/complaints (frustrated), 10% trade-in inquiries (interested), and 5% recall notifications (worried). Add variations in vehicle types.

### 25. Student Loan Repayment Support
Create 50 conversations for a student loan servicer at +1-617-555-7777. Distribution: 35% deferment/forbearance requests (stressed about finances), 30% payment plan questions (confused about options), 20% income-driven repayment setup (methodical/careful), and 15% loan consolidation inquiries (analytical). Include first-time caller scenarios.

### 26. Enterprise Software Support Escalations
Generate 30 conversations for a B2B software company's support line +1-408-555-9000. Distribution: 50% system down/critical issues (panic/urgent), 30% configuration/integration help (technical/patient), 15% licensing and contract questions (businesslike), and 5% professional services inquiries (exploratory). Track escalation patterns.

### 27. Government Benefits Verification
Simulate 45 calls to a government services line at +1-202-555-5000. Include: 40% benefit application status (anxious/dependent), 30% documentation submission questions (confused by requirements), 20% eligibility clarification (concerned about approval), and 10% language line transfers (patient translators needed). Track hold times.

### 28. Real Estate Inquiry and Qualification
Create 55 real estate inquiry calls to +1-786-555-4000. Distribution: 35% property inquiry (interested/shopping), 30% viewing/showing requests (excited), 20% price negotiation follow-ups (business-like), 10% financing questions (cautious), and 5% complaint callbacks (upset with agent). Include multiple property scenarios.

### 29. Gym and Fitness Membership
Generate 40 calls to a fitness center chain at +1-720-555-2000. Include: 35% membership sign-up interest (enthusiastic), 25% billing/subscription questions (frustrated or budget-conscious), 20% class schedule and trainer inquiries (organized), 15% cancellation requests (regretful/unmotivated), and 5% complaint resolutions (upset). Track cancellation prevention success.

### 30. Pharmaceutical Customer Service
Simulate 50 calls for a pharmaceutical customer service line at +1-844-555-1111. Distribution: 40% side effects and medication questions (worried/concerned), 30% prescription refill issues (urgent/routine), 20% insurance and coverage questions (frustrated), and 10% adverse event reporting (alarmed). Include medical sensitivity and privacy considerations.

---

## Notes on Existing Prompts

- **Prompt 9** (Sing a song) is out of scope for persona distribution testing
- **Prompt 10** (Chat workstream) is out of scope - persona distribution is for voice/phone simulations only
- **Prompt 7** (Genesys transcripts) appears to be transcript-based but would need actual transcript files attached
- **Prompt 8** (General contact center test) is vague and would need clarification on intents and customer types

## Prompt Categories

**By Industry:**
- Financial Services: #2, #19, #22, #25
- Telecom/Utilities: #3, #21, #14
- Retail/E-commerce: #12, #18, #24, #29
- Healthcare: #13, #27
- Enterprise/B2B: #17, #23, #26
- Specialized Services: #4, #6, #11, #15, #16, #20, #28, #30

**By Simulation Type:**
- Historical/Transcript-based: #4, #7
- Load Testing: #5
- Issue Validation: #6
- Standard Multi-intent: #1, #11, #12, #13, #14, #15, #16, #17, #18, #19, #20, #21, #22, #23, #24, #25, #26, #27, #28, #29, #30

**By Call Volume:**
- Small (30-50): #3, #1, #13, #18, #19, #21, #23, #24, #25, #28, #29, #30
- Medium (51-80): #12, #14, #15, #17, #20, #22, #26, #27
- Large (81-100): #16, #17
- Load Test (50+): #5
