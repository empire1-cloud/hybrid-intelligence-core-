"""
Strategy Engine
Generates actionable strategies using the Empire-1 approved AI stack.

Supports approved OpenAI and Anthropic models via the local integration layer.
"""

import os
import json
import asyncio
from typing import Optional, Dict, Any

from emergentintegrations.llm.chat import LlmChat, UserMessage
from services.model_policy import enforce_approved_model


class StrategyEngine:
    """Generates actionable strategies using the approved HIC model stack."""

    MODEL_CONFIG = {
        "gpt-5.2": ("openai", "gpt-4o"),
        "gpt-4o": ("openai", "gpt-4o"),
        "gpt-4o-mini": ("openai", "gpt-4o-mini"),
        "claude-sonnet-4.5": ("anthropic", "claude-sonnet-4-5-20250929"),
        "claude-3-5-sonnet": ("anthropic", "claude-3-5-sonnet-20241022"),
    }

    SYSTEM_PROMPT = """You are the Strategy Engine.

Your job is to take any goal the user gives you and return a clear, structured, actionable strategy that creates momentum, removes confusion, and breaks the goal into steps anyone can follow.

RULES:
1. Always return valid JSON only — no markdown, no explanations outside JSON.
2. Never ramble, never fluff, never repeat the user's words back to them.
3. Keep the tone direct, practical, and operator-minded.
4. Break everything into steps that can be executed immediately.
5. If the user's goal is vague, infer the most useful interpretation and proceed.
6. Never ask questions.
7. Always include risks, blind spots, and next actions.
8. Always assume the user wants clarity, speed, and momentum.

OUTPUT FORMAT (JSON ONLY):
{
  "summary": "One paragraph explaining the strategy at a high level.",
  "steps": ["Step 1...", "Step 2...", "Step 3..."],
  "risks": ["Risk 1...", "Risk 2..."],
  "resources": ["Resource 1...", "Resource 2..."],
  "next_action": "The single most important thing the user should do immediately."
}

Return ONLY the JSON object. No other text."""

    @classmethod
    def _get_api_key(cls, provider: str) -> str:
        """Get a provider-specific API key without Google fallbacks."""
        if provider == "anthropic":
            return os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("EMERGENT_LLM_KEY")
        return os.environ.get("OPENAI_API_KEY") or os.environ.get("EMERGENT_LLM_KEY")

    @classmethod
    def _create_chat(cls, model: str) -> LlmChat:
        """Create a configured chat instance after enforcing model policy."""
        approved_model = enforce_approved_model(model)
        provider, model_name = cls.MODEL_CONFIG[approved_model]
        api_key = cls._get_api_key(provider)

        chat = LlmChat(
            api_key=api_key,
            session_id=f"strategy-{approved_model}",
            system_message=cls.SYSTEM_PROMPT
        ).with_model(provider, model_name)

        return chat

    @classmethod
    async def _generate_async(
        cls,
        model: str,
        goal: str,
        context: str = None,
        tone: str = "direct"
    ) -> Dict[str, Any]:
        """Generate strategy asynchronously."""
        chat = cls._create_chat(model)

        prompt = f"Goal: {goal}"
        if context:
            prompt += f"\nContext: {context}"
        if tone:
            prompt += f"\nTone: {tone}"

        message = UserMessage(text=prompt)
        response = await chat.send_message(message)

        try:
            response_text = response

            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()

            return json.loads(response_text)
        except json.JSONDecodeError:
            return {
                "summary": response[:500] if isinstance(response, str) else str(response)[:500],
                "steps": ["Review the generated content and extract actionable steps"],
                "risks": ["Response was not in expected JSON format"],
                "resources": [],
                "next_action": "Retry with a more specific goal"
            }

    @classmethod
    def generate(
        cls,
        model: str,
        goal: str,
        context: str = None,
        tone: str = "direct"
    ) -> Dict[str, Any]:
        """Synchronous wrapper for async generation."""
        return asyncio.run(cls._generate_async(model, goal, context, tone))

    @classmethod
    async def generate_async(
        cls,
        model: str,
        goal: str,
        context: str = None,
        tone: str = "direct"
    ) -> Dict[str, Any]:
        """Async generation method."""
        return await cls._generate_async(model, goal, context, tone)
