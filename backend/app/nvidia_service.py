"""
VendorSync AI — NVIDIA NIM Integration Client
Enterprise integration with NVIDIA API / NIM endpoints using OpenAI-compatible SDK.
Features secure credential management, streaming with reasoning capture,
and strict grounding enforcement.
"""

import os
import time
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator, Tuple
from dotenv import load_dotenv
from openai import OpenAI
import anyio

# Ensure environment variables are loaded
load_dotenv()

logger = logging.getLogger("nvidia_service")

# Default NVIDIA Configuration
DEFAULT_NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_NVIDIA_MODEL = "nvidia/nemotron-3-ultra-550b-a55b"


def get_nvidia_config() -> Dict[str, Any]:
    """Retrieves validated NVIDIA configuration from environment."""
    api_key = os.getenv("NVIDIA_API_KEY", "").strip()
    base_url = os.getenv("NVIDIA_BASE_URL", DEFAULT_NVIDIA_BASE_URL).strip()
    model = os.getenv("NVIDIA_MODEL", DEFAULT_NVIDIA_MODEL).strip()
    return {
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
        "configured": bool(api_key)
    }


def is_nvidia_available() -> bool:
    """Checks if NVIDIA API is configured."""
    return bool(os.getenv("NVIDIA_API_KEY", "").strip())


def create_nvidia_client() -> Optional[OpenAI]:
    """Initializes OpenAI client configured for NVIDIA NIM."""
    cfg = get_nvidia_config()
    if not cfg["configured"]:
        return None
    try:
        return OpenAI(
            base_url=cfg["base_url"],
            api_key=cfg["api_key"],
            timeout=30.0,
            max_retries=1
        )
    except Exception as e:
        logger.error(f"Failed to initialize NVIDIA client: {e}")
        return None


def _clean_error_message(err_str: str) -> str:
    """Sanitizes error messages to prevent accidental API key leaks."""
    api_key = os.getenv("NVIDIA_API_KEY", "").strip()
    if api_key and api_key in err_str:
        return err_str.replace(api_key, "nvapi-***REDACTED***")
    return err_str


