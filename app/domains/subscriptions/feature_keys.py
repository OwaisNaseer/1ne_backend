"""
Maps API surfaces to feature_credit_costs.feature_key (seeded in alembic).

Chat stream / sync — chatbot_message (+ chatbot_message_search for web search).
Templates — template_generate.
Chatbot capabilities — chatbot_capability.
PixGen — pixgen_image.
YouTube quiz — quiz_generate.
Worksheets — worksheet_generate.
Content factory gap-fill — content_gap_fill.
"""

# Re-export string constants for call sites
CHATBOT_MESSAGE = "chatbot_message"
CHATBOT_MESSAGE_SEARCH = "chatbot_message_search"
TEMPLATE_GENERATE = "template_generate"
CHATBOT_CAPABILITY = "chatbot_capability"
PIXGEN_IMAGE = "pixgen_image"
QUIZ_GENERATE = "quiz_generate"
WORKSHEET_GENERATE = "worksheet_generate"
CONTENT_GAP_FILL = "content_gap_fill"
