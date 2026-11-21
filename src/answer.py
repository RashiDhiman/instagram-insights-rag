
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()


def generate_answer(question, hits):
    if not hits:
        return "I couldn't retrieve relevant records from the Instagram export."

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        return "Gemini API key not found. Check GEMINI_API_KEY in your .env file."

    context = "\n\n".join(
        f"SOURCE ID: {hit['id']}\n"
        f"CONTENT: {hit['text']}\n"
        f"METADATA: {hit['metadata']}"
        for hit in hits
    )

    prompt = f"""
You are an Instagram content analytics assistant.
Answer the user's question using only the retrieved Instagram export records below.

Rules:
- Do not invent facts, metrics, dates, or performance explanations.
- If the records do not contain enough information, say so.
- Distinguish Google itself from third-party companies or programmes.
- Summarize instead of copying entire captions.
- Cite each factual claim with its source ID in square brackets, e.g. [reels_28].
- Do not claim that correlation proves causation.

User question:
{question}

Retrieved records:
{context}

Write a concise, useful answer with source citations.
"""

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    return response.text or "Gemini returned an empty response."
