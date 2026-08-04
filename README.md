This was a simple project i made for randomly selecting movies on my Letterboxd watchlist.
I ended up implementing PostgreSQL for storing movies and users as well.

**Made purely for fun and not intended for professional use. I have no idea what i'm doing.**

Requirements:
  1. [uv](https://docs.astral.sh/uv/) (on linux: curl -LsSf https://astral.sh/uv/install.sh | sh)
  2. (optional) postgresql (if you want to experiment with the database)

If you want to run postgresql with Docker, here's a template:
```
docker run -d --name <container_name> -e POSTGRES_USER=<username> -e POSTGRES_PASSWORD=<password> -e POSTGRES_DB=<database_name> -p <port>:5432 postgres:16-trixie
```

***

To get a csv of your letterboxd watchlist:
```
git clone https://github.com/benaytms/ltbxd-db.git
cd ltbxd-db
uv sync
uv run python films_to_csv.py
# the csv file will be saved as './<letterboxd_username>_films.csv'
```

Select random movies from your watchlist:
```
git clone https://github.com/benaytms/ltbxd-db.git
cd ltbxd-db
uv sync
uv run python select_random_film.py
# you can specify a genre to sample from. common examples: action, horror, romance, comedy, war.
```

To test the database:
```
git clone https://github.com/benaytms/ltbxd-db.git
cd ltbxd-db
mv .env.example .env
# Change the values on .env according to your postgresql configuration
uv sync
uv run python integrate.py --user <letterboxd_username>
```

You can also use the additional flags:

```
uv run python integrate.py --help
Usage: integrate.py [OPTIONS]

Options:
  --user TEXT   Letterboxd username  [required]
  --sync        Re-scrape watchlist and sync newly added movies
  --help        Show this message and exit.
```

***

the watchlist data will be stored in the following way:
 ```
  1. genres: id, name
  2. movies: id, user_id, title, release_year
  3. movies_genres: movie_id, genre_id
  4. users: id, username
 ```
