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


def select_random(movies: list[dict], genre: str='all') -> list[dict] | None:
    click.echo(f"Total movies found: {len(movies)}")
    genre = str(input("Select movies with a specific genre (Empty for all): "))
    if (genre == '' or genre is None): genre = 'all'
    if genre != 'all':
        genre_movies=[]
        for m in movies:
            genre_list = m['genres']
            if genre.lower() in genre_list:
                genre_movies.append(m)
        if not movies or len(genre_movies) < 1:
            print(f"No movies found for genre '{genre}'.")
            return None
        
        click.echo(f"{len(genre_movies)} movies found for {genre}")

    while True:
        n = input("How many to select: ").strip()
        try:
            n = int(n)
            if n < 0:
                raise ValueError
        except ValueError:
            logger.error(f"'{n}' not accepted as entry, only positive integers are valid.")
            continue
            
        n = int(n)
        if n == 0:
            return None
        if genre == 'all':
            if n > len(movies):
                click.echo(f"Invalid number, {len(movies)} movies available.")
                continue
            return sample(movies, n)
        else:
            if n > len(genre_movies):
                click.echo(f"Invalid number, {len(genre_movies)} movies with genre: {genre}")
                continue
            return sample(genre_movies, n)


@click.command()
@click.option('--user', required=True, help='Letterboxd username')
@click.option('--sync', is_flag=True, default=False, help='Re-scrape watchlist and sync newly added movies')
def main(user: str, sync: bool):
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

    selected = select_random(movies)
    if selected is None:
        click.echo("No movies selected.")
        return

    click.echo("\nSelected movies:")
    for movie in selected:
        click.echo(f"\t{movie['title']} ({movie['year'] or 'N/A'}) — {', '.join(movie.get('genres') or []) or 'N/A'}")
        time.sleep(1)


if __name__ == "__main__":
    main()
