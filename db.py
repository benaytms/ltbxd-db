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
                conn.commit()
                logger.info("Tables ready.")
                return True
    except Exception as e:
        logger.error(f"Could not create tables: {e}")
        return False


def user_exists(cursor, username: str) -> bool:
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    return cursor.fetchone() is not None


def add_user_watchlist(username: str, movies: list[dict]) -> bool:
    """
    Insert user + their watchlist into the DB.
    If user already exists, skip entirely and return True.
    """
    try:
        with psycopg2.connect(DB_URL) as conn:
            with conn.cursor() as cursor:
                if user_exists(cursor, username):
                    logger.info(f"User '{username}' already in DB, skipping.")
                    return True

                cursor.execute(
                    "INSERT INTO users (username) VALUES (%s) RETURNING id",
                    (username,)
                )
                user_id = cursor.fetchone()[0] # type: ignore

                for movie in movies:
                    cursor.execute(
                        "INSERT INTO movies (user_id, title, release_year) VALUES (%s, %s, %s)",
                        (user_id, movie["title"], movie.get("year"))
                    )

                conn.commit()
                logger.info(f"Added {len(movies)} movies for user '{username}'.")
                return True
    except Exception as e:
        logger.error(f"DB insert failed: {e}")
        return False


def get_user_movies(username: str) -> list[dict] | None:
    """
    Fetch a user's watchlist from DB.
    Returns None if user doesn't exist yet.
    """
    try:
        with psycopg2.connect(DB_URL) as conn:
            with conn.cursor() as cursor:
                if not user_exists(cursor, username):
                    return None
                cursor.execute("""
                    SELECT m.title, m.release_year
                    FROM movies m
                    JOIN users u ON m.user_id = u.id
                    WHERE u.username = %s
                """, (username,))
                rows = cursor.fetchall()
                return [{"title": r[0], "year": r[1]} for r in rows]
    except Exception as e:
        logger.error(f"DB fetch failed: {e}")
        return None
    
    

def sync_user_watchlist(username: str, scraped_movies: list[dict]) -> dict:
    """
    For existing users: diff scraped watchlist against DB, insert new entries.
    For new users: insert everything.
    Returns a summary {"added": int, "already_had": int}.
    """
    try:
        with psycopg2.connect(DB_URL) as conn:
            with conn.cursor() as cursor:
                # get or create user
                cursor.execute(
                    "SELECT id FROM users WHERE username = %s", (username,)
                )
                row = cursor.fetchone()

                if row:
                    user_id = row[0]
                    # fetch what's already stored as a set of (title, year) tuples
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

                # diff: only insert movies not already in DB
                new_movies = [
                    m for m in scraped_movies
                    if (m["title"], m.get("year")) not in existing
                ]

                for movie in new_movies:
                    cursor.execute(
                        "INSERT INTO movies (user_id, title, release_year) VALUES (%s, %s, %s)",
                        (user_id, movie["title"], movie.get("year"))
                    )

                conn.commit()
                return {"added": len(new_movies), "already_had": len(existing)}

    except Exception as e:
        logger.error(f"DB sync failed: {e}")
        return {"added": 0, "already_had": 0}