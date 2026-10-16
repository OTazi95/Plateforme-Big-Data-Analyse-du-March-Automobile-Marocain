import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time, random
from scraper_utils import save_to_bronze

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AutoBot/1.0)"}

def scrape_wandaloo(max_pages=3):
    articles = []
    for page in range(1, max_pages + 1):
        url = f"https://www.wandaloo.com/occasion/maroc/?page={page}"
        print(f"Scraping Wandaloo page {page}")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")
            listings = soup.select(".voiture-occasion, .car-item, article")
            for item in listings:
                try:
                    title = item.select_one("h2, h3, .title, .car-title")
                    price = item.select_one(".price, .prix, [class*='price']")
                    km = item.select_one("[class*='km'], [class*='kilometrage']")
                    year = item.select_one("[class*='year'], [class*='annee']")
                    fuel = item.select_one("[class*='fuel'], [class*='carburant']")
                    link = item.select_one("a")
                    article = {
                        "source": "wandaloo.com",
                        "titre": title.get_text(strip=True) if title else None,
                        "prix": price.get_text(strip=True) if price else None,
                        "kilometrage": km.get_text(strip=True) if km else None,
                        "annee": year.get_text(strip=True) if year else None,
                        "carburant": fuel.get_text(strip=True) if fuel else None,
                        "url": link["href"] if link and link.get("href") else None,
                        "date_publication": datetime.now().isoformat(),
                        "scraped_at": datetime.now().isoformat(),
                    }
                    articles.append(article)
                except Exception as e:
                    print(f"  Erreur: {e}")
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            print(f"Erreur page {page}: {e}")
    return articles

if __name__ == "__main__":
    data = scrape_wandaloo(max_pages=3)
    print(f"📦 {len(data)} annonces Wandaloo collectées")
    save_to_bronze(data, "wandaloo")