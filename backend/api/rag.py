import os
import chromadb
from openai import OpenAI
from openai import OpenAI
from .models import Book

# Initialize ChromaDB Vector Store
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="documents")

# AI Client configuration moved below imports

# Initialize AI Client
# Fallback to OpenAI API/LM Studio if an API key is provided
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

if HAS_GEMINI and AI_PROVIDER == "gemini":
    genai.configure(api_key=GEMINI_API_KEY)
    # Using the correct model name (gemini-1.5-flash)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    gemini_model = None

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
            # Fallback or re-raise
            raise
    else:
        # Fallback to a mock or error if no cloud provider is configured
        print("Warning: No cloud embedding provider configured. Returning zero vector.")
        return [0.0] * 384 # 384 is the size for MiniLM, but Gemini is 768. 
        # Actually, if we change providers, we might need to reset the vector DB.
        # Gemini embedding-001 is 768.

def index_document(book):
    """Embeds a document and inserts it into ChromaDB"""
    doc_id = str(book.id)
    text_content = f"Title: {book.title}. Author: {book.author}. Price: {book.price}. Rating: {book.rating}. Description: {book.description}"
    
    # Check if already indexed
    existing = collection.get(ids=[doc_id])
    if not existing['ids']:
        embedding = generate_embeddings(text_content)
        collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text_content],
            metadatas=[{"title": book.title, "url": book.url}]
        )

def process_rag_query(query):
    """Runs the full RAG pipeline: Embedding -> Similarity Search -> LLM Generation"""
    books = Book.objects.all()
    if not books.exists():
        return {
            "response": "The knowledge base is currently empty. Please navigate to the Data Scraper and fetch documents before running RAG queries.", 
            "sources": []
        }

    try:
        # 1. Generate query embedding
        query_embedding = generate_embeddings(query)
        
        # 2. Similarity Search in ChromaDB (Top 3 closest matches)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )
        
        if not results['documents'][0]:
            return {"response": "No relevant documents found in the Vector DB.", "sources": []}
            
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        sources = [meta['title'] for meta in metadatas]
        
        # 3. Context Building
        context = "\n\n".join(documents)
        
        # 4. Answer Generation with LLM
        prompt = f"""You are a helpful Document Intelligence AI. 
        Answer the user's query using ONLY the following context retrieved from the database.
        Provide insights such as summary, genre classification, or recommendations if relevant to the query.
        If the answer is not contained in the context, say "I don't have enough information based on the indexed documents."
        
        Context:
        {context}
        
        Query: {query}
        """
        
        if AI_PROVIDER == "gemini" and gemini_model is not None:
            prompt_with_system = f"System: You are DocIntel AI, an intelligent RAG assistant.\n\nUser: {prompt}"
            response = gemini_model.generate_content(prompt_with_system)
            ai_response = response.text
        else:
            response = llm_client.chat.completions.create(
                model="local-model", # Used by LM Studio
                messages=[
                    {"role": "system", "content": "You are DocIntel AI, an intelligent RAG assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            ai_response = response.choices[0].message.content
        
        return {"response": ai_response, "sources": sources}
        
    except Exception as e:
        print(f"RAG Error: {e}")
        # Return graceful degradation if LLM is offline or missing API key
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "400" in error_msg or "API key" in error_msg:
            return {
                "response": "⚠️ System Error: Invalid API Key. Please provide a valid Gemini API Key in the backend/.env file.",
                "sources": sources if 'sources' in locals() else []
            }
        return {
            "response": f"⚠️ System Error: Could not connect to the LLM (Provider: {AI_PROVIDER}). Make sure LM Studio is running or your API Key is correct. Error: {str(e)}",
            "sources": sources if 'sources' in locals() else []
        }
