from main import get_movies
import psycopg2
import logging

def create_tables()->bool:
    """
        If the tables don't exist, creates them
    """
    return True

def check_user_on_table()->bool:
    """
        Checks if user is already on the table
    """
    return True

def add_user_wl_to_table()->bool:
    """
        Add user to users table, and user's watchlist to movies table
        They will be linked through their usernames and id.
        On users: id Primary key
        On tables: user_id (user.id) Foreign Key

        If user already on table, skip adding process - but returns True.
    """
    return True

def fetch_userdata()->list[dict]:
    """
        Fetches user movies to use on select_random on main
    """
    return [{}]



if __name__ == "__main__":
    movies = get_movies('ye4rz3r0')
    print(movies[0])