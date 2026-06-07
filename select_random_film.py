from scrape import parse_films
from integrate import select_random
from films_to_csv import get_user_films_to_csv
import pandas as pd
import os
import time

if __name__ == '__main__':
    user = str(input("Letterboxd Username: "))
    
    if not (os.path.isfile(f'./{user}_films.csv')):
        get_user_films_to_csv(user)
        
    user_films = pd.read_csv(f'./{user}_films.csv').to_dict(orient='records')

    selected = select_random(user_films)
    if not selected:
        exit()

    for i,film in enumerate(selected):
        print(f"\t{film['title']} ({film['year']}) - Genres: {film['genres']}")
        time.sleep(1)