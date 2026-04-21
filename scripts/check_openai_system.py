#!/usr/bin/env python3
r"""
One-shot: backend .env -> OpenAI chat API.
Run from 1ne_backend folder:
  Windows: venv\Scripts\python.exe scripts\check_openai_system.py
Exit 0 = OK, 1 = FAIL.
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")


def main() -> int:
    from app.llm.config import llm_settings

    if not (llm_settings.OPENAI_API_KEY or "").strip():
        print("FAIL: OPENAI_API_KEY missing or empty in 1ne_backend/.env")
        return 1

    kwargs: dict = {"api_key": llm_settings.OPENAI_API_KEY.strip()}
    if (llm_settings.OPENAI_BASE_URL or "").strip():
        kwargs["base_url"] = llm_settings.OPENAI_BASE_URL.strip()

    # 1) Direct OpenAI HTTP (same as “key valid?” check)
    try:
        import urllib.request
        import json

        req = urllib.request.Request(
            "https://api.openai.com/v1/models?limit=1",
            headers={"Authorization": f"Bearer {kwargs['api_key']}"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            if resp.status != 200:
                print("FAIL: /v1/models HTTP", resp.status)
                return 1
        print("OK:   /v1/models (key accepted by OpenAI)")
    except Exception as e:
        print("FAIL: /v1/models —", e)
        return 1

    # 2) Real chat completion (same stack apps use)
    try:
        from openai import OpenAI

        client = OpenAI(**kwargs)
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": 'Reply with exactly one word: "pong"'}],
            max_tokens=32,
            temperature=0,
        )
        text = (r.choices[0].message.content or "").strip()
        print("OK:   chat.completions —", repr(text[:120]))
    except Exception as e:
        print("FAIL: chat.completions —", e)
        return 1

    # 3) Same ModelRouter path as chatbots/templates (async)
    try:
        from app.llm.router import ModelRouter

        async def _run() -> str:
            router = ModelRouter()
            out = await router.generate(
                system_message="You reply with one word only.",
                prompt='Say exactly: "pong"',
                model_config={"provider": "openai", "model": "gpt-4o-mini", "temperature": 0, "max_tokens": 32},
            )
            return (out.content or "").strip()

        routed = asyncio.run(_run())
        print("OK:   ModelRouter.generate —", repr(routed[:120]))
    except Exception as e:
        print("FAIL: ModelRouter.generate —", e)
        return 1

    print("ALL CHECKS PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
