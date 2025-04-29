import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Base URL for TMDb popular movies
base_url = "https://www.themoviedb.org"
start_url = f"{base_url}/movie"

# Headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# List to store all scraped data
movies_data = []

# Number of pages to scrape (limit to 3 for this example)
max_pages = 3
page_count = 0

print("Starting to scrape themoviedb.org...")
url = start_url
while url and page_count < max_pages:
    # Fetch the page
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an error for bad responses

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract movies from the current page
    movie_cards = soup.find_all("div", class_="card style_1")
    if not movie_cards:
        print("No movies found on this page. Stopping.")
        break

    # Process each movie
    for card in movie_cards:
        # Extract movie title
        title_tag = card.find("h2")
        title = title_tag.get_text(strip=True) if title_tag else "N/A"

        # Extract release year
        release_tag = card.find("p", class_="meta")
        year = "N/A"
        if release_tag:
            release_text = release_tag.get_text(strip=True)
            # The release date is in the format "MMM DD, YYYY" (e.g., "Apr 25, 2025")
            # Extract the year (last 4 characters)
            if len(release_text) >= 4:
                year = release_text[-4:]

        # Extract rating
        rating_tag = card.find("div", class_="user_score_chart")
        rating = "N/A"
        if rating_tag and "data-percent" in rating_tag.attrs:
            rating = f"{rating_tag['data-percent']}%"

        # Add the extracted data to the list
        movies_data.append({
            "title": title,
            "year": year,
            "rating": rating
        })

    # Increment page count
    page_count += 1
    print(f"Scraped page {page_count} with {len(movie_cards)} movies...")

    # Find the "Next" page link
    next_page = soup.find("a", class_="next")
    if next_page and "href" in next_page.attrs and page_count < max_pages:
        next_page_url = next_page["href"]
        url = base_url + next_page_url  # Construct the full URL for the next page
    else:
        print("No more pages to scrape or max pages reached.")
        url = None

    # Add a delay to avoid overloading the server
    time.sleep(1)

# Save the scraped data to a CSV file
if movies_data:
    df = pd.DataFrame(movies_data)
    df.to_csv("tmdb_movies.csv", index=False)
    print(f"Saved {len(movies_data)} movies to tmdb_movies.csv")
else:
    print("No movies were scraped.")
