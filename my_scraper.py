import os
import requests
import psycopg2
from bs4 import BeautifulSoup
from dotenv import load_dotenv

def fetch_reviews(movie_name):
    search_term = movie_name.lower().replace(" ", "-")
    url = f"https://letterboxd.com/film/{search_term}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    review_elements = soup.select(".review .body")
    reviews = [review.get_text(strip=True) for review in review_elements if review.get_text(strip=True)]
    return reviews[:5]

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def scrape_and_save_reviews(username):
    url = f"https://letterboxd.com/{username}/films/reviews/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

reviews = []

    for review_block in soup.select('.film-detail-content'):
        movie_title_tag = review_block.select_one('.headline-3')
        review_text_tag = review_block.select_one('.body-text')
        date_tag = review_block.select_one('.attribution-date')

        if movie_title_tag:
            movie_title = movie_title_tag.get_text(strip=True)
            review_text = review_text_tag.get_text(strip=True) if review_text_tag else ''
            review_date = date_tag.get_text(strip=True) if date_tag else None

            reviews.append((username, movie_title, review_text, review_date))

    # Insert reviews into DB
    conn = get_db_connection()
    cur = conn.cursor()
    for review in reviews:
        cur.execute(
            """
            INSERT INTO reviews (reviewer, movie_title, review_text, review_date)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
            """,
            review
        )
    conn.commit()
    cur.close()
    conn.close()

    return len(reviews)