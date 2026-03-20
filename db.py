import psycopg2
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

DB_URL = str(os.getenv("DATABASE_URL"))


def create_tables() -> bool:
    try:
        with psycopg2.connect(DB_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username TEXT NOT NULL UNIQUE
                    );
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS movies (
                        id SERIAL PRIMARY KEY,
                        user_id INT NOT NULL REFERENCES users(id),
                        title TEXT NOT NULL,
                        release_year INT
                    );
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS genres (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL UNIQUE
                    );
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS movies_genres (
                        movie_id INT REFERENCES movies(id),
                        genre_id INT REFERENCES genres(id),
                        PRIMARY KEY (movie_id, genre_id)
                    );
                """)
                conn.commit()
                logger.info("Tables ready.")
                return True
    except Exception as e:
        logger.error(f"Could not create tables: {e}")
        return False


def user_exists(cursor, username: str) -> bool:
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    return cursor.fetchone() is not None


def get_or_create_genre(cursor, genre_name: str) -> int:
    cursor.execute(
        "INSERT INTO genres (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
        (genre_name,)
    )
    cursor.execute("SELECT id FROM genres WHERE name = %s", (genre_name,))
    return cursor.fetchone()[0]


def insert_movie_with_genres(cursor, user_id: int, movie: dict) -> None:
    cursor.execute(
        "INSERT INTO movies (user_id, title, release_year) VALUES (%s, %s, %s) RETURNING id",
        (user_id, movie["title"], movie.get("year"))
    )
    movie_id = cursor.fetchone()[0]

    for genre_name in movie.get("genres") or []:
        genre_id = get_or_create_genre(cursor, genre_name)
        cursor.execute(
            "INSERT INTO movies_genres (movie_id, genre_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (movie_id, genre_id)
        )


def get_user_movies(username: str) -> list[dict] | None:
    try:
        with psycopg2.connect(DB_URL) as conn:
            with conn.cursor() as cursor:
                if not user_exists(cursor, username):
                    return None
                cursor.execute("""
                    SELECT m.title, m.release_year, ARRAY_AGG(g.name) AS genres
                    FROM movies m
                    JOIN users u ON m.user_id = u.id
                    LEFT JOIN movies_genres mg ON m.id = mg.movie_id
                    LEFT JOIN genres g ON mg.genre_id = g.id
                    WHERE u.username = %s
                    GROUP BY m.id, m.title, m.release_year
                """, (username,))
                rows = cursor.fetchall()
                return [
                    {"title": r[0], "year": r[1], "genres": [g for g in r[2] if g is not None]}
                    for r in rows
                ]
    except Exception as e:
        logger.error(f"DB fetch failed: {e}")
        return None


def sync_user_watchlist(username: str, scraped_movies: list[dict]) -> dict:
    try:
        with psycopg2.connect(DB_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM users WHERE username = %s", (username,)
                )
                row = cursor.fetchone()

                if row:
                    user_id = row[0]
                    cursor.execute(
                        "SELECT title, release_year FROM movies WHERE user_id = %s",
                        (user_id,)
                    )
                    existing = {(r[0], r[1]) for r in cursor.fetchall()}
                else:
                    cursor.execute(
                        "INSERT INTO users (username) VALUES (%s) RETURNING id",
                        (username,)
                    )
                    user_id = cursor.fetchone()[0] # type: ignore
                    existing = set()

                new_movies = [
                    m for m in scraped_movies
                    if (m["title"], m.get("year")) not in existing
                ]

                for movie in new_movies:
                    insert_movie_with_genres(cursor, user_id, movie)

                conn.commit()
                return {"added": len(new_movies), "already_had": len(existing)}

    except Exception as e:
        logger.error(f"DB sync failed: {e}")
        return {"added": 0, "already_had": 0}