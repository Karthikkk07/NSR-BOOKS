import os
from openai import OpenAI
from .models import Book

# Initialize AI Client
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

AI_PROVIDER = os.environ.get("AI_PROVIDER", "gemini")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "lm-studio")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "http://localhost:1234/v1")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

llm_client = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)

if HAS_GEMINI and AI_PROVIDER == "gemini" and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    gemini_model = None

# Use in-memory ChromaDB — works on serverless (Vercel) and locally
# PersistentClient crashes on Vercel because filesystem is read-only
try:
    import chromadb
    _chroma_client = chromadb.EphemeralClient()
    _collection = _chroma_client.get_or_create_collection(name="documents")
    CHROMA_AVAILABLE = True
except Exception as e:
    print(f"ChromaDB init error (non-fatal): {e}")
    CHROMA_AVAILABLE = False
    _collection = None


def generate_embeddings(text):
    """Generates dense vector embeddings for text using Gemini API"""
    if AI_PROVIDER == "gemini" and HAS_GEMINI and GEMINI_API_KEY:
        try:
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"Gemini Embedding Error: {e}")
            raise
    else:
        print("Warning: No cloud embedding provider configured. Returning zero vector.")
        return [0.0] * 768  # Gemini embedding-001 produces 768-dim vectors


def index_document(book):
    """Embeds a document and inserts it into ChromaDB"""
    if not CHROMA_AVAILABLE or _collection is None:
        return
    doc_id = str(book.id)
    text_content = f"Title: {book.title}. Author: {book.author}. Price: {book.price}. Rating: {book.rating}. Description: {book.description}"
    try:
        existing = _collection.get(ids=[doc_id])
        if not existing['ids']:
            embedding = generate_embeddings(text_content)
            _collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[text_content],
                metadatas=[{"title": book.title, "url": book.url or ""}]
            )
    except Exception as e:
        print(f"Index error: {e}")


def process_rag_query(query):
    """Runs the full RAG pipeline: Embedding -> Similarity Search -> LLM Generation"""
    books = Book.objects.all()
    if not books.exists():
        return {
            "response": "The knowledge base is currently empty. Please use the 'Update Books' scraper to add books first.",
            "sources": []
        }

    # If ChromaDB isn't available, do a simple keyword search fallback
    if not CHROMA_AVAILABLE or _collection is None:
        book_list = ", ".join([b.title for b in books[:5]])
        return {
            "response": f"Vector search is temporarily unavailable. Here are some books in the store: {book_list}",
            "sources": []
        }

    try:
        # Index all books into the in-memory collection (since it's ephemeral)
        for book in books:
            index_document(book)

        # 1. Generate query embedding
        query_embedding = generate_embeddings(query)

        # 2. Similarity Search in ChromaDB (Top 3 closest matches)
        n = min(3, books.count())
        results = _collection.query(
            query_embeddings=[query_embedding],
            n_results=n
        )

        if not results['documents'][0]:
            return {"response": "No relevant documents found in the Vector DB.", "sources": []}

        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        sources = [meta['title'] for meta in metadatas]

        # 3. Context Building
        context = "\n\n".join(documents)

        # 4. Answer Generation with LLM
        prompt = f"""You are a helpful book recommendation AI for NSR BOOKS.
        Answer the user's query using ONLY the following context retrieved from the book database.
        If the answer is not contained in the context, say "I don't have enough information based on the available books."

        Context:
        {context}

        Query: {query}
        """

        if AI_PROVIDER == "gemini" and gemini_model is not None:
            response = gemini_model.generate_content(prompt)
            ai_response = response.text
        else:
            response = llm_client.chat.completions.create(
                model="local-model",
                messages=[
                    {"role": "system", "content": "You are NSR AI, a helpful book assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            ai_response = response.choices[0].message.content

        return {"response": ai_response, "sources": sources}

    except Exception as e:
        print(f"RAG Error: {e}")
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "API key" in error_msg:
            return {
                "response": "⚠️ Invalid Gemini API Key. Please check your GEMINI_API_KEY environment variable in Vercel.",
                "sources": []
            }
        return {
            "response": f"⚠️ AI service error: {str(e)}",
            "sources": []
        }
