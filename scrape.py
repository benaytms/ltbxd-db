import requests
from bs4 import BeautifulSoup
import time
import click
import sys


def get_film_genres(slug: str) -> list[str]:
    try:
        url_movie = f"https://letterboxd.com/film/{slug}/"
        response = requests.get(url_movie, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        genre_links = soup.select("a[href*='/films/genre/']")
        genre_list = [a.text.lower().strip().replace(' ', '_') for a in genre_links]
        print(genre_list)
        return genre_list
    except Exception as e:
        click.echo(f"Error fetching genres for '{slug}': {e}")
        return []


def parse_films(user: str) -> list[dict]:
    """Scrape a Letterboxd watchlist, return list of {title, year, genres}."""
    headers = {"User-Agent": "Mozilla/5.0"}
    movies = []
    page = 1

    while True:
        url_wl = f"https://letterboxd.com/{user}/watchlist/page/{page}/"
        try:
            response = requests.get(url_wl, headers=headers)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            click.echo("Connection error, retrying in 5s...")
            time.sleep(5)
            continue
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code
            if status == 403:
                click.echo("This user's watchlist is private.")
                sys.exit(1)
            elif status == 404:
                click.echo(f"User {user} not found.")
                sys.exit(1)

        soup = BeautifulSoup(response.text, "html.parser")
        posters = soup.find_all("div", {"data-component-class": "LazyPoster"})

        for movie in posters:
            raw = movie["data-item-name"]
            slug = str(movie["data-item-slug"])
            genres = get_film_genres(slug)

            if '(' in raw and raw.endswith(')'): # type: ignore
                name, year = raw.rsplit(" (", 1) # type: ignore
                movies.append({"title": name, "year": int(year.rstrip(")")), "genres": genres})
            else:
                movies.append({"title": raw, "year": None, "genres": genres})

        if len(posters) < 28:
            break
        page += 1
        time.sleep(1.5)

    return movies


if __name__ == "__main__":
    pass