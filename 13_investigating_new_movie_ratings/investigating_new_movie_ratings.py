import requests
import logging
import csv
import re
import numpy as np
import pandas as pd
import seaborn as sns
import warnings
import matplotlib.pyplot as plt
import ipywidgets as widgets
from datetime import datetime
from bs4 import BeautifulSoup

# Set to CRITICAL (remove +1) and Restart/Run All to show logging details
logging.basicConfig(level=logging.CRITICAL+1)

# Suppress low-level warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Set chart defaults
sns.set_theme(style="whitegrid")
sns.set_palette("muted")
plt.rcParams['font.family'] = 'arial'

#------------------------------------------------------------------------------------#
# Scrape the data
#------------------------------------------------------------------------------------#

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}


# Metacritic: New Releases in Theaters
#------------------------------------------------------------------------------------
# Pull from all three pages
metacritic_url1 = "https://www.metacritic.com/browse/movies/release-date/theaters/date"
metacritic_url2 = "https://www.metacritic.com/browse/movies/release-date/theaters/date?page=1"
metacritic_url3 = "https://www.metacritic.com/browse/movies/release-date/theaters/date?page=2"

metacritic = {}

for url in [metacritic_url1, metacritic_url2, metacritic_url3]:
    response = requests.get(url, headers=headers)
    website_html = response.text

    soup = BeautifulSoup(website_html, "html.parser")

    movie_links = soup.find_all("td", class_="clamp-summary-wrap")
    
    for link in movie_links:
        try:
            metacritic[link.find("h3").get_text().strip().lower().replace("–","-").replace(",","").replace("ii","2")] = float(link.find('div', class_=re.compile(r"metascore_w large movie.*")).get_text())
        except ValueError:
            metacritic[link.find("h3").get_text().strip().lower().replace("–","-").replace(",","").replace("ii","2")] = float(np.nan)
                    
logging.critical(metacritic)
print(len(metacritic))


# IMDb: Feature Film (Sorted by Popularity Ascending)
#------------------------------------------------------------------------------------
imdb_urls = [
    "https://www.imdb.com/search/title/?title_type=feature",
    "https://www.imdb.com/search/title/?title_type=feature&start=51&ref_=adv_nxt",
    "https://www.imdb.com/search/title/?title_type=feature&start=101&ref_=adv_nxt",
    "https://www.imdb.com/search/title/?title_type=feature&start=151&ref_=adv_nxt",
    "https://www.imdb.com/search/title/?title_type=feature&start=201&ref_=adv_nxt",
    "https://www.imdb.com/search/title/?title_type=feature&start=251&ref_=adv_nxt",
    "https://www.imdb.com/search/title/?title_type=feature&start=301&ref_=adv_nxt",
    "https://www.imdb.com/search/title/?title_type=feature&start=351&ref_=adv_nxt",
    "https://www.imdb.com/search/title/?title_type=feature&start=401&ref_=adv_nxt",
    "https://www.imdb.com/search/title/?title_type=feature&start=451&ref_=adv_nxt",
    ]

imdb = {}

for url in imdb_urls:

    response = requests.get(url, headers=headers)
    website_html = response.text

    soup = BeautifulSoup(website_html, "html.parser")
    
    movie_items = soup.find_all("h3", class_="lister-item-header")
    movie_rating_texts = soup.find_all("div", attrs={"name":"ir"})
    
    # Multiply IMDb rating by 10 to convert to 100 pt scale similar to the other websites
    for item, rating in zip(movie_items, movie_rating_texts):
        imdb[item.a.text.strip().lower().replace("–","-").replace(",","").replace("ii","2")] = float(rating.strong.text)*10

logging.critical(imdb)
print(len(imdb))


# Rotten Tomatoes: New Movies in Theaters
#------------------------------------------------------------------------------------
rottentomatoes_url = "https://www.rottentomatoes.com/browse/movies_in_theaters/sort:popular?page=5"

rottentomatoes = {}

response = requests.get(rottentomatoes_url, headers=headers)
website_html = response.text

soup = BeautifulSoup(website_html, "html.parser")

movie_title_texts = soup.find_all("span", attrs={"data-qa":"discovery-media-list-item-title"})

movie_rating_texts = soup.find_all("score-pairs", attrs={"criticsscore": True})
for item, rating in zip(movie_title_texts, movie_rating_texts):
    if rating["criticsscore"]=="":
        rating["criticsscore"] = np.nan
    else:
        rating["criticsscore"] = int(rating["criticsscore"])
    rottentomatoes[item.text.strip().lower().replace("–","-").replace(",","").replace("ii","2")] = rating["criticsscore"]
    
