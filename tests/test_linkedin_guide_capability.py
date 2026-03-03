"""
Test LinkedIn Guide capability response serialization.

Ensures that when the LLM returns bytes or the parsed result contains bytes,
the capability service always returns JSON-serializable data (no "Object of type bytes
is not JSON serializable" error).
"""
import json
import uuid
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from app.domains.chatbots.models import Chatbot, ChatbotCapability, ChatbotModelAssignment
from app.domains.chatbots.services.capability_service import CapabilityService
from app.llm.schemas import TokenUsage


def _ensure_no_bytes_in_obj(obj, path="root"):
    """Recursively check that no bytes exist in obj (for diagnosis)."""
    if isinstance(obj, bytes):
        raise AssertionError(f"Found bytes at {path}")
    if isinstance(obj, dict):
        for k, v in obj.items():
            _ensure_no_bytes_in_obj(k, f"{path}.key")
            _ensure_no_bytes_in_obj(v, f"{path}[{k!r}]")
    elif isinstance(obj, (list, tuple)):
        for i, item in enumerate(obj):
            _ensure_no_bytes_in_obj(item, f"{path}[{i}]")


@pytest.fixture
def career_coach_chatbot(db):
    """Create minimal Career Readiness Coach chatbot with linkedin_guide capability."""
    chatbot = Chatbot(
        id=uuid.uuid4(),
        slug="career-readiness-coach",
        name="Career Readiness Coach",
        description="Test",
        category="subject",
        subject="Career",
        access_level="premium",
        system_prompt="You are a career coach.",
        is_active=True,
    )
    db.add(chatbot)
    db.flush()

    assignment = ChatbotModelAssignment(
        chatbot_id=chatbot.id,
        provider="openai",
        model_name="gpt-4o-mini",
        priority=0,
        is_primary=True,
        is_enabled=True,
    )
    db.add(assignment)
    db.flush()

    capability = ChatbotCapability(
        chatbot_id=chatbot.id,
        capability_key="linkedin_guide",
        capability_name="LinkedIn & Professional Networking",
        capability_description="Test",
        capability_category="instruction",
        icon_name="Linkedin",
        display_order=6,
        is_primary=True,
        requires_input_type="text",
        system_prompt_template="Return valid JSON only.",
        processing_mode="structured",
        is_active=True,
    )
    db.add(capability)
    db.commit()
    db.refresh(chatbot)
    return chatbot


@pytest.fixture
def test_user(db):
    """Create a minimal user for capability execution."""
    from app.domains.auth.models import User
    from app.domains.tenants.models import Tenant

    tenant = Tenant(id=uuid.uuid4(), name="Test Tenant", slug="test-tenant")
    db.add(tenant)
    db.flush()

    user = User(
        id=uuid.uuid4(),
        email="test-cap@example.com",
        tenant_id=tenant.id,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.mark.asyncio
async def test_linkedin_guide_returns_json_serializable_when_llm_returns_bytes(
    db, career_coach_chatbot, test_user
):
    """
    When the LLM returns bytes (e.g. from cache or provider), the capability
    must still return a JSON-serializable result so the API does not raise
    'Object of type bytes is not JSON serializable'.
    """
    capability_service = CapabilityService(db)

    # Simulate LLM returning raw bytes (e.g. from cache/Redis or provider quirk).
    # Use a mock so content stays as bytes; LLMResponse(content=b"...") would coerce to str in Pydantic.
    mock_llm_response = MagicMock()
    mock_llm_response.content = b"some raw bytes response that is not valid json"
    mock_llm_response.model_used = "gpt-4o-mini"
    mock_llm_response.provider = "openai"
    mock_llm_response.token_usage = TokenUsage(prompt=0, completion=0, total=0)
    mock_llm_response.cost_estimate = None
    mock_llm_response.latency_ms = 100

    with patch.object(capability_service, "model_router") as mock_router:
        mock_router.generate = AsyncMock(return_value=mock_llm_response)

        # This would previously raise or return result that fails json.dumps
        result = await capability_service.execute_capability(
            chatbot_id=career_coach_chatbot.id,
            capability_key="linkedin_guide",
            user_id=test_user.id,
            input_data="LinkedIn Guide",
            parameters={
                "grade_level": "K-5",
                "region": "United States",
                "industry": "Technology",
                "career_level": "Entry",
            },
            save_result=False,
        )

    # Must be serializable to JSON (no bytes anywhere)
    assert "result" in result
    _ensure_no_bytes_in_obj(result["result"], "result")
    json_str = json.dumps(result["result"])
    assert isinstance(json_str, str)
    assert "content" in result["result"]
    # Content should have been decoded from bytes to str
    assert isinstance(result["result"]["content"], str)


@pytest.mark.asyncio
async def test_ensure_json_serializable_converts_nested_bytes(db):
    """_ensure_json_serializable converts bytes at any nesting level."""
    capability_service = CapabilityService(db)

    data = {
        "a": b"bytes here",
        "b": {"c": b"nested bytes", "d": [b"list bytes"]},
        "e": "already str",
    }
    out = capability_service._ensure_json_serializable(data)
    assert out["a"] == "bytes here"
    assert out["b"]["c"] == "nested bytes"
    assert out["b"]["d"][0] == "list bytes"
    assert out["e"] == "already str"
    json.dumps(out)
