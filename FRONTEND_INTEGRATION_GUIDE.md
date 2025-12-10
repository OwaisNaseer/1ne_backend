# Frontend Integration Guide - Template Streaming Endpoints

## Overview

This document provides detailed requirements and implementation guidelines for integrating template streaming endpoints in the 1ne-frontend application.

## Backend Endpoints Summary

### 1. Template Listing Endpoint
**GET** `/api/v1/templates`

**Query Parameters:**
- `subject` (optional): Filter by subject_default
- `grade_band` (optional): Filter by grade_bands_supported
- `category` (optional): Filter by TemplateCategory enum

**Response:** `List[TemplateListItem]`
```typescript
interface TemplateListItem {
  id: string; // UUID
  slug: string;
  name: string;
  description: string | null;
  category: string; // TemplateCategory enum
  subject_default: string | null;
  grade_bands_supported: string[] | null;
  is_active: boolean;
}
```

**Status Codes:**
- `200 OK`: Success
- `500 Internal Server Error`: Database error

---

### 2. Template Detail Endpoint
**GET** `/api/v1/templates/{slug}`

**Path Parameters:**
- `slug` (required): Template slug identifier

**Response:** `TemplateDetail`
```typescript
interface TemplateDetail {
  id: string; // UUID
  slug: string;
  name: string;
  description: string | null;
  category: string;
  subject_default: string | null;
  grade_bands_supported: string[] | null;
  is_system_template: boolean;
  is_active: boolean;
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
  latest_version: TemplateVersionPublic | null;
}

interface TemplateVersionPublic {
  id: string; // UUID
  version: number;
  status: string; // TemplateVersionStatus enum
  input_schema: Record<string, any>; // JSON schema for form fields
  output_schema: Record<string, any> | null;
  prompt_definition: Record<string, any> | null;
  model_config: Record<string, any> | null; // LLM model configuration
  published_at: string | null; // ISO datetime
}
```

**Status Codes:**
- `200 OK`: Success
- `404 Not Found`: Template not found or not active

---

### 3. Template Execution Endpoint (Non-Streaming)
**POST** `/api/v1/templates/{slug}/execute`

**Path Parameters:**
- `slug` (required): Template slug

**Request Body:** `TemplateExecuteRequest`
```typescript
interface TemplateExecuteRequest {
  data: Record<string, any>; // Must match template's input_schema
}
```

**Response:** `TemplateExecuteResponse`
```typescript
interface TemplateExecuteResponse {
  execution_id: string; // UUID
  template_id: string; // UUID
  template_version: number;
  output: UniversalTemplateOutput;
  model_used: string | null;
  provider_used: string | null;
  token_usage: {
    prompt: number;
    completion: number;
    total: number;
  } | null;
  latency_ms: number | null;
}

interface UniversalTemplateOutput {
  overview: string;
  learning_goals: string[];
  materials: string[];
  steps: LessonStep[];
  differentiation: string[];
  assessment: AssessmentSection | null;
  teacher_notes: string[];
  bloom_alignment: BloomAlignmentItem[];
  questions: AssessmentQuestion[] | null; // For assessment templates
  communication: CommunicationSection | null; // For communication templates
}
```

**Status Codes:**
- `200 OK`: Success
- `404 Not Found`: Template not found or no published version
- `422 Unprocessable Entity`: Missing required fields in input data

---

### 4. Template Streaming Execution Endpoint ⭐
**POST** `/api/v1/templates/{slug}/execute-stream`

**Path Parameters:**
- `slug` (required): Template slug

**Request Body:** `TemplateExecuteRequest`
```typescript
interface TemplateExecuteRequest {
  data: Record<string, any>; // Must match template's input_schema
}
```

**Response:** Server-Sent Events (SSE) stream
- **Content-Type:** `text/event-stream`
- **Headers:**
  - `Cache-Control: no-cache`
  - `Connection: keep-alive`
  - `X-Accel-Buffering: no`

**SSE Event Format:**
Each event is sent as:
```
data: <JSON_STRING>\n\n
```

**Event Types:**