dates = {}
date_format = "%b %d, %Y"
movie_open_dates = soup.find_all("span", attrs={"data-qa":"discovery-media-list-item-start-date"})
for item, date in zip(movie_title_texts, movie_open_dates):
    if date.text.strip().startswith("Opened"):
        date_string = date.text.strip()[len("Opened "):]
    date_datetime = datetime.strptime(date_string, date_format)
    date_formatted = date_datetime.strftime("%Y-%m-%d")
    dates[item.text.strip().lower().replace("–","-").replace(",","").replace("ii","2")] = date_formatted
    
logging.critical(rottentomatoes)
logging.critical(dates)
print(len(rottentomatoes))


# Fandango: From Rotten Tomatoes' Verified Audience Score
#------------------------------------------------------------------------------------
fandango = {}

movie_rating_texts = soup.find_all("score-pairs", attrs={"audiencescore": True})
for item, rating in zip(movie_title_texts, movie_rating_texts):
    if rating["audiencescore"]=="":
        rating["audiencescore"] = np.nan
    else:
        rating["audiencescore"] = int(rating["audiencescore"])
    fandango[item.text.strip().lower().replace("–","-").replace(",","").replace("ii","2")] = rating["audiencescore"]
    
logging.critical(fandango)
print(len(fandango))


#------------------------------------------------------------------------------------#
# Merge or import the data
#------------------------------------------------------------------------------------#
all_movies = set(list(metacritic.keys()) + list(imdb.keys()) + list(rottentomatoes.keys()) + list(fandango.keys()))
all_movie_ratings = {}
for movie in all_movies:
    all_movie_ratings[movie] = [metacritic.get(movie, np.nan), imdb.get(movie, np.nan), rottentomatoes.get(movie, np.nan), fandango.get(movie, np.nan)]

# Comment the following line out and uncomment the last line to follow the results in this project.
filename = "movie_ratings.csv"

# Write data to .csv file (one column per movie site)
default_release_date = np.nan
with open(filename, mode='w', newline='', encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    writer.writerow(["Movie", "Release Date", "Metacritic", "IMDb", "Rotten Tomatoes", "Fandango"])
    for movie, rankings in all_movie_ratings.items():
        # Use pop() method with default value to get the release date for each movie
        release_date = dates.pop(movie, default_release_date)
        writer.writerow([movie, release_date] + rankings)

# In the case of a runtime error, one or more of the movie critic sites restructured their page(s).
# Either 
#   (1) Hard mode: Update the pertaining web scraping code, or
#   (2) Easy mode: Uncomment and use the following data snapshotted on July 30 instead:
# filename = "movie_ratings-07-30-2023.csv"


#------------------------------------------------------------------------------------#
# Clean the data
#------------------------------------------------------------------------------------#

df = pd.read_csv(filename, encoding="UTF-8-sig")

critics = ["Metacritic", "IMDb", "Rotten Tomatoes", "Fandango"]

def chart_theme():
    sns.despine(top=True, bottom=True, left=True, right=True)
    plt.grid(axis="y", alpha=0.3)
    plt.xlabel("")
    plt.ylabel("")
    plt.ylim(20,100)
    plt.tick_params(axis="both", length=0)
    plt.tight_layout()
    
# NaN values
for i in range(5):
    count_four_nan = df[df.isnull().sum(axis=1) == i].shape[0]
    print(f"Number of movies with {i} NaN values:", count_four_nan)

print(f"Total number of new movies: {len(df)}")

df.dropna(subset=critics, how="all", inplace=True)
print(f"Total number of new movies: {len(df)}")

df["nan_count"] = df[critics].isnull().sum(axis=1)

df = df[df["nan_count"] < 3]
print(f"Total number of new movies: {len(df)}")

df['Average Score'] = df[critics].mean(axis=1)

df.head()


#------------------------------------------------------------------------------------#
# Explore the data
#------------------------------------------------------------------------------------#

# Movies with no null ratings
all_ratings = df[df["nan_count"]==0].copy().reset_index(drop=True)
all_ratings.sort_values(by="Average Score", ascending=False)

# Movie ratings by number of critics
def boxplot(num_critics):
    new_df = df[df["nan_count"]==len(critics)-num_critics].copy()
    variable_df = new_df.drop(columns=['Release Date','nan_count', 'Average Score'])
    melted_df = variable_df.melt(id_vars='Movie', var_name='Critic', value_name='Rating')
    plt.figure(figsize=(6, 3))
    sns.boxplot(x='Critic', 
                y='Rating', 
                data=melted_df, 
                palette='muted')
    plt.suptitle("Ratings by Critic for New Movie Releases", fontsize=20, y=0.9)
    plt.ylim(20,100)
    spell_out_numbers = {1: "One", 2: "Two", 3: "Three", 4: "Four"}
    if num_critics==1:
        plt.title(f"{len(new_df)} Movies Rated by One Critic")
    else:
        plt.title(f"{len(new_df)} Movies Rated by {spell_out_numbers[num_critics]} Critics")    
    chart_theme()
    plt.show()
    
    print(f"Number of critics: {num_critics}")
    for critic in critics:
        print(f"{critic}: {round(new_df[critic].notnull().sum()/len(new_df)*100)}%")
        
# If the boxplot doesn't update when using the slider, cut, run, repaste, and rerun this code cell.
critics = ["Metacritic", "IMDb", "Rotten Tomatoes", "Fandango"]
num_critics_slider = widgets.IntSlider(
                                    value=4, min=2, max=4, 
                                    description="Number of Critics (2-4)", 
                                    style={"description_width":"initial"},
                                    continuous_update=False,
                                    layout=widgets.Layout(width="35%")
                                    )

widgets.interactive(boxplot, num_critics=num_critics_slider)

# Movie ratings by month
all_ratings.sort_values(by='Release Date', inplace=True)

plt.figure(figsize=(8, 4))
for critic in critics:
    plt.scatter(all_ratings['Release Date'], all_ratings[critic], label=critic)
plt.title("Scores by Movie Critic for New Movie Releases", fontsize=20)
plt.xlabel("Release Date", fontsize=12)
plt.ylabel("Scores", fontsize=12)
plt.xticks(rotation=45, ha="right", fontsize=10)
plt.legend()
chart_theme()
plt.show()

# Top 5 newly released movie ratings
top_five = all_ratings.sort_values(by="Average Score", ascending=False).head()
top_five

fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(10, 7), sharex=True)

