import os
from .models import Book

# ── Gemini Setup ─────────────────────────────────────────────────────────────
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

if HAS_GEMINI and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    gemini_model = None


def _keyword_search(query: str, books, top_k: int = 3):
    """
    Simple keyword search — no vector DB, works on all platforms including Vercel.
    """
    query_words = set(query.lower().split())
    scored = []
    for book in books:
        text = f"{book.title} {book.description or ''} {book.rating or ''}".lower()
        score = sum(1 for w in query_words if w in text)
        scored.append((score, book))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [b for _, b in scored[:top_k]]


def index_document(book):
    """No-op: vector indexing removed for serverless compatibility."""
    pass


def process_rag_query(query: str):
    """
    AI-powered book search:
    1. Keyword-match books from Django DB
    2. Build a context string
    3. Send to Gemini for a smart answer (fallback to plain list)
    """
    books = list(Book.objects.all())
    if not books:
        return {
            "response": "The library is empty. Click 'Update Books' in the sidebar to scrape books first.",
            "sources": []
        }

    relevant = _keyword_search(query, books)
    if not relevant:
        relevant = books[:3]

    sources = [b.title for b in relevant]

    # Build context for the LLM
    context_parts = []
    for b in relevant:
        context_parts.append(
            f"Title: {b.title}\n"
            f"Author: {b.author}\n"
            f"Price: {b.price}\n"
            f"Rating: {b.rating}\n"
            f"Description: {b.description or 'N/A'}"
        )
    context = "\n\n---\n\n".join(context_parts)

    if gemini_model is not None:
        prompt = (
            "You are NSR AI, a friendly book assistant for NSR BOOKS store.\n"
            "Answer the user's question using ONLY the book information provided below.\n"
            "If the answer is not available, say so politely.\n\n"
            f"Books:\n{context}\n\n"
            f"User question: {query}"
        )
        try:
            response = gemini_model.generate_content(prompt)
            return {"response": response.text, "sources": sources}
        except Exception as e:
            print(f"Gemini error: {e}")

    # Plain fallback when no LLM is available
    lines = [f"• {b.title} — {b.rating} stars, ₹{b.price}" for b in relevant]
    return {
        "response": (
            f"Here are the most relevant books for \"{query}\":\n\n"
            + "\n".join(lines)
            + "\n\n(Add a GEMINI_API_KEY in Vercel environment settings to enable AI answers.)"
        ),
        "sources": sources
    }
