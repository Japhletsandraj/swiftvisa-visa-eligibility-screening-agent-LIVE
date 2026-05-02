"""
SwiftVisa - LLM Integration with LM Studio
Handles communication with the Llama model via LM Studio
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import requests
import json
from typing import Dict, List, Optional

from config.config import (
    LM_STUDIO_CONFIG,
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
    ELIGIBILITY_PROMPT_TEMPLATE,
    LOGGING_CONFIG,
)

logging.basicConfig(level=LOGGING_CONFIG["level"], format=LOGGING_CONFIG["format"])
logger = logging.getLogger(__name__)


class LMStudioLLM:
    """LLM interface for LM Studio."""

    def __init__(
        self,
        base_url: str = None,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
    ):
        self.base_url = base_url or LM_STUDIO_CONFIG["base_url"]
        self.model = model or LM_STUDIO_CONFIG["model"]
        self.temperature = temperature or LM_STUDIO_CONFIG["temperature"]
        self.max_tokens = max_tokens or LM_STUDIO_CONFIG["max_tokens"]

        logger.info(f"[LLM] Connecting to {self.base_url} — model: {self.model}")
        self._test_connection()
        logger.info("[LLM] Ready")

    # ── Connection ────────────────────────────────────────────────────────────

    def _test_connection(self):
        try:
            r = requests.get(f"{self.base_url}/models", timeout=5)
            if r.status_code == 200:
                logger.info("[LLM] Connected to LM Studio")
            else:
                logger.warning(f"[LLM] LM Studio responded with status {r.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"[LLM] Cannot connect to LM Studio: {e}")
            raise ConnectionError(f"Cannot connect to LM Studio at {self.base_url}")

    # ── Core generate ─────────────────────────────────────────────────────────

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = None,
        max_tokens: int = None,
        stream: bool = False,
    ) -> str:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
            "stream": stream,
        }

        try:
            for i, msg in enumerate(messages):
                logger.debug(f"  msg[{i}] role={msg['role']} len={len(msg['content'])}")

            logger.info(f"[LLM] Sending request to {url}...")
            response = requests.post(url, json=payload, timeout=520)

            if response.status_code != 200:
                detail = response.text
                logger.error(f"[LLM] Error response ({response.status_code}): {detail}")
                if "context" in detail.lower() or "length" in detail.lower():
                    raise ValueError(
                        "Context length exceeded. Reduce retrieved chunks or shorten the prompt."
                    )
                raise ValueError(f"LLM returned error: {detail}")

            response.raise_for_status()
            text = response.json()["choices"][0]["message"]["content"]
            logger.debug(f"[LLM] Response: {len(text)} chars")
            return text

        except requests.exceptions.Timeout as e:
            error_msg = f"LM Studio request timed out after 520 seconds. Make sure LM Studio is running at {self.base_url} and the model '{self.model}' is loaded."
            logger.error(f"[LLM] Timeout: {error_msg}")
            raise TimeoutError(error_msg)
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Cannot connect to LM Studio at {self.base_url}. Is LM Studio running? Check config.py for the correct IP and port."
            logger.error(f"[LLM] Connection error: {error_msg}")
            raise ConnectionError(error_msg)
        except requests.exceptions.HTTPError as e:
            logger.error(f"[LLM] HTTP error: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"[LLM] Request error: {e}")
            raise

    # ── Public methods ────────────────────────────────────────────────────────

    def answer_question(
        self,
        question: str,
        context: str,
        system_prompt: str = None,
    ) -> str:
        """Answer a question from retrieved policy context."""
        user_message = USER_PROMPT_TEMPLATE.format(context=context, question=question)
        messages = [
            {"role": "system", "content": system_prompt or SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ]
        logger.info(f"[QA] '{question}'")
        return self.generate(messages)

    def evaluate_eligibility(
        self,
        user_profile: Dict,
        visa_type: str,
        context: str,
        country: str = "the destination country",   # NEW — injected by rag_pipeline
    ) -> str:
        """
        Evaluate visa eligibility.

        Args:
            user_profile: Form field values from app.py.
            visa_type:    Visa type string (may include country suffix added by rag_pipeline).
            context:      Formatted retrieved policy context.
            country:      Human-readable country name for the prompt.
        """
        profile_str = "\n".join(f"{k}: {v}" for k, v in user_profile.items())

        user_message = ELIGIBILITY_PROMPT_TEMPLATE.format(
            context=context,
            user_profile=profile_str,
            visa_type=visa_type.replace("_", " ").title(),
            country=country,
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ]

        logger.info(f"[EVAL] visa={visa_type} country={country}")
        return self.generate(messages, temperature=0.2)

    def chat(
        self,
        user_message: str,
        conversation_history: List[Dict] = None,
        context: str = None,
    ) -> str:
        """Multi-turn chat with optional RAG context."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if conversation_history:
            messages.extend(conversation_history)

        if context:
            enhanced = f"CONTEXT:\n{context}\n\nUSER QUESTION:\n{user_message}"
        else:
            enhanced = user_message

        messages.append({"role": "user", "content": enhanced})
        return self.generate(messages)


# ── CLI test ──────────────────────────────────────────────────────────────────

def test_llm():
    print("\n" + "=" * 70)
    print(" SwiftVisa — LMStudioLLM test")
    print("=" * 70)

    try:
        llm = LMStudioLLM()

        # Test 1 — QA
        print("\n[Test 1] Question answering")
        context = """
        UK Student Visa Financial Requirements:
        - At least £1,334/month for living costs in London
        - At least £1,023/month outside London
        - Funds must have been held for 28 consecutive days
        """
        question = "How much money do I need for a student visa in London?"
        print(f"Q: {question}")
        print(f"A: {llm.answer_question(question, context)}")

        # Test 2 — Eligibility
        print("\n[Test 2] Eligibility evaluation")
        profile = {
            "Age": 25, "Nationality": "Indian",
            "Education": "Bachelor's in Computer Science",
            "English Test": "IELTS 7.0",
            "University Offer": "Yes — University of London",
            "Financial Proof": "£15,000",
        }
        result = llm.evaluate_eligibility(
            user_profile=profile,
            visa_type="student",
            context=context,
            country="United Kingdom",
        )
        print(result)

        print("\n" + "=" * 70)
        print(" Test complete!")

    except Exception as e:
        print(f"\nError: {e}")
        print("Ensure LM Studio is running and the model is loaded.")


if __name__ == "__main__":
    test_llm()