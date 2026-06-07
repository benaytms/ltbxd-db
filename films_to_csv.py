import pandas as pd
from scrape import parse_films

def get_user_films_to_csv(user: str, csv_name: str) -> None:
    films_list = parse_films(user)

    df = pd.DataFrame(films_list)
    df['year'] = df['year'].fillna(0).astype(int)

    df.to_csv(csv_name, index=False)

    del df
    del films_list

if __name__ == '__main__':
    user = str(input("Letterboxd username: "))
    csv_name = str(input("CSV filepath name: "))
    get_user_films_to_csv(user, csv_name)