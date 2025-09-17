# full_scale_used_goods_comparator.py
# This is a full-scale prototype implementation of the described project: a web application that scrapes used goods from various Korean marketplaces,
# rates items based on quality, age, and descriptions, calculates suggested prices, and provides a user interface for searching and viewing comparisons.
# 
# IMPORTANT LEGAL AND ETHICAL NOTES:
# - Web scraping may violate the terms of service of the targeted websites (e.g., Carrot Market, Joong-go Nara, Bungae Jangtu).
#   Always check and comply with their policies, robots.txt, and applicable laws (e.g., in Korea, data protection laws).
# - This code is for educational purposes only. Do not deploy it without proper permissions or API access.
# - In a production environment, use official APIs if available, or obtain consent.
# - Anti-scraping measures (e.g., CAPTCHA, rate limiting) are not handled here; real-world use would require ethical alternatives.
# 
# Technologies used:
# - Backend: Flask (web framework)
# - Database: SQLite (for storing scraped data temporarily; in production, use PostgreSQL or MongoDB)
# - Scraping: BeautifulSoup + requests (simple; for JS-heavy sites, consider Selenium or Scrapy)
# - NLP/Rating: Basic keyword-based analysis (for faults, age); extend with spaCy or KoNLPy for Korean NLP
# - Frontend: Jinja templates with Bootstrap for professional UI
# - Monetization: Placeholder for Stripe integration (subscriptions); not fully implemented here
# - Hosting: Instructions at the end for deploying to Heroku or AWS
# 
# Project Structure (assume files in a directory):
# - app.py (this file: main Flask app)
# - models.py (DB models)
# - scraper.py (scraping logic)
# - rater.py (rating and pricing logic)
# - templates/ (HTML templates: base.html, index.html, results.html)
# - static/ (CSS/JS: use Bootstrap CDN for simplicity)
# - requirements.txt (dependencies)
# 
# To run locally:
# 1. pip install -r requirements.txt
# 2. python app.py
# 3. Visit http://localhost:5000
# 
# For production: See hosting section at the end.

# --- requirements.txt content (commented out; create a separate file) ---
# flask==3.0.3
# requests==2.32.3
# beautifulsoup4==4.12.3
# sqlite3 (built-in)
# --- End requirements.txt ---

import sqlite3
from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import datetime
from urllib.parse import quote

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('used_goods.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items
                 (id INTEGER PRIMARY KEY, site TEXT, title TEXT, price REAL, description TEXT, age INTEGER, quality TEXT, image_url TEXT, rating REAL, suggested_price REAL)''')
    conn.commit()
    conn.close()

init_db()

# Scraper functions (placeholder for specific sites; adapt selectors based on site HTML)
def scrape_carrot_market(query):
    # Carrot Market (daangn.com) - Example URL structure; this is hypothetical and may change
    url = f"https://www.daangn.com/search/{quote(query)}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    items = []
    for item in soup.find_all('article', class_='flea-market-article'):  # Hypothetical class; inspect actual site
        title = item.find('h2').text.strip() if item.find('h2') else 'N/A'
        price_str = item.find('p', class_='article-price').text.strip() if item.find('p', class_='article-price') else '0'
        price = float(re.sub(r'[^\d]', '', price_str)) if price_str else 0.0
        description = item.find('p', class_='article-content').text.strip() if item.find('p', class_='article-content') else ''
        image_url = item.find('img')['src'] if item.find('img') else ''
        age = extract_age(description)  # Custom function
        quality = extract_quality(description)
        items.append({'site': 'Carrot Market', 'title': title, 'price': price, 'description': description, 'age': age, 'quality': quality, 'image_url': image_url})
    return items

def scrape_joonggo_nara(query):
    # Joong-go Nara (joonggonara.co.kr) - Hypothetical
    url = f"https://web.joonggonara.co.kr/search?searchword={quote(query)}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    items = []
    for item in soup.find_all('div', class_='item'):  # Hypothetical
        title = item.find('a', class_='title').text.strip()
        price_str = item.find('span', class_='price').text.strip()
        price = float(re.sub(r'[^\d]', '', price_str))
        description = item.find('div', class_='desc').text.strip()
        image_url = item.find('img')['src']
        age = extract_age(description)
        quality = extract_quality(description)
        items.append({'site': 'Joong-go Nara', 'title': title, 'price': price, 'description': description, 'age': age, 'quality': quality, 'image_url': image_url})
    return items

def scrape_bungae_jangtu(query):
    # Bungae Jangtu (bunjang.co.kr) - Hypothetical
    url = f"https://m.bunjang.co.kr/search/products?q={quote(query)}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    items = []
    for item in soup.find_all('div', class_='sc-kAzzGY'):  # Hypothetical; use actual classes
        title = item.find('div', class_='name').text.strip()
        price_str = item.find('div', class_='price').text.strip()
        price = float(re.sub(r'[^\d]', '', price_str))
        description = item.find('div', class_='desc').text.strip()
        image_url = item.find('img')['src']
        age = extract_age(description)
        quality = extract_quality(description)
        items.append({'site': 'Bungae Jangtu', 'title': title, 'price': price, 'description': description, 'age': age, 'quality': quality, 'image_url': image_url})
    return items

# Helper functions for extraction (basic regex/keywords; improve with NLP)
def extract_age(description):
    # Extract age in years; e.g., "1년 사용" -> 1
    match = re.search(r'(\d+)\s*년', description)
    return int(match.group(1)) if match else 0

def extract_quality(description):
    # Basic fault detection; keywords for faults
    faults = ['고장', '파손', '스크래치', '오염', '손상']  # Korean for broken, damaged, scratch, stained, etc.
    if any(fault in description for fault in faults):
        return 'Poor'
    return 'Good'

# Rating and Pricing Logic
def rate_item(item):
    # Rating: 0-10 scale; lower for older/higher faults
    age_penalty = min(item['age'] / 5, 1.0)  # Max penalty at 5+ years
    quality_score = 1.0 if item['quality'] == 'Good' else 0.5
    rating = 10 * (1 - age_penalty) * quality_score
    return round(rating, 1)

def calculate_suggested_price(items, original_price=0):
    # Average price, adjusted by ratings; assume original_price provided or scraped
    if not items:
        return 0.0
    avg_price = sum(item['price'] for item in items) / len(items)
    avg_rating = sum(item['rating'] for item in items) / len(items)
    suggested = avg_price * (avg_rating / 10) if original_price == 0 else (original_price * 0.5) + (avg_price * 0.5)
    return round(suggested, 2)

# Store scraped items in DB
def store_items(items):
    conn = sqlite3.connect('used_goods.db')
    c = conn.cursor()
    for item in items:
        item['rating'] = rate_item(item)
        c.execute('''INSERT INTO items (site, title, price, description, age, quality, image_url, rating)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (item['site'], item['title'], item['price'], item['description'], item['age'], item['quality'], item['image_url'], item['rating']))
    conn.commit()
    conn.close()