for i, (index, row) in enumerate(top_five.iterrows()):
    row_idx = i // 2
    col_idx = i % 2
    movie_name = row['Movie']
    ratings = row[['Metacritic', 'IMDb', 'Rotten Tomatoes', 'Fandango', 'Average Score']]
    scores = ratings.index.tolist()
    
    axes[row_idx, col_idx].bar(scores, ratings, alpha=0.9)
    axes[row_idx, col_idx].set_title(f"{movie_name.title()}", fontsize=14)
    if col_idx == 0:
        axes[row_idx, col_idx].set_ylim(0,100)
    else:
        axes[row_idx, col_idx].set_yticklabels([])

for i in range(len(top_five), 3*2):
    row_idx = i // 2
    col_idx = i % 2
    fig.delaxes(axes[row_idx, col_idx])
    
plt.xticks(rotation=45)
chart_theme()
plt.show()

# Bottom 5 newly released movie ratings
bottom_five = all_ratings.sort_values(by="Average Score", ascending=True).head()
bottom_five

fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(10, 7), sharex=True)

for i, (index, row) in enumerate(bottom_five.iterrows()):
    row_idx = i // 2
    col_idx = i % 2
    movie_name = row['Movie']
    ratings = row[['Metacritic', 'IMDb', 'Rotten Tomatoes', 'Fandango', 'Average Score']]
    scores = ratings.index.tolist()
    
    axes[row_idx, col_idx].bar(scores, ratings, alpha=0.9)
    axes[row_idx, col_idx].set_title(f"{movie_name.title()}", fontsize=14)
    if col_idx == 0:
        axes[row_idx, col_idx].set_ylim(0,100)
    else:
        axes[row_idx, col_idx].set_yticklabels([])

for i in range(len(bottom_five), 3*2):
    row_idx = i // 2
    col_idx = i % 2
    fig.delaxes(axes[row_idx, col_idx])
    
plt.xticks(rotation=45)
chart_theme()
plt.show()

# Average ratings by movie critic
average_scores = all_ratings[['Metacritic', 'IMDb', 'Rotten Tomatoes', 'Fandango', 'Average Score']].mean()
print(round(average_scores.sort_values(ascending=False)))

plt.figure(figsize=(7, 4))
average_scores.plot(kind='bar', alpha=0.9)

plt.title("Average Score for Each Movie Critic Site", fontsize=20)
plt.xticks(rotation=0)
plt.ylim(0, 100) 
chart_theme()
plt.show()

# Histogram of average ratings for new releases rated by all 4 movie critics
plt.figure(figsize=(8, 4))
bins = range(0, 101, 10)
plt.hist(all_ratings['Average Score'], bins=bins, alpha=0.7)
plt.suptitle("Histogram of Average Ratings", fontsize=20, y=.93)
plt.title(f"For {len(all_ratings)} New Releases Rated by All 4 Movie Critics")
plt.xticks(bins)
chart_theme()
plt.ylim(0,10)
plt.show()

# Histogram of average ratings for all new releases
plt.figure(figsize=(8, 4))
bins = range(0, 101, 10)
plt.hist(df['Average Score'], bins=bins, alpha=0.7)
plt.suptitle("Histogram of Average Ratings", fontsize=20, y=.93)
plt.title(f"For {len(df)} New Movie Releases in Theaters")
plt.xticks(bins)
chart_theme()
plt.ylim(0,40)
plt.show()
