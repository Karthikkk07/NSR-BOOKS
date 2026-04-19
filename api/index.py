"""
Vercel Serverless Python Handler for NSR BOOKS API.

Pure Python — no Django import at module level.
Uses sqlite3 (stdlib), requests, beautifulsoup4, google-generativeai.
All available on Vercel with zero native extension issues.
"""

import json
import os
import sqlite3
import re
from http.server import BaseHTTPRequestHandler
from urllib.parse import urljoin, urlparse, parse_qs

# ── DB Path ───────────────────────────────────────────────────────────────────
# Vercel is read-only except /tmp — copy db there if it exists
_ORIG_DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'db.sqlite3')
_TMP_DB  = '/tmp/nsr_books.db'

def _get_db():
    """Return a connection to a writable SQLite database in /tmp."""
    if not os.path.exists(_TMP_DB):
        # First cold start: create the schema from scratch
        _init_db(_TMP_DB)
    return sqlite3.connect(_TMP_DB)

def _init_db(path):
    """Create all required tables."""
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS api_book (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            price REAL,
            rating TEXT,
            description TEXT,
            url TEXT,
            image_url TEXT,
            purchases_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS api_querycache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            sources TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    con.commit()
    con.close()


# ── Helpers ───────────────────────────────────────────────────────────────────
def _json_resp(handler, data, status=200):
    body = json.dumps(data).encode()
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json')
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    handler.send_header('Access-Control-Allow-Headers', 'Content-Type')
    handler.send_header('Content-Length', str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _read_body(handler):
    length = int(handler.headers.get('Content-Length', 0))
    if length:
        return json.loads(handler.rfile.read(length))
    return {}


# ── Route Handlers ────────────────────────────────────────────────────────────
def handle_health(handler, method, params, body):
    con = _get_db()
    book_count = con.execute("SELECT COUNT(*) FROM api_book").fetchone()[0]
    query_count = con.execute("SELECT COUNT(*) FROM api_querycache").fetchone()[0]
    con.close()
    _json_resp(handler, {
        "status": "healthy",
        "version": "1.0.0",
        "database_connected": True,
        "document_count": book_count,
        "query_count": query_count
    })


def handle_books_list(handler, method, params, body):
    con = _get_db()
    rows = con.execute(
        "SELECT id, title, author, price, rating, description, url, image_url, purchases_count, created_at FROM api_book ORDER BY id DESC"
    ).fetchall()
    con.close()
    books = [
        {"id": r[0], "title": r[1], "author": r[2], "price": r[3], "rating": r[4],
         "description": r[5], "url": r[6], "image_url": r[7], "purchases_count": r[8], "created_at": r[9]}
        for r in rows
    ]
    _json_resp(handler, books)


def handle_book_buy(handler, book_id):
    con = _get_db()
    con.execute("UPDATE api_book SET purchases_count = purchases_count + 1 WHERE id=?", (book_id,))
    con.commit()
    count = con.execute("SELECT purchases_count FROM api_book WHERE id=?", (book_id,)).fetchone()
    con.close()
    _json_resp(handler, {"status": "purchase successful", "purchases_count": count[0] if count else 0})


def handle_scrape(handler, method, params, body):
    try:
        import requests
        from bs4 import BeautifulSoup
        from urllib.parse import urljoin

        base_url = "https://books.toscrape.com/"
        resp = requests.get(base_url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        articles = soup.find_all('article', class_='product_pod')

        con = _get_db()
        added = 0
        for article in articles[:20]:
            title_tag = article.h3.a
            title = title_tag.get('title') or title_tag.text
            price_text = article.find('p', class_='price_color').text
            price = float(re.sub(r'[^\d.]', '', price_text) or '0')
            rating_tag = article.find('p', class_='star-rating')
            rating_cls = rating_tag['class'] if rating_tag else []
            rating = next((r for r in rating_cls if r != 'star-rating'), 'Unknown')
            img_tag = article.find('img')
            img_src = img_tag['src'] if img_tag else ''
            image_url = urljoin(base_url, img_src)

            exists = con.execute("SELECT 1 FROM api_book WHERE title=?", (title,)).fetchone()
            if not exists:
                con.execute(
                    "INSERT INTO api_book (title, author, price, rating, description, url, image_url) VALUES (?,?,?,?,?,?,?)",
                    (title, "Various Authors", price, rating,
                     f"A {rating}-rated book. Cataloged for NSR BOOKS.", base_url, image_url)
                )
                added += 1
        con.commit()
        con.close()
        _json_resp(handler, {"status": "success", "message": f"Successfully cataloged {added} new books.", "books_added": added})
    except Exception as e:
        _json_resp(handler, {"status": "error", "message": str(e)}, 500)


def handle_query(handler, method, params, body):
    query = body.get('query', '').strip()
    if not query:
        _json_resp(handler, {"error": "Query is required"}, 400)
        return

    con = _get_db()
    rows = con.execute("SELECT title, author, price, rating, description FROM api_book").fetchall()
    con.close()

    if not rows:
        _json_resp(handler, {
            "query": query,
            "response": "The library is empty. Click 'Update Books' to add books first.",
            "sources": []
        })
        return

    # Keyword search
    query_words = set(query.lower().split())
    scored = []
    for r in rows:
        text = f"{r[0]} {r[4] or ''} {r[3] or ''}".lower()
        score = sum(1 for w in query_words if w in text)
        scored.append((score, r))
    scored.sort(key=lambda x: x[0], reverse=True)
    relevant = [r for _, r in scored[:3]] or rows[:3]
    sources = [r[0] for r in relevant]

    context = "\n\n---\n\n".join(
        f"Title: {r[0]}\nAuthor: {r[1]}\nPrice: {r[2]}\nRating: {r[3]}\nDescription: {r[4] or 'N/A'}"
        for r in relevant
    )

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    ai_response = None
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = (
                "You are NSR AI, a friendly book assistant.\n"
                "Answer using ONLY the books below. If not available, say so politely.\n\n"
                f"Books:\n{context}\n\nQuestion: {query}"
            )
            ai_response = model.generate_content(prompt).text
        except Exception as e:
            print(f"Gemini error: {e}")

    if not ai_response:
        lines = [f"• {r[0]} — {r[3]} stars, ₹{r[2]}" for r in relevant]
        ai_response = f"Books matching \"{query}\":\n\n" + "\n".join(lines)

    con = _get_db()
    con.execute("INSERT INTO api_querycache (query, response, sources) VALUES (?,?,?)",
                (query, ai_response, json.dumps(sources)))
    con.commit()
    con.close()

    _json_resp(handler, {"query": query, "response": ai_response, "sources": sources})


# ── Router ────────────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress default access logs

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _route(self, method):
        path = urlparse(self.path).path.rstrip('/')
        body = _read_body(self) if method in ('POST', 'PUT', 'PATCH') else {}

        # /api/health/
        if path in ('/api/health', '/api/health/'):
            return handle_health(self, method, {}, body)

        # /api/books/
        if path in ('/api/books', '/api/books/') and method == 'GET':
            return handle_books_list(self, method, {}, body)

        # /api/books/<id>/buy/
        m = re.match(r'^/api/books/(\d+)/buy/?$', path)
        if m and method == 'POST':
            return handle_book_buy(self, int(m.group(1)))

        # /api/scrape/
        if path in ('/api/scrape', '/api/scrape/') and method == 'POST':
            return handle_scrape(self, method, {}, body)

        # /api/query/
        if path in ('/api/query', '/api/query/') and method == 'POST':
            return handle_query(self, method, {}, body)

        _json_resp(self, {"error": "Not found", "path": path}, 404)

    def do_GET(self):  self._route('GET')
    def do_POST(self): self._route('POST')
    def do_PUT(self):  self._route('PUT')
    def do_DELETE(self): self._route('DELETE')


# Vercel expects 'app' to be the WSGI/handler callable
app = Handler
