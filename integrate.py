import click
import logging
import time
from random import sample
from scrape import parse_films
from db import create_tables, sync_user_watchlist, get_user_movies

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s) %(message)s'
)

logger = logging.Logger(__name__)


def fetch_or_scrape(username: str) -> list[dict]:
    """Always scrape fresh, sync DB, return full watchlist."""
    movies = parse_films(username)
    result = sync_user_watchlist(username, movies)
    logger.info(f"Sync complete — {result['added']} new, {result['already_had']} already stored.")
    return movies


def select_random(movies: list[dict]) -> list[dict] | None:
    n = int(input("How many to select: "))
    if n == 0:
        return None
    if n < 0 or n > len(movies):
        click.echo("Invalid number.")
        return None
    return sample(movies, n)


# cli.py
@click.command()
@click.option('--user', required=True, help='Letterboxd username')
@click.option('--sync', is_flag=True, default=False, help='Re-scrape and sync new movies')
def main(user: str, sync: bool):
    create_tables()

    existing = get_user_movies(user)

    if existing is None:
        # new user — scrape and store
        click.echo(f"New user, scraping watchlist...")
        movies = parse_films(user)
        sync_user_watchlist(user, movies)
    elif sync:
        # returning user requesting a refresh
        click.echo(f"Syncing watchlist for '{user}'...")
        movies = parse_films(user)
        result = sync_user_watchlist(user, movies)
        click.echo(f"{result['added']} new movies added.")
    else:
        # returning user, just use what's in the DB
        movies = existing
        click.echo(f"Loaded {len(movies)} movies from database.")

    selected = select_random(movies)
    if selected is None:
        click.echo("No movies selected.")
        return

    click.echo("\nSelected movies:")
    for movie in selected:
        click.echo(f"  {movie['title']} ({movie['year'] or 'N/A'})")
        time.sleep(1.5)


if __name__ == "__main__":
    #main()
    parse_films('ye4rz3r0')