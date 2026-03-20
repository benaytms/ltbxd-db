import click
import logging
import time
from random import sample
from scrape import parse_films
from db import create_tables, sync_user_watchlist, get_user_movies

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)


def select_random(movies: list[dict], genre: str) -> list[dict] | None:
    n = int(input("How many to select: "))
    if n == 0:
        return None

    if genre != 'all':
        genre_movies=[]
        for m in movies:
            genre_list = m['genres']
            if genre.lower() in genre_list:
                genre_movies.append(m)
        if not movies:
            click.echo(f"No movies found for genre '{genre}'.")
            return None
        if n<0 or n > len(genre_movies):
            click.echo(f"Invalid number, {len(genre_movies)} movies with genre: {genre}")
            return None
        return sample(genre_movies, n)

    if n < 0 or n > len(movies):
        click.echo(f"Invalid number, {len(movies)} movies available.")
        return None

    return sample(movies, n)


@click.command()
@click.option('--user', required=True, help='Letterboxd username')
@click.option('--sync', is_flag=True, default=False, help='Re-scrape and sync newly added movies')
@click.option('--genre', default='all', help='Specifies a genre to sample from')
def main(user: str, sync: bool, genre: str):
    create_tables()
    existing = get_user_movies(user)

    if existing is None:
        click.echo("New user, scraping watchlist...")
        movies = parse_films(user)
        result = sync_user_watchlist(user, movies)
        click.echo(f"{result['added']} movies added.")
    elif sync:
        click.echo(f"Syncing watchlist for '{user}'...")
        movies = parse_films(user)
        result = sync_user_watchlist(user, movies)
        click.echo(f"{result['added']} new movies added.")
    else:
        movies = existing
        click.echo(f"Loaded {len(movies)} movies from database.")

    selected = select_random(movies, genre)
    if selected is None:
        click.echo("No movies selected.")
        return

    click.echo("\nSelected movies:")
    for movie in selected:
        click.echo(f"  {movie['title']} ({movie['year'] or 'N/A'}) — {', '.join(movie.get('genres') or []) or 'N/A'}")
        time.sleep(0.3)


if __name__ == "__main__":
    main()