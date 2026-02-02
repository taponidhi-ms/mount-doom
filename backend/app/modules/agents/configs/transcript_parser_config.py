"""Configuration for Transcript Parser Agent."""

from ..config import AgentConfig
from ..instructions import TRANSCRIPT_PARSER_AGENT_INSTRUCTIONS


# Define agent configuration
AGENT_CONFIG = AgentConfig(
    agent_id="transcript_parser",
    agent_name="TranscriptParserAgent",
    display_name="Transcript Parser",
    description="Parse customer-representative transcripts to extract intent, subject, and sentiment from conversations.",
    instructions=TRANSCRIPT_PARSER_AGENT_INSTRUCTIONS,
    container_name="single_turn_conversations",
    scenario_name="TranscriptParserAgent",
    input_field="transcript",
    input_label="Transcript",
    input_placeholder="Paste the customer-representative conversation transcript to analyze...",
    sample_inputs=[
        {
            "label": "Trainer late complaint",
            "value": "Rep: Hello! How can I help you today?\nCustomer: My trainer showed up 20 minutes late to my session today, and I'm really frustrated because it threw off my whole schedule.\nRep: I'm really sorry to hear about your experience and understand how frustrating that must be; would you like me to look into this issue and see what I can do to help resolve it?\nCustomer: Yes, please look into it because this isn't the first time it's happened and I want to know what will actually be done about it.\nRep: Thank you for letting me know—I'll document your concern and follow up with your trainer's manager to ensure this is addressed; would you also like a callback once we have an update for you?\nCustomer: Yes, I need a callback because I want to know what action you'll take and if this issue will actually be fixed.\nRep: Absolutely, I will request a callback for you and make sure your issue is prioritized; can you please confirm the best phone number and time for us to reach you?\nCustomer: You can reach me at 684-379-0542, and afternoons after 2pm work best for me.",
            "category": "Valid",
            "tags": ["complaint-resolution", "upset", "trainer-issue", "callback-request", "negative-sentiment"]
        },
        {
            "label": "Cancellation due to affordability",
            "value": "Rep: Hello! How can I help you today?\nCustomer: I need to cancel my subscription because I can't afford the recurring payments anymore.\nRep: I'm sorry to hear that you're having trouble with the recurring payments. May I please have your account details so I can assist you with the cancellation?\nCustomer: Sure, my account number is 8429173056.\nRep: Thank you for providing your account number. I will begin the cancellation process for your subscription right away.Your subscription has been canceled. Is there anything else I can assist you with today?\nCustomer: No, that's all I needed, thanks for your help.",
            "category": "Valid",
            "tags": ["cancellation-request", "unmotivated", "affordability", "subscription", "quick-resolution"]
        },
        {
            "label": "Medical cancellation",
            "value": "Rep: Hello! What can I assist you with today?\nCustomer: Hi, I need to cancel my membership due to a recent medical issue that won't allow me to continue.\nRep: I'm sorry to hear about your situation, and I can help you with your membership cancellation; could you please provide your membership number or account details?\nCustomer: My membership number is 3847592016, and I really wish I didn't have to do this, but my doctor advised it.\nRep: Thank you for sharing your membership number, and I completely understand—your health comes first; I'll start the cancellation process right away and will let you know once it's complete.\nCustomer: I appreciate you helping with this—it's just hard for me to leave, but I know it's necessary right now.\nRep: I understand how difficult this must be, and I'm here to support you; if you ever decide to return, we'll be happy to welcome you back.",
            "category": "Valid",
            "tags": ["cancellation-request", "regretful", "medical-reasons", "empathetic", "supportive"]
        },
        {
            "label": "Gym membership cancellation",
            "value": "Rep: Hello! What can I assist you with today?\nCustomer: I want to cancel my gym membership because I'm not using it at all anymore.\nRep: I'm sorry to hear that you're no longer using your membership, and I can help you with the cancellation process. May I please have your membership ID or the email address linked to your account?\nCustomer: My email is msmith82@email.com, and I just want to get this canceled as soon as possible.\nRep: Thank you for providing your email, and I'll begin the cancellation process right away. For verification, may I have your full name and date of birth, please?\nCustomer: My name is Mark Smith and my date of birth is 09/12/1982.\nRep: Thank you for confirming your details, Mark. Your cancellation request is being processed, and you'll receive a confirmation email shortly. Is there anything else I can assist you with today?\nCustomer: No, I don't need anything else, just glad this is finally being taken care of.",
            "category": "Valid",
            "tags": ["cancellation-request", "unmotivated", "gym-membership", "verification", "straightforward"]
        },
        {
            "label": "Kids swim class inquiry",
            "value": "Rep: Hello! What can I assist you with today?\nCustomer: I'd like to know the schedule for kids' swim classes and which trainers will be teaching them this month.\nRep: Thank you for your interest! Could you please tell me the age group of your child, so I can provide the specific swim class schedule and trainers for this month?\nCustomer: My child is 8 years old—can you share the schedule and trainer details for that age group?\nRep: Thank you for confirming your child's age; for 8-year-olds, swim classes are held on Tuesdays and Thursdays at 4:00 PM, and the trainers this month are Coach Emily and Coach Ryan. Would you like more details or help with enrollment?\nCustomer: Could you send me a brief overview of both trainers and let me know if there are any upcoming changes to the schedule later this month?",
            "category": "Valid",
            "tags": ["class-schedule", "trainer-inquiry", "organized", "kids-program", "swim-class"]
        },
        {
            "label": "Recurring yoga class slots",
            "value": "Rep: Hello! What can I assist you with today?\nCustomer: I'd like to book recurring yoga class slots each week with the same trainer—can you let me know what's available?\nRep: Absolutely! May I have your preferred days, times, and the trainer's name so I can check the available slots for you?\nCustomer: I'd prefer Wednesdays and Fridays at 7am with Lisa Carter if she's available for those times weekly.\nRep: Thank you for sharing your preferences—I'll check Lisa Carter's availability for Wednesdays and Fridays at 7am and let you know if she has recurring slots open.Thank you for providing the details—I'll check if Lisa Carter is available at 7am on Wednesdays and Fridays each week and get right back to you.\nCustomer: Great, please let me know as soon as you confirm her availability so I can plan my schedule around those sessions.",
            "category": "Valid",
            "tags": ["class-schedule", "trainer-inquiry", "organized", "yoga", "recurring-booking"]
        },
        {
            "label": "Downgrade subscription",
            "value": "Rep: Hello! How can I help you today?\nCustomer: Hi, I'm looking to downgrade my subscription because the current plan is too expensive for me right now.\nRep: I understand, and I'd be happy to help you with downgrading your subscription—may I please have your account email address to verify your information?\nCustomer: Sure, my account email is janet.morris82@email.com.\nRep: Thank you, Janet—I've located your account. Could you please tell me which subscription plan you'd like to downgrade to?\nCustomer: I'd like to switch to the Basic plan since it's the most affordable option for me right now.\nRep: Thank you for letting me know, Janet. I will proceed to downgrade your subscription to the Basic plan and send you a confirmation email once it's complete—is there anything else I can assist you with today?\nCustomer: No, that's all for now—thanks for helping me switch, I really appreciate it.",
            "category": "Valid",
            "tags": ["billing-question", "subscription-change", "budget-conscious", "downgrade", "affordability"]
        },
        {
            "label": "Billing address update issue",
            "value": "Rep: Hello! How can I help you today?\nCustomer: I updated my billing address last week, but my statement still shows my old address—why hasn't it changed yet?\nRep: I'm sorry for the inconvenience; sometimes statements are prepared in advance, so your address update may not reflect until the next billing cycle. Would you like me to double-check that your new address is correctly updated in our system?\nCustomer: Yes, please check if my new address is actually saved, because I really need this fixed before my next statement goes out.\nRep: Absolutely, I'll verify your address now—can you please confirm the updated address you intended to save?\nCustomer: Sure, it's 2587 Willow Creek Drive, Boston, MA 02114—can you make absolutely sure this is what shows up in your system?\nRep: Thank you for confirming—I've checked, and your address is correctly saved as 2587 Willow Creek Drive, Boston, MA 02114 in our system. Your next statement should reflect the updated address.",
            "category": "Valid",
            "tags": ["billing-question", "frustrated", "address-update", "statement-issue", "verification"]
        },
        {
            "label": "Summer camp signup",
            "value": "Rep: Hello! What can I assist you with today?\nCustomer: I want to sign up for the summer camp and gym combo—could you tell me how to get started?\nRep: Absolutely! To get started, I'll need your name and preferred contact information, then I can walk you through the summer camp and gym combo registration process.\nCustomer: Great, my name is Jessica Marshall and you can reach me at 489-712-3651. What's the next step for signing up?\nRep: Thank you, Jessica! The next step is to fill out a brief registration form; would you prefer to receive it by email or complete it over the phone?\nCustomer: I'd prefer to complete it over the phone so we can get everything set up right now!\nRep: Perfect! May I confirm your age and any specific preferences or requirements for the summer camp or gym access before we proceed with the registration?\nCustomer: I'm 32 years old, and I'd love flexible gym hours—with access to the pool—plus my preference is for outdoor activities during camp.",
            "category": "Valid",
            "tags": ["membership-signup", "enthusiastic", "summer-camp", "gym-combo", "positive-sentiment"]
        },
        {
            "label": "Premium membership inquiry",
            "value": "Rep: Hello! What can I assist you with today?\nCustomer: Hi there! I'm really excited to join and wanted to learn more about your premium membership and personal training options.\nRep: Thank you for your interest! Our premium membership offers added amenities and access to exclusive classes, while our personal training provides tailored workouts with certified trainers—would you like details on pricing or specific features?\nCustomer: Yes, could you send me the pricing details for both the premium membership and the personal training packages?\nRep: Of course! Premium membership starts at $59 per month, and personal training packages begin at $40 per session—would you like information on available discounts or package options?\nCustomer: Absolutely, I'd love to hear about any discounts or package deals you have for both premium membership and personal training!",
            "category": "Valid",
            "tags": ["membership-signup", "enthusiastic", "premium-tier", "personal-training", "positive-sentiment"]
        },
        {
            "label": "Double billing complaint",
            "value": "Rep: Hello! How can I help you today?\nCustomer: I'm being charged twice every month and it's getting really frustrating, can you check why this keeps happening?\nRep: I'm sorry to hear about the duplicate charges—let me check your account details and see why this is happening. Can you please confirm your full name and the email address associated with your account?\nCustomer: My name is Jordan Peters and the email on my account is jordan.peters@gmail.com.\nRep: Thank you, Jordan. I'm pulling up your account now—can you confirm if both charges are for the same service, or are they for different products?\nCustomer: Both charges are for the exact same subscription—there's nothing extra or different, which is why this makes no sense to me.\nRep: Thank you for confirming, Jordan. I see the duplicate charges on your account, and I'll investigate further—have you signed up for the subscription more than once, or used any alternate payment methods?\nCustomer: No, I've only signed up once and always use the same credit card, so I have no idea why this keeps happening.",
            "category": "Valid",
            "tags": ["billing-question", "frustrated", "double-billing", "investigation", "negative-sentiment"]
        },
    ]
)
