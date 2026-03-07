import os
import json

import redis
from openai import OpenAI
from config import OPENAI_API_KEY, LLM_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

# ==========================================================
# CONVERSATION MEMORY — Redis or in-memory fallback
# ==========================================================

MAX_TURNS = 10
CONV_TTL_SECONDS = 24 * 60 * 60  # 24 hours

REDIS_URL = os.getenv("REDIS_URL", "")

_redis: redis.Redis | None = None
_fallback_sessions: dict = {}  # in-memory fallback when no Redis


def _get_redis() -> redis.Redis | None:
    global _redis
    if _redis is not None:
        return _redis
    if REDIS_URL:
        try:
            _redis = redis.from_url(REDIS_URL, decode_responses=True)
            _redis.ping()
            print("✅ Redis connected")
            return _redis
        except Exception as e:
            print(f"⚠️ Redis unavailable, using in-memory fallback: {e}")
            return None
    return None


def _conv_key(user_id: str) -> str:
    return f"conv:{user_id}"


def _load_history(user_id: str) -> list[dict]:
    r = _get_redis()
    if r:
        raw = r.get(_conv_key(user_id))
        if raw:
            return json.loads(raw)
        return []
    else:
        return _fallback_sessions.get(user_id, [])


def _save_history(user_id: str, history: list[dict]):
    r = _get_redis()
    if r:
        r.setex(_conv_key(user_id), CONV_TTL_SECONDS, json.dumps(history))
    else:
        _fallback_sessions[user_id] = history


# ==========================================================
# SYSTEM PROMPT
# ==========================================================

SYSTEM_PROMPT = """
You are a multilingual eCommerce customer support assistant.

Rules:
- Answer politely and clearly.
- Reply in the same language as the question.
- Understand the emotion of the customer and respond empathetically.
- Behave like a real human customer support agent.
- Use the provided context to answer.
- Give short and crisp answers and in case where users asks for AI(your) opinion give it.
- Be supportive, patient, helpful and solution oriented.
- Context may include knowledge base results or web search results.
- Prefer knowledge base answers first.
- If web results are provided, summarize them clearly.
- Keep responses concise (1–3 sentences) since answers are spoken aloud as voice responses.

Emotion Handling Guidelines:
- Always first acknowledge the customer's concern before giving the answer.
- If the customer sounds frustrated, angry, or disappointed, apologize sincerely and reassure them that you will help resolve the issue.
- If the customer sounds confused, explain the answer in a simple and clear way.
- If the customer sounds worried, reassure them and guide them step-by-step.
- If the customer sounds happy or satisfied, respond positively and appreciate their feedback.
- Never argue with the customer even if they are upset.
- Stay calm, polite, and professional at all times.

Conversation Style:
- Respond like a friendly human support agent, not like a robot.
- Use natural conversational tone as used in daily conversations.
- If information is missing, politely ask the customer for the required details (order id, product name, etc.).
- Always end the response by offering help if the customer needs anything else.

Language Style Guidelines:
- Reply in the same language used by the customer.
- Convert any formal or textbook language from the context into natural conversational language.
- Avoid pure literary or overly formal language.
- Use the spoken form of the language commonly used in everyday conversations.
- Do NOT copy sentences directly from the context if they sound formal — rewrite them in a casual, human-friendly way.
"""


# ==========================================================
# GENERATE ANSWER
# ==========================================================


def generate_answer(user_id, query, context_docs):
    history = _load_history(user_id)

    context = "\n".join(context_docs[:5])

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append(
        {
            "role": "user",
            "content": f"""
Context:
{context}

Customer Question:
{query}
""",
        }
    )

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=150,
        timeout=30,
    )

    answer = response.choices[0].message.content

    history.append({"role": "user", "content": query})
    history.append({"role": "assistant", "content": answer})

    # Trim to last MAX_TURNS turns
    if len(history) > MAX_TURNS * 2:
        history = history[-MAX_TURNS * 2:]

    _save_history(user_id, history)

    return answer