# Routes
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    # Scrape from multiple sites
    items = scrape_carrot_market(query) + scrape_joonggo_nara(query) + scrape_bungae_jangtu(query)
    # Store in DB (for persistence and monetized features)
    store_items(items)
    # Calculate suggested price (assume original_price=0 for simplicity; user can input)
    suggested_price = calculate_suggested_price(items)
    # For monetization: In production, check user subscription; here, show all
    return render_template('results.html', items=items, query=query, suggested_price=suggested_price)

# API for monetized features (e.g., detailed reports)
@app.route('/api/detailed_report', methods=['GET'])
def detailed_report():
    # Placeholder: Require subscription (integrate Stripe)
    # For now, return JSON of items
    conn = sqlite3.connect('used_goods.db')
    c = conn.cursor()
    c.execute('SELECT * FROM items')
    items = c.fetchall()
    conn.close()
    return jsonify(items)

if __name__ == '__main__':
    app.run(debug=True)

# --- templates/base.html (create in templates/ folder) ---
"""
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Used Goods Comparator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

# --- templates/index.html ---
"""
{% extends 'base.html' %}
{% block content %}
<h1 class="mt-5">Used Goods Price Comparator</h1>
<form method="post" action="/search" class="mt-3">
    <div class="input-group">
        <input type="text" class="form-control" name="query" placeholder="Search for an item (e.g., iPhone 12)" required>
        <button type="submit" class="btn btn-primary">Search</button>
    </div>
</form>
<p class="mt-3">Premium features: Subscribe for detailed ratings and purchasing options.</p>
{% endblock %}
"""

# --- templates/results.html ---
"""
{% extends 'base.html' %}
{% block content %}
<h1 class="mt-5">Results for "{{ query }}"</h1>
<p>Suggested Price: {{ suggested_price }} KRW</p>
<table class="table table-striped">
    <thead>
        <tr>
            <th>Site</th>
            <th>Title</th>
            <th>Price (KRW)</th>
            <th>Age (years)</th>
            <th>Quality</th>
            <th>Rating (0-10)</th>
            <th>Image</th>
        </tr>
    </thead>
    <tbody>
        {% for item in items %}
        <tr>
            <td>{{ item.site }}</td>
            <td>{{ item.title }}</td>
            <td>{{ item.price }}</td>
            <td>{{ item.age }}</td>
            <td>{{ item.quality }}</td>
            <td>{{ item.rating }}</td>
            <td><img src="{{ item.image_url }}" alt="Item Image" width="100"></td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
"""

# Hosting Instructions:
# 1. Heroku (free tier for prototyping):
#    - Install Heroku CLI
#    - heroku create myapp
#    - Add Procfile: web: python app.py
#    - git init, add/commit, git push heroku master
#    - heroku ps:scale web=1
# 2. AWS (for scalability):
#    - Use EC2 or Elastic Beanstalk
#    - Upload code, install dependencies, run with gunicorn: gunicorn app:app
#    - Manage traffic with ELB, data with RDS
# 3. Monetization:
#    - Integrate Stripe: pip install stripe
#    - Add routes for /subscribe, use Stripe API for payments
#    - Example: stripe.Charge.create(amount=500, currency="krw", source="tok_visa")
#    - For safety: Add user auth (Flask-Login), HTTPS, input validation

# Expansion Ideas:
# - Add more sites via modular scrapers
# - Use ML for better rating (e.g., sentiment analysis on descriptions)
# - Purchasing: Integrate payment gateways, but ensure compliance with e-commerce laws
# - Traffic management: Use Redis for caching, Celery for async scraping