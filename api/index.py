"""
Vercel Serverless Entry — Flask-based NSR BOOKS API.
Flask is explicitly supported by @vercel/python.
"""
import json, os, re, sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib.parse import urljoin

app = Flask(__name__)
CORS(app)

# ── Database ──────────────────────────────────────────────────────────────────
_DB = '/tmp/nsr_books.db'

def get_db():
    if not os.path.exists(_DB):
        _init_db()
    return sqlite3.connect(_DB)

def _init_db():
    con = sqlite3.connect(_DB)
    con.executescript("""
        CREATE TABLE IF NOT EXISTS book (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL DEFAULT 'Various Authors',
            price REAL DEFAULT 0,
            rating TEXT,
            description TEXT,
            url TEXT,
            image_url TEXT,
            purchases_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS query_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            response TEXT,
            sources TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    con.commit()
    con.close()

def rows_to_books(rows):
    return [{"id":r[0],"title":r[1],"author":r[2],"price":r[3],"rating":r[4],
             "description":r[5],"url":r[6],"image_url":r[7],"purchases_count":r[8],"created_at":r[9]}
            for r in rows]

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route('/api/health/')
@app.route('/api/health')
def health():
    con = get_db()
    books = con.execute("SELECT COUNT(*) FROM book").fetchone()[0]
    queries = con.execute("SELECT COUNT(*) FROM query_cache").fetchone()[0]
    con.close()
    return jsonify({"status":"healthy","version":"2.0.0","database_connected":True,
                    "document_count":books,"query_count":queries})

@app.route('/api/books/')
@app.route('/api/books')
def books_list():
    con = get_db()
    rows = con.execute(
        "SELECT id,title,author,price,rating,description,url,image_url,purchases_count,created_at FROM book ORDER BY id DESC"
    ).fetchall()
    con.close()
    return jsonify(rows_to_books(rows))

@app.route('/api/books/<int:book_id>/buy/', methods=['POST'])
@app.route('/api/books/<int:book_id>/buy', methods=['POST'])
def buy_book(book_id):
    con = get_db()
    con.execute("UPDATE book SET purchases_count=purchases_count+1 WHERE id=?", (book_id,))
    con.commit()
    count = con.execute("SELECT purchases_count FROM book WHERE id=?", (book_id,)).fetchone()
    con.close()
    return jsonify({"status":"purchase successful","purchases_count": count[0] if count else 0})

@app.route('/api/scrape/', methods=['POST'])
@app.route('/api/scrape', methods=['POST'])
def scrape():
    try:
        import requests as req
        from bs4 import BeautifulSoup
        base = "https://books.toscrape.com/"
        r = req.get(base, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        articles = soup.find_all('article', class_='product_pod')
        con = get_db()
        added = 0
        for article in articles[:20]:
            title_tag = article.h3.a
            title = title_tag.get('title') or title_tag.text
            price_text = article.find('p', class_='price_color').text
            price = float(re.sub(r'[^\d.]', '', price_text) or '0')
            rating_tag = article.find('p', class_='star-rating')
            rating_cls = rating_tag['class'] if rating_tag else []
            rating = next((c for c in rating_cls if c != 'star-rating'), 'Unknown')
            img_src = (article.find('img') or {}).get('src', '')
            image_url = urljoin(base, img_src)
            exists = con.execute("SELECT 1 FROM book WHERE title=?", (title,)).fetchone()
            if not exists:
                con.execute(
                    "INSERT INTO book (title,price,rating,description,url,image_url) VALUES (?,?,?,?,?,?)",
                    (title, price, rating, f"A {rating}-rated book cataloged by NSR BOOKS.", base, image_url)
                )
                added += 1
        con.commit()
        con.close()
        return jsonify({"status":"success","message":f"Cataloged {added} new books.","books_added":added})
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}), 500

@app.route('/api/query/', methods=['POST'])
@app.route('/api/query', methods=['POST'])
def query():
    data = request.get_json(force=True) or {}
    q = data.get('query','').strip()
    if not q:
        return jsonify({"error":"Query is required"}), 400

    con = get_db()
    rows = con.execute("SELECT title,author,price,rating,description FROM book").fetchall()
    if not rows:
        con.close()
        return jsonify({"query":q,"response":"Library is empty. Click 'Update Books' first.","sources":[]})

    qwords = set(q.lower().split())
    scored = sorted(rows, key=lambda r: sum(1 for w in qwords if w in f"{r[0]} {r[4] or ''}".lower()), reverse=True)
    top = scored[:3] or rows[:3]
    sources = [r[0] for r in top]
    context = "\n\n---\n\n".join(
        f"Title: {r[0]}\nAuthor: {r[1]}\nPrice: {r[2]}\nRating: {r[3]}\nDesc: {r[4] or 'N/A'}"
        for r in top
    )

    ai_resp = None
    key = os.environ.get("GEMINI_API_KEY","")
    if key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=key)
            m = genai.GenerativeModel('gemini-1.5-flash')
            ai_resp = m.generate_content(
                f"You are NSR AI. Answer using only these books:\n{context}\n\nQuestion: {q}"
            ).text
        except Exception as e:
            print(f"Gemini error: {e}")

    if not ai_resp:
        ai_resp = f"Books matching \"{q}\":\n" + "\n".join(f"• {r[0]} — {r[3]} stars, ₹{r[2]}" for r in top)

    con.execute("INSERT INTO query_cache (query,response,sources) VALUES (?,?,?)",
                (q, ai_resp, json.dumps(sources)))
    con.commit()
    con.close()
    return jsonify({"query":q,"response":ai_resp,"sources":sources})

@app.route('/api/otp/request/', methods=['POST'])
@app.route('/api/otp/request', methods=['POST'])
def otp_request():
    return jsonify({"status":"success","message":"Auth disabled — direct access enabled."})

@app.route('/api/otp/verify/', methods=['POST'])
@app.route('/api/otp/verify', methods=['POST'])
def otp_verify():
    return jsonify({"status":"verified"})
