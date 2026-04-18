import requests
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .models import Book
from .rag import index_document

def scrape_books_toscrape(limit=10):
    base_url = "https://books.toscrape.com/"
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return {"status": "error", "message": f"Connection failed: {str(e)}"}

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article', class_='product_pod')
    
    added = 0
    for article in articles[:limit]:
        # Robust title extraction
        title_tag = article.h3.a
        title = title_tag.get('title') or title_tag.text
        
        # Robust price parsing
        price_text = article.find('p', class_='price_color').text
        price_clean = re.sub(r'[^\d.]', '', price_text)
        
        # Robust rating extraction
        rating_tag = article.find('p', class_='star-rating')
        rating_class = rating_tag['class'] if rating_tag else []
        rating = [r for r in rating_class if r != 'star-rating'][0] if rating_class else "Unknown"
        
        # Robust image URL with urljoin
        img_tag = article.find('img')
        img_src = img_tag['src'] if img_tag else ""
        image_url = urljoin(base_url, img_src)

        # Avoid duplicates
        if not Book.objects.filter(title=title).exists():
            book = Book.objects.create(
                title=title,
                author="Various Authors",
                price=float(price_clean) if price_clean else 0.0,
                rating=rating,
                description=f"A professional book discovery with a {rating} rating. Cataloged for NSR BOOKS AI Intelligence.",
                url=base_url,
                image_url=image_url
            )
            # Add to ChromaDB vector store
            try:
                index_document(book)
            except Exception as e:
                print(f"Indexing error: {e}")
            added += 1
            
    return {"status": "success", "message": f"Successfully cataloged {added} new books for NSR BOOKS.", "books_added": added}