#### 4.1 Meta Event (First Event)
```typescript
{
  type: "meta";
  template_slug: string;
  template_name: string;
  timestamp: number; // Unix timestamp
}
```

#### 4.2 Content Event (Streaming Chunks)
```typescript
{
  type: "content";
  chunk: string; // Text chunk from LLM
  template_slug: string;
}
```
**Note:** Multiple content events are sent as the LLM generates output. Each chunk should be appended to accumulate the full response.

#### 4.3 Done Event (Final Event)
```typescript
{
  type: "done";
  execution_id: string; // UUID
  template_slug: string;
}
```
**Note:** This event signals that streaming is complete. The frontend should parse the accumulated content as JSON (TOON format) to get the final `UniversalTemplateOutput`.

#### 4.4 Error Event
```typescript
{
  type: "error";
  message: string;
  template_slug: string;
}
```

**Status Codes:**
- `200 OK`: Stream started (connection established)
- `404 Not Found`: Template not found or no published version
- `422 Unprocessable Entity`: Missing required fields in input data

---

### 5. Demo Endpoints (Optional)
**POST** `/api/v1/demo/templates/{slug}/execute`
**POST** `/api/v1/demo/templates/{slug}/execute-stream`

Same structure as regular endpoints but without authentication requirements.

---

## Frontend Implementation Requirements

### 1. API Client Setup

#### 1.1 Base URL Configuration
```typescript
// In api/client.ts or similar
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
```

#### 1.2 Type Definitions
Create/update `src/api/types.ts` with all interfaces mentioned above.

---

### 2. Template Listing Implementation

#### 2.1 API Function
```typescript
// In src/api/templates.ts
export const fetchTemplates = async (
  params?: {
    subject?: string;
    grade_band?: string;
    category?: string;
  },
  signal?: AbortSignal
): Promise<TemplateListItem[]> => {
  const queryParams = new URLSearchParams();
  if (params?.subject) queryParams.append('subject', params.subject);
  if (params?.grade_band) queryParams.append('grade_band', params.grade_band);
  if (params?.category) queryParams.append('category', params.category);
  
  const url = `${API_BASE_URL}/v1/templates${queryParams.toString() ? `?${queryParams}` : ''}`;
  
  const response = await fetch(url, { signal });
  if (!response.ok) {
    throw new Error(`Failed to fetch templates: ${response.statusText}`);
  }
  return response.json();
};
```

#### 2.2 Component Usage
- Use in `TemplatesLibrary.tsx` or similar component
- Display list of templates with navigation to detail page
- Handle loading and error states

---

### 3. Template Detail Implementation

#### 3.1 API Function
```typescript
// In src/api/templates.ts
export const fetchTemplateDetail = async (
  slug: string,
  signal?: AbortSignal
): Promise<TemplateDetail> => {
  const url = `${API_BASE_URL}/v1/templates/${slug}`;
  
  const response = await fetch(url, { signal });
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`Template '${slug}' not found`);
    }
    throw new Error(`Failed to fetch template: ${response.statusText}`);
  }
  return response.json();
};
```

#### 3.2 Component Usage
- Use in `TemplateRunner.tsx` to load template metadata
- Extract `input_schema` from `latest_version` to render form fields
- Display template name, description, and other metadata

---

### 4. Streaming Implementation ⭐ (CRITICAL)

#### 4.1 SSE Streaming Hook
Create `src/hooks/useTemplateStream.ts`:

