from httpx import request
import requests
from bs4 import BeautifulSoup
from random import sample
import time
import click
import sys
import json
import os

CACHE_FILE="db/watchlists.json"

headers={"User-Agent": "Mozilla/5.0"}

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def parse_films(USER:str)->list:
    movies = []
    page = 1
    while True:
        url = f"https://letterboxd.com/{USER}/watchlist/page/{page}/"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            print("Connection error, retrying in 5s...")
            time.sleep(5)
            continue
        except requests.exceptions.HTTPError as e:
            status=e.response.status_code
            if status==403:
                click.echo("This user watchlist is private.")
                sys.exit(1)
            elif status==404:
                click.echo("Page not found, this user does not exist.")
                sys.exit(1)

        soup = BeautifulSoup(response.text, "html.parser")
        posters = soup.find_all("div", {"data-component-class": "LazyPoster"})

        batch_number = len(posters)
        for movie in posters:
            raw = movie["data-item-name"]
            if '(' in raw and raw.endswith(')'): # type: ignore
                name, year = raw.rsplit(" (", 1) # type: ignore
                year = int(year.rstrip(")"))
                movies.append({"title": name, "year": year})
            else:
                movies.append({"title": raw, "year": None})
        if batch_number<28:
            break
        page += 1
        time.sleep(1)
    return movies

def select_random(movies:list, USER:str)->list[dict]:
    num_movies=len(movies)
    n = int(input("How many to select: "))
    if (not isinstance(n, int)) or n<0 or n>num_movies:
        click.echo("Invalid parameter")
        sys.exit(0)
    return sample(movies, n)

@click.command()
@click.option('--user', default=None, help='Letterboxd Username')
def main(user:str)->None:
    """ Parses through USER letterboxd watchlist and select a sample of movies """
    USER=user
    if USER is None:
        click.echo("No value provided\n")
        click.echo('Run "python [script] --help" for more information')
        sys.exit(0)

    cache=load_cache()
    if USER in cache:
        movies = cache[USER]
    else:
        movies = parse_films(USER)
        cache[USER] = movies
        save_cache(cache)

    selected_movies=select_random(movies, USER)
    print("Selected movies were: \n") 
    for idx in range(len(selected_movies)):
        title,year = (selected_movies[idx]['title'], selected_movies[idx]['year'])
        print(f"{title} - {year}")
        time.sleep(1)


if __name__ == "__main__":
    main()
