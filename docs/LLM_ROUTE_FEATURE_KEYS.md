# HTTP routes → credit `feature_key` mapping

All paths are under the **same base** as the live API (typically `https://<host>/api/v1/...` locally `http://127.0.0.1:8000/api/v1/...`).

Values must match rows in `feature_credit_costs` (see `a9b8c7d6e5f4_create_credit_system_tables.py` and follow-up seeds). Code constants: `app/domains/subscriptions/feature_keys.py`.

| HTTP route | Method | Mechanism | `feature_key` | Notes |
|------------|--------|-----------|-----------------|-------|
| `/api/v1/chatbots/{slug}/messages` | POST | `MessageService` → `ModelRouter` | `chatbot_message` | Sync chat |
| `/api/v1/chatbots/{slug}/messages/stream` | POST | `MessageService.stream_message` | `chatbot_message` | SSE / credits charged after stream |
| `/api/v1/chatbots/{slug}/capabilities/{capability_key}` | POST | `CapabilityService` | `chatbot_capability` | Specialist tools |
| `/api/v1/templates/{slug}/execute` | POST | `ExecutionService` | `template_generate` | Charge only if authenticated |
| `/api/v1/templates/{slug}/execute-stream` | POST | `ExecutionService.execute_stream` | `template_generate` | 402 before stream opens |
| `/api/v1/pixgen/generate` (alias `/generate`) | POST | OpenAI Images | `pixgen_image` | Per image |
| `/api/v1/pixgen/generate-batch` | POST | OpenAI Images | `pixgen_image` | Per image in batch |
| `/api/v1/youtube-quiz/generate` | POST | `YouTubeQuizService` → `ModelRouter` | `quiz_generate` | Requires auth |
| `/api/v1/worksheets/generate` | POST | `WorksheetService` | `worksheet_generate` | See `content_ingestion/routes.py` (`router` prefix `/api/v1`) |
| `/api/v1/content-factory/generate/micro-course` | POST | `ContentFactoryService` (admin) | `content_gap_fill` | `super_admin` / `org_admin` |

**Seeded but not a separate charge path today**

- `chatbot_message_search` — reserved in DB for a future “web search” chat mode; current chat paths charge `chatbot_message` only.

**Not metered as per-click credits (policy)**

- Personalization / hub **background workers** (e.g. inventory expansion) — subscription / internal policy; not `402` on user HTTP calls.
- **Embeddings** and document ingestion pipelines — operational; not in this user-click credit map.

When adding a new user-triggered LLM or image call, add or reuse a `feature_key`, seed its cost, and return **402** with `insufficient_credits_detail` on failure to match templates and chat.
