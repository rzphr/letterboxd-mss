import requests
from bs4 import BeautifulSoup

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
