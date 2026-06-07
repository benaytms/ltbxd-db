import pandas as pd
from scrape import parse_films

def get_user_films_to_csv(user: str) -> None:
    print("Fetching watchlist...")
    films_list = parse_films(user)

    df = pd.DataFrame(films_list)
    df['year'] = df['year'].fillna(0).astype(int)

    csv_name = './' + user + '_films.csv'

    df.to_csv(csv_name, index=False)

    del df
    del films_list

if __name__ == '__main__':
    user = str(input("Letterboxd username: "))
    get_user_films_to_csv(user)