```typescript
import { useState, useCallback, useRef, useEffect } from 'react';

interface StreamEvent {
  type: 'meta' | 'content' | 'done' | 'error';
  template_slug: string;
  [key: string]: any;
}

interface UseTemplateStreamReturn {
  content: string; // Accumulated content
  isStreaming: boolean;
  error: string | null;
  startStream: (slug: string, data: Record<string, any>) => void;
  stopStream: () => void;
  executionId: string | null;
}

export const useTemplateStream = (): UseTemplateStreamReturn => {
  const [content, setContent] = useState<string>('');
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [executionId, setExecutionId] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const startStream = useCallback((slug: string, data: Record<string, any>) => {
    // Reset state
    setContent('');
    setError(null);
    setExecutionId(null);
    setIsStreaming(true);

    // Close existing connection if any
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    // Create POST request body
    const requestBody = JSON.stringify({ data });

    // For SSE with POST, we need to use fetch with ReadableStream
    // EventSource only supports GET, so we'll use fetch API
    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
    const url = `${API_BASE_URL}/v1/templates/${slug}/execute-stream`;

    // Use fetch with streaming response
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: requestBody,
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Stream failed: ${response.statusText}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error('No response body');
        }

        const readStream = () => {
          reader.read().then(({ done, value }) => {
            if (done) {
              setIsStreaming(false);
              return;
            }

            // Decode chunk
            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const jsonStr = line.slice(6); // Remove 'data: ' prefix
                  const event: StreamEvent = JSON.parse(jsonStr);

                  switch (event.type) {
                    case 'meta':
                      // First event - metadata
                      console.log('Stream started:', event);
                      break;

                    case 'content':
                      // Append chunk to accumulated content
                      setContent((prev) => prev + event.chunk);
                      break;

                    case 'done':
                      // Stream complete
                      setExecutionId(event.execution_id);
                      setIsStreaming(false);
                      break;

                    case 'error':
                      // Error occurred
                      setError(event.message);
                      setIsStreaming(false);
                      break;
                  }
                } catch (parseError) {
                  console.error('Failed to parse SSE event:', parseError);
                }
              }
            }

            // Continue reading
            readStream();
          }).catch((err) => {
            setError(err.message);
            setIsStreaming(false);
          });
        };

        readStream();
      })
      .catch((err) => {
        setError(err.message);
        setIsStreaming(false);
      });
  }, []);

  const stopStream = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopStream();
    };
  }, [stopStream]);

  return {
    content,
    isStreaming,
    error,
    startStream,
    stopStream,
    executionId,
  };
};
```

#### 4.2 Parse Streaming Content
After streaming completes, parse the accumulated content:

```typescript
// The content is in TOON format (text-based JSON alternative)
// You may need to parse it or convert it to JSON
// For now, assume it's JSON string that needs parsing

const parseStreamedContent = (content: string): UniversalTemplateOutput | null => {
  try {
    // If content is TOON format, you'll need a TOON parser
    // For now, try JSON parsing
    const parsed = JSON.parse(content);
    return parsed as UniversalTemplateOutput;
  } catch (error) {
    console.error('Failed to parse streamed content:', error);
    return null;
  }
};
```

#### 4.3 Component Integration
Update `TemplateRunner.tsx`:

```typescript
import { useTemplateStream } from '../hooks/useTemplateStream';

const TemplateRunner = () => {
  const { slug } = useParams<{ slug: string }>();
  const { content, isStreaming, error, startStream, stopStream, executionId } = useTemplateStream();
  const [parsedOutput, setParsedOutput] = useState<UniversalTemplateOutput | null>(null);

  const handleSubmit = async (formData: Record<string, any>) => {
    if (!slug) return;
    
    // Start streaming
    startStream(slug, formData);
  };

  // Parse content when streaming completes
  useEffect(() => {
    if (!isStreaming && content && executionId) {
      const parsed = parseStreamedContent(content);
      setParsedOutput(parsed);
    }
  }, [isStreaming, content, executionId]);

  // Display streaming content in real-time
  // Display parsed output when complete
  // Handle errors appropriately
};
```

---

### 5. Error Handling

#### 5.1 Network Errors
- Handle connection failures
- Show user-friendly error messages
- Provide retry mechanism

#### 5.2 Validation Errors (422)
```typescript
// Backend returns:
{
  "detail": {
    "message": "Missing required fields in input data: field1, field2",
    "missing": ["field1", "field2"],
    "error_type": "validation_error"
  }
}
```

#### 5.3 Streaming Errors
- Handle SSE connection drops
- Show error messages from error events
- Allow user to retry

---

### 6. User Experience Considerations

