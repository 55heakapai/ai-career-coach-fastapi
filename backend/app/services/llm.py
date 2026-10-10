"""LLM access behind one small interface so providers can be swapped or mocked."""
import json
import logging
import re
from functools import lru_cache

import httpx

from app.core.config import settings

log = logging.getLogger(__name__)


class LLMError(Exception):
    """Raised when the model cannot produce a usable answer."""


def parse_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)  # model wrapped JSON in prose or fences
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    raise LLMError("The AI returned an unreadable answer. Try again.")


class GeminiLLM:
    URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def _call(self, system: str, contents: list[dict], json_mode: bool) -> str:
        config = {"temperature": 0.6}
        if json_mode:
            config["responseMimeType"] = "application/json"
        body = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": contents,
            "generationConfig": config,
        }
        try:
            res = httpx.post(
                self.URL.format(model=settings.gemini_model),
                json=body,
                headers={"x-goog-api-key": settings.gemini_api_key},
                timeout=45,
            )
            res.raise_for_status()
            return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
            log.exception("Gemini request failed")
            raise LLMError("The AI service is unavailable right now. Try again in a moment.") from exc

    def chat(self, system: str, messages: list[dict]) -> str:
        contents = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]}
            for m in messages
        ]
        return self._call(system, contents, json_mode=False)

    def json(self, task: str, system: str, prompt: str) -> dict:
        text = self._call(system, [{"role": "user", "parts": [{"text": prompt}]}], json_mode=True)
        return parse_json(text)


MOCK_JSON = {
    "resume": {
        "summary": "Demo feedback (no API key configured). Your resume shows relevant projects.",
        "strengths": ["Clear project list", "Relevant tech stack"],
        "improvements": ["Add measurable results to bullets", "List links to live demos"],
        "rewritten_bullets": [
            {"original": "Built a web app", "improved": "Built a web app used by [X] users, cutting load time by [Y%]"}
        ],
    },
    "questions": {
        "questions": [
            {"question": "Walk me through a project you are proud of.", "type": "project", "hint": "Cover your role and one hard decision."},
            {"question": "How would you design a REST API for a booking system?", "type": "technical", "hint": "Think resources, status codes and auth."},
            {"question": "Tell me about a time you got stuck and how you got unstuck.", "type": "behavioral", "hint": "Use situation, action, result."},
        ]
    },
    "evaluate": {
        "score": 6,
        "strengths": ["Answered the question directly"],
        "improvements": ["Add a concrete example", "Explain the trade-off you considered"],
        "model_answer_outline": ["State the goal", "Describe your approach", "Give a result", "Name one trade-off"],
    },
}


class MockLLM:
    """Offline stand-in used in tests and when no API key is configured."""

    def chat(self, system: str, messages: list[dict]) -> str:
        last = messages[-1]["content"][:120]
        return f"(Demo mode, no AI key set) You asked: \"{last}\". Add GEMINI_API_KEY to get real coaching."

    def json(self, task: str, system: str, prompt: str) -> dict:
        return MOCK_JSON[task]


@lru_cache
def get_llm():
    if settings.llm_provider == "gemini" and settings.gemini_api_key:
        return GeminiLLM()
    log.warning("Using the mock LLM. Set LLM_PROVIDER=gemini and GEMINI_API_KEY for real answers.")
    return MockLLM()
