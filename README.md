<img width="1911" height="883" alt="Screenshot 2026-04-18 225925" src="https://github.com/user-attachments/assets/ae9eac18-5ae9-45b3-ab5f-fe0a98529de9" /><img width="1911" height="883" alt="Screenshot 2026-04-18 225925" src="https://github.com/user-attachments/assets/b5950067-71c1-41be-9715-7258d6c99523" /># 🧠 Document Intelligence Platform

> A full-stack AI platform that automates web scraping, creates vector embeddings, and provides an intelligent RAG-powered chatbot for semantic document search.

## 🌟 Key Features
- **Automated Web Scraping**: Extracts document metadata and text using Selenium/BeautifulSoup.
- **RAG AI Chatbot**: Intelligent semantic search powered by ChromaDB and Sentence Transformers.
- **LLM Integration**: Context-aware answering using LM Studio / OpenAI.
- **AI Insights**: Automatically generates book summaries, genre classifications, and recommendations.
- **Modern Dashboard**: A premium, glassmorphic React UI with real-time system telemetry.

## 🚀 Quick Setup

**1. Clone & Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**2. Frontend Setup (New Terminal)**
```bash
cd frontend
npm install
npm run dev
```

## 🔌 Core API Endpoints
- `GET /api/books/` - Retrieve indexed documents from the database.
- `POST /api/scrape/` - Trigger the automated web crawler.
- `POST /api/query/` - Submit a query to the RAG AI pipeline.
- `GET /api/health/` - Check vector database and API health.

## 💬 Sample RAG Q&A
**User**: *"What are some classic books involving a futuristic dystopia?"*  
**AI**: *"Based on our indexed library, '1984' by George Orwell is highly relevant. The document explores themes of surveillance and totalitarianism."*  
**Sources**: `[1984 (ID: 402)]`

## 📸 Screenshots
*(Insert Screenshot 1: Main Dashboard here)*
*(Insert Screenshot 2: RAG AI Chat Interface here)*
*(Insert Screenshot 3: Data Scraper Pipeline here)*








