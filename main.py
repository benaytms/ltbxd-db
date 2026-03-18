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



def load_cache():
    """
        If the JSON file with all watchlists already exists, load it
        If not, then just starts a new one
    """
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}



def save_cache(cache):
    """
        Saves the cache to the JSON file
    """
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)



def parse_films(USER:str)->list[dict]:
    """ 
        Parse through the given user watchlist and saves all their movies
        into a list
    """
    headers={"User-Agent": "Mozilla/5.0"}
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



def get_movies(USER:str)->list[dict]:
    """
        If the user already has an entry in the JSON file returns
        that user movie watchlist. If not,
        Uses the parse_films function to get the films
    """
    cache=load_cache()
    if USER in cache:
        movies = cache[USER]
    else:
        movies = parse_films(USER)
        cache[USER] = movies
        save_cache(cache)
    return movies



def select_random(movies:list)->list[dict]|None:
    """
        Selects a sample of the user watchlist. Size of sample needs to be specified.
    """
    num_movies=len(movies)
    n = int(input("How many to select: "))
    if n==0:
        return None
    if (not isinstance(n, int)) or n<0 or n>num_movies:
        click.echo("Invalid parameter")
        sys.exit(0)
    return sample(movies, n)



@click.command()
@click.option('--user', default=None, help='Letterboxd Username')
def integrate(user:str)->None:
    """ 
        Parses through USER letterboxd watchlist and select a sample of movies.
    """
    USER=user
    if USER is None:
        click.echo("No value provided\n")
        click.echo('Run "python [script] --help" for more information')
        sys.exit(0)

    movies=get_movies(USER)
    selected_movies=select_random(movies)

    if selected_movies is None:
        click.echo("No movie selected.")
    else:
        print("Selected movies were: \n") 
        for idx in range(len(selected_movies)):
            title,year = (selected_movies[idx]['title'], selected_movies[idx]['year'])
            print(f"{title} - {year}")
            time.sleep(1)


if __name__ == "__main__":
    integrate()
