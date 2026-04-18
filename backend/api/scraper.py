import requests
import re
from bs4 import BeautifulSoup
from .models import Book
from .rag import index_document

def scrape_books_toscrape(limit=10):
    url = "https://books.toscrape.com/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return {"status": "error", "message": f"Connection failed: {str(e)}"}

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article', class_='product_pod')
    
    added = 0
    for article in articles[:limit]:
        title = article.h3.a['title']
        price_text = article.find('p', class_='price_color').text
        price_clean = re.sub(r'[^\d.]', '', price_text)
        rating_class = article.find('p', class_='star-rating')['class']
        rating = [r for r in rating_class if r != 'star-rating'][0]
        
        # Extract image
        img_tag = article.find('img')
        img_src = img_tag['src'] if img_tag else ""
        if img_src.startswith("../"):
            img_src = img_src.replace("../", "")
        image_url = url + img_src

        # Avoid duplicates
        if not Book.objects.filter(title=title).exists():
            book = Book.objects.create(
                title=title,
                author="Unknown Author",
                price=float(price_clean),
                rating=rating,
                description=f"A great book with a {rating} star rating. Automatically indexed for semantic search.",
                url=url,
                image_url=image_url
            )
            # Add to ChromaDB vector store
            index_document(book)
            added += 1
            
    return {"status": "success", "message": f"Successfully scraped {limit} items. {added} new documents added to Vector DB.", "books_added": added}
