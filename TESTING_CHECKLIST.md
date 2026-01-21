# End-to-End Testing Checklist

## Prerequisites
1. ✅ Run migrations: `alembic upgrade head`
2. ✅ Seed data: `python -m app.seed.cli --subscriptions --chatbots`
3. ✅ Start backend: `uvicorn app.main:app --reload`
4. ✅ Start frontend: `npm run dev`

## Free Chatbot (general-teaching-assistant) Testing

### ✅ Feature Gating (GPT Style)
- [ ] **Audio/Voice Button**: Should show lock icon for free users, disabled state
- [ ] **Web Search Button**: Should show lock icon for free users, disabled state  
- [ ] **File Attachment Button**: Should show lock icon for free users, disabled state
- [ ] Clicking locked features shows "Upgrade to Premium" message

### ✅ Core Functionality
- [ ] **Send Message**: Type message, click send, verify API call
- [ ] **Receive Response**: Verify response appears from backend API
- [ ] **Conversation History**: Messages persist in database
- [ ] **Load Conversations**: Previous conversations load from API on page load

### ✅ Actions Menu
- [ ] **Questions Action**: 
  - Click "Questions" in Actions menu
  - Verify prompt is generated in input field
  - Send and verify response
- [ ] **Length Setting**:
  - Click "Length" in Actions menu
  - Select Short/Medium/Long
  - Send message and verify response length matches
- [ ] **Summarize Action**:
  - Have a conversation with assistant
  - Click "Summarize" in Actions menu
  - Verify prompt is generated
  - Send and verify summary response
- [ ] **Custom Prompts**:
  - Click "Custom Prompts" in Actions menu
  - Modal opens with prompt management
  - Add new prompt and save
  - Verify prompt appears in saved list
  - Click "Use" on saved prompt - verify it populates input
  - Delete a prompt and verify it's removed

### ✅ Bot Modes
- [ ] **Fastest Mode**: Select and send message, verify faster response
- [ ] **Smartest Mode**: Select and verify balanced response
- [ ] **Critical Thinking Mode**: Select and verify deeper analysis

### ✅ Quota Display
- [ ] **Quota in Header**: Shows "Messages: X / Y" with progress bar
- [ ] **Quota Updates**: After sending message, quota count updates
- [ ] **Quota Limit**: When limit reached, shows appropriate message

### ✅ Premium Features (Should be Disabled)
- [ ] **Audio**: Button disabled with lock icon
- [ ] **Web Search**: Button disabled with lock icon
- [ ] **File Attachments**: Button disabled with lock icon
- [ ] Clicking shows upgrade message

## Premium Chatbot (literacy-lab-coach) Testing

### ✅ Access Control
- [ ] **Free User**: Should see access denied or upgrade prompt
- [ ] **Premium User**: Can access chatbot

### ✅ Capabilities
- [ ] **Text Complexity Analysis**: Execute capability, verify structured response
- [ ] **Guided Reading Strategies**: Execute capability, verify response
- [ ] **Writing Feedback**: Execute capability, verify feedback format
- [ ] **Progress Tracking**: Verify tracking updates

## API Endpoints Testing

### Chatbot APIs
- [ ] `GET /api/v1/chatbots` - List chatbots
- [ ] `GET /api/v1/chatbots/{slug}` - Get chatbot details
- [ ] `GET /api/v1/chatbots/{slug}/conversations` - List conversations
- [ ] `GET /api/v1/chatbots/conversations/{id}` - Get conversation
- [ ] `POST /api/v1/chatbots/{slug}/messages` - Send message
- [ ] `DELETE /api/v1/chatbots/conversations/{id}` - Delete conversation

### Subscription APIs
- [ ] `GET /api/v1/subscriptions/me` - Get user subscription
- [ ] `GET /api/v1/subscriptions/me/features` - Get user features
- [ ] `GET /api/v1/subscriptions/me/quotas` - Get quota summary
- [ ] `GET /api/v1/subscriptions/me/features/{feature_key}` - Check feature access

## Error Handling
- [ ] **Network Error**: Verify user-friendly error message
- [ ] **Quota Exceeded**: Verify quota limit message
- [ ] **Premium Required**: Verify upgrade prompt
- [ ] **Invalid Input**: Verify validation errors

## UI/UX Verification
- [ ] All buttons have proper tooltips
- [ ] Disabled states are visually clear (grayed out, lock icons)
- [ ] Loading states show during API calls
- [ ] Messages display correctly with timestamps
- [ ] Conversation history sidebar works
- [ ] Quota display updates in real-time

## Performance
- [ ] Messages send within reasonable time (< 5 seconds)
- [ ] Conversations load quickly (< 1 second)
- [ ] UI remains responsive during API calls
- [ ] No console errors

---

**Status**: Ready for testing after migrations and seed data
