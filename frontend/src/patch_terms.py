import os

app_path = r"c:\Users\Karthik Reddy\OneDrive\Desktop\KARTHIK\coding vs\project  Book ai automation\frontend\src\App.jsx"

with open(app_path, "r", encoding="utf-8") as f:
    content = f.read()

# Map of complicated terms to simple ones
replacements = {
    "Knowledge Base": "Book Catalog",
    "Ask AI (RAG)": "NSR AI Assistant",
    "Data Pipeline": "Update Books",
    "RAG AI Assistant": "NSR Smart Assistant",
    "Retrieval-Augmented Generation": "AI-Powered Search",
    "Initialize Scraping Engine": "Add New Books",
    "Executing Pipeline...": "Looking for books...",
    "Web Intelligence Scraper": "Book Finder Engine",
    "vector-embedded knowledge base": "online book collection",
    "System Telemetry": "App Status",
    "Vectorized": "Analyzed",
    "Embedded": "Active",
    "ChromaDB embeddings are ready. Vector engine is primed for queries.": "The smart search engine is ready to help you find books.",
    "Your intelligent document processing platform.": "Your smart online bookstore.",
    "Manage your knowledge base and view sales.": "Browse our books and check out our bestsellers.",
    "Navigate to the Scraper to ingest documents.": "Click 'Update Books' to bring in new titles.",
    "Ask a question about the indexed documents?": "Ask me anything about our books!",
    "Hello! I am DocIntel AI. I have full access to our vector knowledge base. What would you like to know about the indexed documents?": "Hello! I am NSR AI. I know everything about the books in our shop. How can I help you today?",
    "Extracted From:": "References:",
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(app_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Simplified terminology in App.jsx")
