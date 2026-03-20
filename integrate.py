import click
import logging
from random import sample
from scrape import parse_films
from db import create_tables, add_user_watchlist, get_user_movies

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s) %(message)s'
)


def fetch_or_scrape(username: str) -> list[dict]:
    """Check DB first, scrape only if user isn't stored yet."""
    movies = get_user_movies(username)
    if movies is not None:
        return movies
    movies = parse_films(username)
    add_user_watchlist(username, movies)
    return movies


def select_random(movies: list[dict]) -> list[dict] | None:
    n = int(input("How many to select: "))
    if n == 0:
        return None
    if n < 0 or n > len(movies):
        click.echo("Invalid number.")
        return None
    return sample(movies, n)


@click.command()
@click.option('--user', required=True, help='Letterboxd username')
def main(user: str):
    create_tables()
    movies = fetch_or_scrape(user)
    click.echo(f"Watchlist has {len(movies)} movies.")

    selected = select_random(movies)
    if selected is None:
        click.echo("No movies selected.")
        return

    click.echo("\nSelected movies:")
    for movie in selected:
        click.echo(f"  {movie['title']} ({movie['year'] or 'N/A'})")


if __name__ == "__main__":
    main()