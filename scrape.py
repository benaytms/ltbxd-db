import requests
from bs4 import BeautifulSoup
import time
import click
import sys

def parse_films(user: str) -> list[dict]:
    """
        Scrape a Letterboxd watchlist, return list of {title, year}.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    movies = []
    page = 1

    while True:
        url = f"https://letterboxd.com/{user}/watchlist/page/{page}/"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            print("Connection error, retrying in 5s...")
            time.sleep(5)
            continue
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code
            if status == 403:
                click.echo("This user's watchlist is private.")
                sys.exit(1)
            elif status == 404:
                click.echo("User not found.")
                sys.exit(1)

        soup = BeautifulSoup(response.text, "html.parser")
        posters = soup.find_all("div", {"data-component-class": "LazyPoster"})

        for movie in posters:
            raw = movie["data-item-name"]
            if '(' in raw and raw.endswith(')'): # type: ignore
                name, year = raw.rsplit(" (", 1) # type: ignore
                movies.append({"title": name, "year": int(year.rstrip(")"))})
            else:
                movies.append({"title": raw, "year": None})

        if len(posters) < 28:
            break
        page += 1
        time.sleep(1)

    return movies