def build_nvidia_messages(
    user_message: str,
    factual_table_md: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
    scoped_vendor_name: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Constructs the grounded prompt structure with system instructions,
    verified facts context, and recent conversation history.
    """
    system_prompt = (
        "You are VendorSync Copilot, an enterprise procurement intelligence AI powered by NVIDIA NIM. "
        "Your mission is to help procurement officers and supply-chain directors make evidence-based decisions, "
        "evaluate supplier risk, identify delivery bottlenecks, and draft negotiation strategies.\n\n"
        "### STRICT GROUNDING & ACCURACY CONTRACT:\n"
        "1. GROUND ALL METRICS IN THE PROVIDED VERIFIED DATA: Every percentage, dollar amount, count, and score "
        "must come directly from the [VERIFIED DATA] section below. NEVER invent, hallucinate, or extrapolate figures.\n"
        "2. SEPARATION OF FACT AND ADVICE: Clearly distinguish between observed operational facts "
        "(e.g., 'Northstar Components has 96% on-time delivery') and strategic recommendations "
        "(e.g., 'Recommend prioritizing for high-volume orders').\n"
        "3. EXPLAIN ASSUMPTIONS & FORMULAS: When asked about KPIs, cite the official calculation formulas.\n"
        "4. STATE MISSING DATA: If the user asks for metrics not present in the verified data, clearly inform them.\n"
        "5. PROFESSIONAL ENTERPRISE TONE: Format responses cleanly in GitHub-flavored markdown with bullet points, "
        "bold highlights, and data tables where comparative analysis is helpful."
    )

    if scoped_vendor_name:
        system_prompt += f"\nNote: The user has actively scoped this session to vendor: **{scoped_vendor_name}**."

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_prompt}
    ]

    # Include recent chat history (up to last 6 messages)
    if chat_history:
        for m in chat_history[-6:]:
            role = "assistant" if m.get("sender") == "assistant" or m.get("role") == "assistant" else "user"
            content = m.get("text") or m.get("content") or ""
            if content and not content.startswith("*(") and not content.startswith("⚠️"):
                messages.append({"role": role, "content": content})

    # Grounded query with factual context
    grounded_user_content = (
        f"{factual_table_md}\n\n"
        f"--- USER INQUIRY ---\n"
        f"{user_message}"
    )

    messages.append({"role": "user", "content": grounded_user_content})
    return messages


def _execute_sync_nvidia_call(
    client: OpenAI,
    model: str,
    messages: List[Dict[str, str]],
    temperature: float = 0.6,
    max_tokens: int = 4096
) -> Dict[str, Any]:
    """Synchronous worker that calls NVIDIA API with retry on transient errors."""
    last_err = None
    for attempt in range(2):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            choice = completion.choices[0]
            content = choice.message.content or ""
            reasoning = getattr(choice.message, "reasoning_content", None)
            return {"content": content, "reasoning": reasoning}
        except Exception as e:
            last_err = e
            err_str = str(e)
            if attempt < 1 and ("503" in err_str or "429" in err_str or "overloaded" in err_str.lower() or "timeout" in err_str.lower()):
                logger.info(f"Transient error on NVIDIA API (attempt {attempt+1}/2), backing off: {err_str[:80]}")
                time.sleep(1.0)
                continue
            break
    if last_err:
        raise last_err
    return {"content": "", "reasoning": None}


async def call_nvidia_api(
    user_message: str,
    factual_table_md: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
    scoped_vendor_name: Optional[str] = None,
    max_tokens: int = 4096,
    temperature: float = 0.6
) -> Optional[Dict[str, Any]]:
    """
    Executes a grounded call to the NVIDIA API asynchronously.
    Returns dict with reply, reasoning, model, and provider on success, or None on error.
    """
    cfg = get_nvidia_config()
    client = create_nvidia_client()
    if not client:
        return None

    messages = build_nvidia_messages(user_message, factual_table_md, chat_history, scoped_vendor_name)

    try:
        result = await anyio.to_thread.run_sync(
            _execute_sync_nvidia_call,
            client,
            cfg["model"],
            messages,
            temperature,
            max_tokens
        )
        return {
            "reply": result["content"].strip(),
            "reasoning": result.get("reasoning"),
            "provider": "NVIDIA NIM",
            "model": cfg["model"],
            "connected": True
        }
    except Exception as e:
        safe_err = _clean_error_message(str(e))
        logger.error(f"NVIDIA API request failed: {safe_err}")
        return None


async def stream_nvidia_api(
    user_message: str,
    factual_table_md: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
    scoped_vendor_name: Optional[str] = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Streams tokens from NVIDIA NIM generator.
    Yields dicts with {"chunk": str, "reasoning": str, "done": bool}.
    """
    cfg = get_nvidia_config()
    client = create_nvidia_client()
    if not client:
        yield {"chunk": "", "error": "NVIDIA API not configured", "done": True}
        return

    messages = build_nvidia_messages(user_message, factual_table_md, chat_history, scoped_vendor_name)

    def _sync_stream():
        try:
            return client.chat.completions.create(
                model=cfg["model"],
                messages=messages,
                temperature=0.6,
                top_p=0.95,
                max_tokens=4096,
                extra_body={"chat_template_kwargs": {"enable_thinking": True}, "reasoning_budget": 2048},
                stream=True
            )
        except Exception:
            return client.chat.completions.create(
                model=cfg["model"],
                messages=messages,
                temperature=0.6,
                max_tokens=4096,
                stream=True
            )

    try:
        stream = await anyio.to_thread.run_sync(_sync_stream)
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            c = getattr(delta, "content", None)
            r = getattr(delta, "reasoning_content", None)
            if c or r:
                yield {"chunk": c or "", "reasoning": r or "", "done": False}
        yield {"chunk": "", "reasoning": "", "done": True}
    except Exception as e:
        safe_err = _clean_error_message(str(e))
        logger.error(f"NVIDIA streaming failed: {safe_err}")
        yield {"chunk": f"\n\n*[Connection error: {safe_err}]*", "done": True, "error": safe_err}
