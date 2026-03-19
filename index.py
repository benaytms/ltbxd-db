from main import get_movies
from dotenv import load_dotenv
import psycopg2
import logging
import os

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s %(message)s'
)

logger = logging.getLogger(__name__)

DB_URL=str(os.getenv("DATABASE_URL"))
ALLOWED_TABLES = ("users", "movies")

def create_tables()->bool:
    """
        If the tables don't exist, creates them
    """
    try:
        with psycopg2.connect(DB_URL) as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(
                        f'''
                        CREATE TABLE IF NOT EXISTS {ALLOWED_TABLES[0]}
                        (
                            id SERIAL PRIMARY KEY,
                            username TEXT NOT NULL UNIQUE,
                        );
                        '''
                        )
                    cursor.execute(
                        f'''
                        CREATE TABLE IF NOT EXISTS {ALLOWED_TABLES[1]} 
                        (
                            id SERIAL PRIMARY KEY,
                            user_id INT NOT NULL,
                            title TEXT,
                            release_year INT,
                            FOREIGN KEY (user_id) REFERENCES {ALLOWED_TABLES[0]}(id)
                        );
                        '''
                    )
                    conn.commit()
                    return True
                except Exception as e:
                    logger.warning("At least one of the tables could not be created. Status: {e}")
                    return False
    except Exception as e:
        logger.error(f"Connection could not be established to database. Status: {e}")
        return False
    

#def check_user_on_table(username:str)->bool:
    """
        Checks if user is already on the table
    """
#    return True


def add_user_wl_to_table(user_data:dict)->bool:
    """
        Add user to users table, and user's watchlist to movies table
        They will be linked through their usernames and id.
        On users: id Primary key
        On tables: user_id (user.id) Foreign Key

        If user already on table, skip adding process - but returns True.
    """
    try:
        with psycopg2.connect(DB_URL) as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(
                        f"SELECT 1 FROM {ALLOWED_TABLES[0]} WHERE username = %s", (username,)
                    )
                    if not cursor.fetchone():
                        cursor.execute(f'''
                            INSERT INTO {ALLOWED_TABLES[0]}
                                (title, date, explanation, url, copyright, media_type)
                            VALUES
                                (%s, %s)
                            ''',
                            (,)
                        )
                        logger.info(f"Image '{}' added to database.")
                        return True
                    else:
                        logger.info("Today's image already in database, skipping.")
                        return False
                except Exception as e:
                    logger.warning(f"")
    except Exception as e:
        logger.error(f"Connection could not be established to database. Status: {e}")
        return False

def fetch_userdata()->list[dict]:
    """
        Fetches user movies to use on select_random on main
    """
    return [{}]



if __name__ == "__main__":
    movies = get_movies('ye4rz3r0')
    print(movies[0])