#### 6.1 Loading States
- Show loading indicator while fetching template list
- Show loading indicator while fetching template detail
- Show streaming indicator during SSE stream
- Display "Generating..." message during streaming

#### 6.2 Real-time Updates
- Display content chunks as they arrive
- Show typing/streaming animation
- Update UI incrementally

#### 6.3 Completion Handling
- Parse final content when `done` event received
- Display formatted output
- Show execution metadata (execution_id, latency, etc.)

---

### 7. Testing Checklist

- [ ] Template listing loads correctly
- [ ] Template detail loads correctly
- [ ] Form validation works (required fields)
- [ ] Streaming starts when form submitted
- [ ] Content appears in real-time during streaming
- [ ] Done event is received and handled
- [ ] Error events are handled gracefully
- [ ] Connection cleanup on component unmount
- [ ] Network errors are handled
- [ ] 404 errors are handled
- [ ] 422 validation errors are handled

---

### 8. Important Notes

1. **SSE with POST**: Standard `EventSource` API only supports GET requests. For POST requests with SSE, use `fetch` API with `ReadableStream` as shown in the hook example above.

2. **Content Accumulation**: Content chunks must be accumulated to form the complete response. The final content is in TOON format (or JSON) and needs parsing.

3. **Cleanup**: Always close connections and clean up resources when component unmounts or user navigates away.

4. **Error Recovery**: Implement retry logic for failed streams.

5. **Type Safety**: Ensure all TypeScript types match backend schemas exactly.

6. **Base URL**: Use environment variable for API base URL to support different environments.

---

## Example Complete Flow

1. User navigates to templates list page
2. Frontend calls `GET /api/v1/templates`
3. User clicks on a template
4. Frontend calls `GET /api/v1/templates/{slug}`
5. Frontend renders form based on `input_schema`
6. User fills form and submits
7. Frontend calls `POST /api/v1/templates/{slug}/execute-stream`
8. Frontend receives SSE events:
   - `meta` event (stream started)
   - Multiple `content` events (chunks)
   - `done` event (stream complete)
9. Frontend parses accumulated content
10. Frontend displays formatted output to user

---

## Backend Response Examples

### Template List Response
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "slug": "lesson_planner",
    "name": "Lesson Planner",
    "description": "Generate comprehensive lesson plans",
    "category": "lesson_planning",
    "subject_default": "math",
    "grade_bands_supported": ["K-2", "3-5"],
    "is_active": true
  }
]
```

### Template Detail Response
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "slug": "lesson_planner",
  "name": "Lesson Planner",
  "description": "Generate comprehensive lesson plans",
  "category": "lesson_planning",
  "subject_default": "math",
  "grade_bands_supported": ["K-2", "3-5"],
  "is_system_template": true,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "latest_version": {
    "id": "223e4567-e89b-12d3-a456-426614174000",
    "version": 1,
    "status": "published",
    "input_schema": {
      "type": "object",
      "properties": {
        "topic": { "type": "string" },
        "learning_objective": { "type": "string" }
      },
      "required": ["topic", "learning_objective"]
    },
    "output_schema": null,
    "prompt_definition": null,
    "model_config": null,
    "published_at": "2024-01-01T00:00:00Z"
  }
}
```

### SSE Event Examples

**Meta Event:**
```
data: {"type":"meta","template_slug":"lesson_planner","template_name":"Lesson Planner","timestamp":1704067200.0}

```

**Content Event:**
```
data: {"type":"content","chunk":"{\"overview\":\"This lesson","template_slug":"lesson_planner"}

```

**Done Event:**
```
data: {"type":"done","execution_id":"323e4567-e89b-12d3-a456-426614174000","template_slug":"lesson_planner"}

```

**Error Event:**
```
data: {"type":"error","message":"Error during template execution: Connection timeout","template_slug":"lesson_planner"}

```

---

## Support

For questions or issues, refer to:
- Backend API documentation: `http://localhost:8000/docs`
- Backend code: `1ne_backend/app/api/v1/routes_templates.py`
- Execution service: `1ne_backend/app/services/execution_service.py`

