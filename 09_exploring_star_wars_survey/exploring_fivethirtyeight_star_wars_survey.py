import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# %matplotlib inline
warnings.filterwarnings("ignore")

# Import the data
star_wars = pd.read_csv("star_wars.csv", encoding="ISO-8859-1")

print(star_wars.shape)

# Check for duplicates
star_wars_copy = star_wars.drop_duplicates(subset=["RespondentID"])
print(star_wars_copy.shape)
print(star_wars.head(10))

# Original column names
print(star_wars.columns)

# Rename column headers
star_wars = star_wars.rename(columns={
    "Have you seen any of the 6 films in the Star Wars franchise?":"Have you seen at least one Star Wars film?",
    "Do you consider yourself to be a fan of the Star Wars film franchise?":"Are you a Star Wars fan?",
    "Which of the following Star Wars films have you seen? Please select all that apply.":"Watched Ep 1",
    "Unnamed: 4":"Watched Ep 2",
    "Unnamed: 5":"Watched Ep 3",
    "Unnamed: 6":"Watched Ep 4",
    "Unnamed: 7":"Watched Ep 5",
    "Unnamed: 8":"Watched Ep 6",
    "Please rank the Star Wars films in order of preference with 1 being your favorite film in the franchise and 6 being your least favorite film.":"Ranked Ep 1",
    "Unnamed: 10":"Ranked Ep 2",
    "Unnamed: 11":"Ranked Ep 3",
    "Unnamed: 12":"Ranked Ep 4",
    "Unnamed: 13":"Ranked Ep 5",
    "Unnamed: 14":"Ranked Ep 6",
    "Please state whether you view the following characters favorably, unfavorably, or are unfamiliar with him/her.": "Han Solo",
    "Unnamed: 16":"Luke Skywalker",
    "Unnamed: 17":"Princess Leia Organa",
    "Unnamed: 18":"Anakin Skywalker",
    "Unnamed: 19":"Obi Wan Kenobi",
    "Unnamed: 20":"Emperor Palpatine",
    "Unnamed: 21":"Darth Vader",
    "Unnamed: 22":"Lando Calrissian",
    "Unnamed: 23":"Boba Fett",
    "Unnamed: 24":"C-3P0",
    "Unnamed: 25":"R2-D2",
    "Unnamed: 26":"Jar Jar Binks",
    "Unnamed: 27":"Padme Amidala",
    "Unnamed: 28":"Yoda",
    "Do you consider yourself to be a fan of the Expanded Universe?":"Are you an Expanded Universe fan?",
    "Do you consider yourself to be a fan of the Star Trek franchise?":"Are you a Star Trek fan?"
})

# Cleaned column names
print(star_wars.columns)

# Convert values to appropriate data types
star_wars.info(verbose=True)

# Clean and map Yes/No columns
for column in star_wars.columns:
    print(star_wars[column].unique())
    
bool_yes_no = {
    "Yes": True,
    "No": False,
    np.NaN: False,
}

for column in [
    'Have you seen at least one Star Wars film?',
    'Are you a Star Wars fan?',
    'Are you familiar with the Expanded Universe?',
    'Are you an Expanded Universe fan?', 
    'Are you a Star Trek fan?'
]:
    star_wars[column] = star_wars[column].map(bool_yes_no)
    
print(star_wars.iloc[:,1].value_counts())

# Clean and map columns for watched movies
bool_watched_movie = {
    'Star Wars: Episode I  The Phantom Menace': True,
    'Star Wars: Episode II  Attack of the Clones': True,
    'Star Wars: Episode III  Revenge of the Sith': True,
    'Star Wars: Episode IV  A New Hope': True,
    'Star Wars: Episode V The Empire Strikes Back': True,
    'Star Wars: Episode VI Return of the Jedi': True,
    np.NaN: False
}

for column in star_wars.columns[3:9]:
    star_wars[column] = star_wars[column].map(bool_watched_movie)
    
print(star_wars.iloc[:,3].value_counts())

print(star_wars.iloc[:,8].value_counts())

# Clean and map columns for character favorability
bool_chars = {
    "Very favorably":1,
    "Somewhat favorably":2,
    "Neither favorably nor unfavorably (neutral)":3,
    "Somewhat unfavorably":4,
    "Very unfavorably":5,
    "Unfamiliar (N/A)":6,
    np.NaN: 6
}

for column in star_wars.columns[15:29]:
    star_wars[column] = star_wars[column].map(bool_chars)
    
# Check order of Age values
star_wars["Age"].value_counts().sort_index()

seen_star_wars = star_wars[star_wars["Have you seen at least one Star Wars film?"] == True]
print(len(seen_star_wars))

not_seen_star_wars = star_wars[star_wars["Have you seen at least one Star Wars film?"] == False]
print(len(not_seen_star_wars))

print(seen_star_wars.head(10))

false_positives = []

for i in range(len(star_wars)):
    count = 0
    row = star_wars.iloc[i]
    for column in range(3, 9):
        if row[column] == False and row[1] == True:
            count += 1
            
    if count == 6:
        false_positives.append(i)
        star_wars.iloc[i,1] = False
        
print(false_positives)
seen_star_wars = seen_star_wars.drop(index=false_positives)
print(len(false_positives))
print(len(seen_star_wars))

star_wars["Have you seen at least one Star Wars film?"].value_counts()

# Create functions to generate Most Viewed and Highest Ranked plots
# Generic and emphasized bar colors
li = "#d5bbff" # light purple
da = "#6017d9" # dark purple

# Function to generate Most Viewed plot
def most_viewed(population, colors):
    """Generates plot showing most viewed movies in ascending order by episode.
    
    Args:
    - population (function): name of the data set or subset
    - colors (list): list of six strings either 'li' or 'da' to denote light or dark colors for each bar
    """
    percents_seen = []
    for i in range(1,7):
        percent_seen = population[f"Watched Ep {i}"].sum() / len(population) * 100
        percents_seen.append(percent_seen)

    movies = [
        "I - The Phantom Menace",
        "II - Attack of the Clones",
        "III - Revenge of the Sith",
        "IV - A New Hope",
        "V - The Empire Strikes Back",
        "VI - Return of the Jedi"
    ]

    spines = ["bottom", "top", "left", "right"]

    print(percents_seen)
    print(movies)

    fig, ax = plt.subplots(figsize = (5, 2), facecolor="#ffffff")
    bars = ax.barh(movies, percents_seen, height = 0.8, color = colors)
    plt.gca().invert_yaxis()
    ax.tick_params(left=False, bottom=False)
    plt.yticks(fontname="Arial", fontsize=11)
    ax.bar_label(container=bars, fmt="{:.0f}%", padding=5, fontname="Courier New", fontsize=11)
    ax.set_xticks([])
    ax.set_facecolor("#ffffff")

    for spine in spines:
        ax.spines[spine].set_visible(False)
        
    plt.suptitle("Most Viewed Star Wars Films", x=0.0, y=1.22, fontname="Arial", fontsize=16, fontweight="bold")
    
# Function to generate Highest Rated plot
def highest_rated(population, colors):
    """Generates plot showing highest rated movies in ascending order by episode.
    
    Args:
    - population (function): name of the data set or subset
    - colors (list): list of six strings either 'li' or 'da' to denote light or dark colors for each bar
    """
    
    highest_rated = population[population.columns[9:15]].mean()
    movies = [
    "I - The Phantom Menace",
    "II - Attack of the Clones",
    "III - Revenge of the Sith",
    "IV - A New Hope",
    "V - The Empire Strikes Back",
    "VI - Return of the Jedi"
    ]

    spines = ["bottom", "top", "left", "right"]

    fig, ax = plt.subplots(figsize = (5, 2), facecolor="#ffffff")
    bars = ax.barh(movies, highest_rated, height = 0.8, color = colors)
    plt.gca().invert_yaxis()
    ax.tick_params(left=False, bottom=False)
    plt.yticks(fontname="Arial", fontsize=11)
    ax.bar_label(container=bars, fmt="{:.2f}", padding=5, fontname="Courier New", fontsize=11)
    ax.set_xticks([])
    ax.set_facecolor("#ffffff")
    plt.suptitle("Average Rating of Star Wars Films", x=0.09, y=1.22, fontname="Arial", fontsize=16, fontweight="bold")

    for spine in spines:
        ax.spines[spine].set_visible(False)
        
# Find the most viewed movies

star_wars["Have you seen at least one Star Wars film?"].value_counts(normalize=True)
    
most_viewed(seen_star_wars, [li,li,li,li,da,li])
plt.title(f"Of {len(seen_star_wars)} respondents who watched at least one Star Wars film", x=0.06, y=1.12, fontname="Arial", fontsize=13)

# Find the highest ranked movies

highest_rated(seen_star_wars, [li,li,li,li,da,li])
plt.title(f"Of {len(seen_star_wars)} respondents who watched at least one Star Wars film", x=0.11, y=1.12, fontname="Arial", fontsize=13)

seen_all_movies = star_wars

for i in range(len(star_wars)):
    count = 0
    row = star_wars.iloc[i]
    for column in range(3, 9):
        if row[column] == True and row[1] == True:
            count += 1
            
    if count != 6:
        seen_all_movies = seen_all_movies.drop(index=i)

print(len(seen_all_movies))
print(len(seen_all_movies)/len(star_wars))

most_viewed(seen_all_movies, [li,li,li,li,li,li])
plt.title(f"Of {len(seen_all_movies)} Star Wars fans who watched all six Star Wars films", x=0.04, y=1.12, fontname="Arial", fontsize=13)

highest_rated(seen_all_movies, [li,li,li,li,da,li])
plt.title(f"Of {len(seen_all_movies)} respondents who watched all six Star Wars films", x=0.07, y=1.12, fontname="Arial", fontsize=13)

# Star Wars fans

len(not_seen_star_wars[not_seen_star_wars["Are you a Star Wars fan?"]==True])

star_wars_fans = seen_star_wars[seen_star_wars["Are you a Star Wars fan?"]==True]

print(f"Number of respondents who have seen at least one Star Wars film: {len(seen_star_wars)}")
print(f"Number of watchers who identify as Star Wars fan: {len(star_wars_fans)}")
print(f"{round(len(star_wars_fans)/len(seen_star_wars)*100)}% of those who watched at least one Star Wars movie identified themselves as a Star Wars fan.")
print(f"{round(len(star_wars_fans)/len(star_wars)*100)}% of respondents are Star Wars fans.")

most_viewed(star_wars_fans, [li,li,li,li,da,da])
plt.title(f"Of {len(star_wars_fans)} Star Wars fans who watched at least one Star Wars film", x=0.09, y=1.12, fontname="Arial", fontsize=13)

highest_rated(star_wars_fans, [li,li,li,li,da,li])
plt.title(f"Of {len(star_wars_fans)} Star Wars fans who watched at least one Star Wars film", x=0.28, y=1.12, fontname="Arial", fontsize=13)

# True Star Wars fans

true_star_wars_fans = seen_all_movies[seen_all_movies["Are you a Star Wars fan?"]==True]

print(f"Number of respondents who have seen all six films: {len(seen_all_movies)}")
print(f"Number of all six movie watchers who identify as Star Wars fan: {len(true_star_wars_fans)}")
print(f"{round(len(true_star_wars_fans)/len(seen_all_movies)*100)}% of those who watched all six movies classified themselves as a Star Wars fan.")
print(f"{round(len(seen_all_movies)/len(star_wars)*100)}% of respondents have watched all six movies.")
print(f"{round(len(true_star_wars_fans)/len(star_wars)*100)}% of respondents have watched all six movies and identified themselves as Star Wars fans.")

most_viewed(true_star_wars_fans, [li,li,li,da,li,li])
plt.title(f"Of {len(true_star_wars_fans)} Star Wars fans who watched all six Star Wars films", x=0.04, y=1.12, fontname="Arial", fontsize=13)

highest_rated(true_star_wars_fans, [li,li,li,li,da,li])
plt.title(f"Of {len(true_star_wars_fans)} Star Wars fans who watched all six Star Wars films", x=0.08, y=1.12, fontname="Arial", fontsize=13)

# Star Trek fans

star_trek_fans = seen_star_wars[seen_star_wars["Are you a Star Trek fan?"]==True]

print(f"Number of respondents who identify as Star Trek fan: {len(star_trek_fans)}")

print(f"\nNumber of respondents who have seen at least one Star Wars film: {len(seen_star_wars)}")
print(f"{round(len(star_trek_fans)/len(seen_star_wars)*100)}% of those who have seen a Star Wars film identify as a Star Trek fan.")

print(f"\nNumber of respondents who have seen all six Star Wars films: {len(seen_all_movies)}")
print(f"{round(len(star_trek_fans)/len(seen_all_movies)*100)}% of those who have seen all six Star Wars films identify as a Star Trek fan.")
print(f"{round(len(star_trek_fans)/len(star_wars)*100)}% of respondents identified themselves as Star Trek fans.")

most_viewed(star_trek_fans, [li,li,li,li,da,li])
plt.title(f"Of {len(star_trek_fans)} Star Trek fans who watched at least one Star Wars film", x=0.08, y=1.12, fontname="Arial", fontsize=13)

highest_rated(star_trek_fans, [li,li,li,li,da,li])
plt.title(f"Of {len(star_trek_fans)} Star Trek fans who watched at least one Star Wars film", x=0.12, y=1.12, fontname="Arial", fontsize=13)

# Gender

star_wars["Gender"].value_counts(normalize=True)
seen_star_wars["Gender"].value_counts(normalize=True)
not_seen_star_wars["Gender"].value_counts(normalize=True)
star_wars["Gender"][star_wars["Are you a Star Wars fan?"]==True].value_counts(normalize=True)
star_wars["Gender"][star_wars["Are you a Star Trek fan?"]==True].value_counts(normalize=True)
seen_all_movies["Gender"][seen_all_movies["Are you a Star Wars fan?"]==True].value_counts(normalize=True)
seen_all_movies["Gender"][(seen_all_movies["Are you a Star Wars fan?"]==True) & (seen_all_movies["Are you a Star Trek fan?"]==True)].value_counts(normalize=True)

females = seen_star_wars[seen_star_wars["Gender"]=="Female"]
female_star_wars_fans = seen_star_wars[(seen_star_wars["Gender"]=="Female") & (seen_star_wars["Are you a Star Wars fan?"]==True)]
female_true_star_wars_fans = seen_all_movies[(seen_all_movies["Gender"]=="Female") & (seen_all_movies["Are you a Star Wars fan?"]==True)]

males = seen_star_wars[seen_star_wars["Gender"]=="Male"]
male_star_wars_fans = seen_star_wars[(seen_star_wars["Gender"]=="Male") & (seen_star_wars["Are you a Star Wars fan?"]==True)]
male_true_star_wars_fans = seen_all_movies[(seen_all_movies["Gender"]=="Male") & (seen_all_movies["Are you a Star Wars fan?"]==True)]

populations = [females, female_star_wars_fans, female_true_star_wars_fans, males, male_star_wars_fans, male_true_star_wars_fans]

# Gender: Most Viewed Movies

percents_seen = {}
for i, pop in enumerate(populations):
    values = []
    for j in range(1,7):
        percent_seen = pop[f"Watched Ep {j}"].sum() / len(pop)
        values.append(percent_seen)

    percents_seen[i] = values

pop_1_values = percents_seen[0]
pop_2_values = percents_seen[1]
pop_3_values = percents_seen[2]
pop_4_values = percents_seen[3]
pop_5_values = percents_seen[4]
pop_6_values = percents_seen[5]

bar_positions = range(1,7)
bar_width = 0.13

fig, ax = plt.subplots(figsize = (10, 3), facecolor="#ffffff")
ax.bar(bar_positions, pop_1_values, width=bar_width, label='Female', color="#ffdab5")
ax.bar([p + bar_width for p in bar_positions], pop_2_values, width=bar_width, label='Female Star Wars Fans', color="#ff9c3b")
ax.bar([p + bar_width * 2 for p in bar_positions], pop_3_values, width=bar_width, label='Female True Star Wars Fans', color="#ff7e00")
ax.bar([p + bar_width * 3 for p in bar_positions], pop_4_values, width=bar_width, label='Male', color="#c2d2ff")
ax.bar([p + bar_width * 4 for p in bar_positions], pop_5_values, width=bar_width, label='Male Star Wars Fans', color="#6d8eff")
ax.bar([p + bar_width * 5 for p in bar_positions], pop_6_values, width=bar_width, label='Male True Star Wars Fans', color="#0042ff")

plt.yticks(fontsize=10)
plt.ylim([0,1])
ax.yaxis.set_major_formatter(FuncFormatter('{0:.0%}'.format))

ax.set_xticks([])
plt.xticks([p + bar_width * 2.5 for p in bar_positions], range(1,7), fontname="Arial", fontsize=14)

plt.title('Most Viewed Star Wars films', y=1.1, fontname="Arial", fontsize=16, fontweight="bold")

legend=plt.legend(loc="upper right", bbox_to_anchor=(1.3,1.1))
plt.setp(legend.texts, family='Arial')

plt.grid(axis="y", linewidth=0.2)
                  
spines = ["bottom", "top", "left", "right"]
for spine in spines:
    ax.spines[spine].set_visible(False)
ax.tick_params(left=False, bottom=False)

plt.show()

# Gender: Highest Rated Movies

average_ratings = {}
for i, pop in enumerate(populations):
    average_rating = pop[pop.columns[9:15]].mean()
    average_ratings[i] = average_rating

pop_1_values = average_ratings[0]
pop_2_values = average_ratings[1]
pop_3_values = average_ratings[2]
pop_4_values = average_ratings[3]
pop_5_values = average_ratings[4]
pop_6_values = average_ratings[5]

bar_positions = range(1,7)
bar_width = 0.13

fig, ax = plt.subplots(figsize = (10, 3), facecolor="#ffffff")
ax.bar(bar_positions, pop_1_values, width=bar_width, label='Female', color="#ffdab5")
ax.bar([p + bar_width for p in bar_positions], pop_2_values, width=bar_width, label='Female Star Wars Fans', color="#ff9c3b")
ax.bar([p + bar_width * 2 for p in bar_positions], pop_3_values, width=bar_width, label='Female True Star Wars Fans', color="#ff7e00")
ax.bar([p + bar_width * 3 for p in bar_positions], pop_4_values, width=bar_width, label='Male', color="#c2d2ff")
ax.bar([p + bar_width * 4 for p in bar_positions], pop_5_values, width=bar_width, label='Male Star Wars Fans', color="#6d8eff")
ax.bar([p + bar_width * 5 for p in bar_positions], pop_6_values, width=bar_width, label='Male True Star Wars Fans', color="#0042ff")

plt.yticks(fontsize=10)
plt.ylim([0,5])

ax.set_xticks([])
plt.xticks([p + bar_width * 2.5 for p in bar_positions], range(1,7), fontname="Arial", fontsize=14)

plt.title('Highest Rated Star Wars films', y=1.1, fontname="Arial", fontsize=16, fontweight="bold")

legend=plt.legend(loc="upper right", bbox_to_anchor=(1.32,1.1))
plt.setp(legend.texts, family='Arial')

plt.grid(axis="y", linewidth=0.2)

spines = ["bottom", "top", "left", "right"]
for spine in spines:
    ax.spines[spine].set_visible(False)
ax.tick_params(left=False, bottom=False)

plt.show()

# Education

star_wars["Education"].value_counts(normalize=True)
not_seen_star_wars["Education"].value_counts(normalize=True)
seen_star_wars["Education"].value_counts(normalize=True)
seen_all_movies["Education"].value_counts(normalize=True)
star_wars_fans["Education"].value_counts(normalize=True)
true_star_wars_fans["Education"].value_counts(normalize=True)
seen_all_movies["Education"][(seen_all_movies["Are you a Star Wars fan?"]==True) & (seen_all_movies["Are you a Star Trek fan?"]==True)].value_counts()

# Region

star_wars["Location (Census Region)"].value_counts(normalize=True)
not_seen_star_wars["Location (Census Region)"].value_counts(normalize=True).head(3)
seen_star_wars["Location (Census Region)"].value_counts(normalize=True).head(3)
seen_all_movies["Location (Census Region)"].value_counts(normalize=True).head(3)
star_wars_fans["Location (Census Region)"].value_counts(normalize=True).head(3)
true_star_wars_fans["Location (Census Region)"].value_counts(normalize=True).head(3)

# Create a function to plot individual age distributions
li = "#fac06e" # yellow
da = "#2a4858" # dark blue

def age_distribution(population, colors):
    """Generates plot showing age distribution for a population in ascending order by age group.
    
    Args:
    - population (function): name of the data set or subset
    - colors (list): list of two strings either 'li' or 'da' to denote light or dark colors for each bar
    """

    age_ranges = population.index
    percent_age = population.values

    fig, ax = plt.subplots(figsize = (4, 2), facecolor="#ffffff")
    bars = ax.bar(age_ranges, percent_age, color = colors)
    ax.tick_params(left=False, bottom=False)
    plt.yticks(fontname="Arial", fontsize=11)
    ax.bar_label(container=bars, fmt="{:.2f}%", padding=5, fontname="Courier New", fontsize=11)
    ax.set_yticks([])
    ax.set_facecolor("#ffffff")
    plt.xticks(rotation=0, fontsize=11)

    spines = ["bottom", "top", "left", "right"]
    for spine in spines:
        ax.spines[spine].set_visible(False)
        
# Respondents by age who submitted a survey

ages_submit_survey = star_wars["Age"].value_counts(normalize=True).sort_index()*100
age_distribution(ages_submit_survey, [li,li,da,li])
plt.title("Respondents by Age", y = 1.2, fontname="Arial", fontsize=16, fontweight="bold")

# Respondents by age who have not seen a Star Wars movie

ages_not_seen = not_seen_star_wars["Age"].value_counts(normalize=True).sort_index()*100
age_distribution(ages_not_seen, [li,li,li,da])
plt.title("Respondents who haven't seen Star Wars", y = 1.2, fontname="Arial", fontsize=16, fontweight="bold")

# Respondents by age who have seen Star Wars

ages_seen = seen_star_wars["Age"].value_counts(normalize=True).sort_index()*100
age_distribution(ages_seen, [li,li,da,li])
plt.title("Respondents who have seen Star Wars", y = 1.2, fontname="Arial", fontsize=16, fontweight="bold")

# Explore major age population segments

# Explore major age population segments: Respondents by age who have seen at least one Star Wars movie
ages_18_seen = seen_star_wars[seen_star_wars["Age"]=="18-29"]
ages_30_seen = seen_star_wars[seen_star_wars["Age"]=="30-44"]
ages_45_seen = seen_star_wars[seen_star_wars["Age"]=="45-60"]
ages_60_seen = seen_star_wars[seen_star_wars["Age"]=="> 60"]

# Explore major age population segments: Respondents by age who have seen all six movies
ages_18_all = seen_all_movies[seen_all_movies["Age"]=="18-29"]
ages_30_all = seen_all_movies[seen_all_movies["Age"]=="30-44"]
ages_45_all = seen_all_movies[seen_all_movies["Age"]=="45-60"]
ages_60_all = seen_all_movies[seen_all_movies["Age"]=="> 60"]

# Explore major age population segments: Respondents by age who identified as a Star Wars fan and have seen at least one movie
ages_18_fan = star_wars_fans[star_wars_fans["Age"]=="18-29"]
ages_30_fan = star_wars_fans[star_wars_fans["Age"]=="30-44"]
ages_45_fan = star_wars_fans[star_wars_fans["Age"]=="45-60"]
ages_60_fan = star_wars_fans[star_wars_fans["Age"]=="> 60"]

# Explore major age population segments: Respondents by age who identified as a Star Wars fan and have seen all six movies
ages_18_true_fan = true_star_wars_fans[true_star_wars_fans["Age"]=="18-29"]
ages_30_true_fan = true_star_wars_fans[true_star_wars_fans["Age"]=="30-44"]
ages_45_true_fan = true_star_wars_fans[true_star_wars_fans["Age"]=="45-60"]
ages_60_true_fan = true_star_wars_fans[true_star_wars_fans["Age"]=="> 60"]

# Create functions to plot grouped age distributions

li = "#fac06e" # light
me = "#64c987" # medium
ha = "#00898a" # hard
da = "#2a4858" # dark

# Age: Most Viewed Movies

def age_most_viewed(populations):
    """Generates plot showing most viewed movies in ascending order by episode for each age group.
    
    Args:
    - population (function): name of the data set or subset
    - colors (list): list of four strings either 'li', 'me', 'ha, or 'da' to denote light or dark colors for each bar
    """
    
    percents_seen = {}
    for i, pop in enumerate(populations):
        values = []
        for j in range(1,7):
            percent_seen = pop[f"Watched Ep {j}"].sum() / len(pop)
            values.append(percent_seen)

        percents_seen[i] = values

    pop_1_values = percents_seen[0]
    pop_2_values = percents_seen[1]
    pop_3_values = percents_seen[2]
    pop_4_values = percents_seen[3]

    bar_positions = range(1,7)
    bar_width = 0.13

    fig, ax = plt.subplots(figsize = (10, 3), facecolor="#ffffff")
    ax.bar(bar_positions, pop_1_values, width=bar_width, label='18-29', color=li)
    ax.bar([p + bar_width for p in bar_positions], pop_2_values, width=bar_width, label='30-44', color=me)
    ax.bar([p + bar_width * 2 for p in bar_positions], pop_3_values, width=bar_width, label='45-59', color=ha)
    ax.bar([p + bar_width * 3 for p in bar_positions], pop_4_values, width=bar_width, label='> 60', color=da)

    plt.yticks(fontsize=10)
    plt.ylim([0,1])
    ax.yaxis.set_major_formatter(FuncFormatter('{0:.0%}'.format))

    ax.set_xticks([])
    plt.xticks([p + bar_width * 1.5 for p in bar_positions], range(1,7), fontname="Arial", fontsize=14)

    plt.title('Most Viewed Star Wars films', y=1.1, fontname="Arial", fontsize=16, fontweight="bold")

    legend=plt.legend(loc="upper right", bbox_to_anchor=(1.3,1.1))
    plt.setp(legend.texts, family='Arial')

    plt.grid(axis="y", linewidth=0.2)

    spines = ["bottom", "top", "left", "right"]
    for spine in spines:
        ax.spines[spine].set_visible(False)
    ax.tick_params(left=False, bottom=False)

    plt.show()

# Age: Highest Rated Movies

def age_highest_rated(populations):
    """Generates plot showing highest rated movies in ascending order by episode for each age group.
    
    Args:
    - population (function): name of the data set or subset
    - colors (list): list of four strings either 'li', 'me', 'ha, or 'da' to denote light or dark colors for each bar
    """
    
    average_ratings = {}
    for i, pop in enumerate(populations):
        average_rating = pop[pop.columns[9:15]].mean()
        average_ratings[i] = average_rating

    pop_1_values = average_ratings[0]
    pop_2_values = average_ratings[1]
    pop_3_values = average_ratings[2]
    pop_4_values = average_ratings[3]

    bar_positions = range(1,7)
    bar_width = 0.13

    fig, ax = plt.subplots(figsize = (10, 3), facecolor="#ffffff")
    ax.bar(bar_positions, pop_1_values, width=bar_width, label='18-29', color=li)
    ax.bar([p + bar_width for p in bar_positions], pop_2_values, width=bar_width, label='30-44', color=me)
    ax.bar([p + bar_width * 2 for p in bar_positions], pop_3_values, width=bar_width, label='45-59', color=ha)
    ax.bar([p + bar_width * 3 for p in bar_positions], pop_4_values, width=bar_width, label='> 60', color=da)

    plt.yticks(fontsize=10)
    plt.ylim([0,5])

    ax.set_xticks([])
    plt.xticks([p + bar_width * 1.5 for p in bar_positions], range(1,7), fontname="Arial", fontsize=14)

    plt.title('Highest Rated Star Wars films', y=1.1, fontname="Arial", fontsize=16, fontweight="bold")

    legend=plt.legend(loc="upper right", bbox_to_anchor=(1.32,1.1))
    plt.setp(legend.texts, family='Arial')

    plt.grid(axis="y", linewidth=0.2)

    spines = ["bottom", "top", "left", "right"]
    for spine in spines:
        ax.spines[spine].set_visible(False)
    ax.tick_params(left=False, bottom=False)

    plt.show()
    
# Respondents by age who have seen at least one Star Wars movie
populations = [ages_18_seen, ages_30_seen, ages_45_seen, ages_60_seen]
age_most_viewed(populations)
age_highest_rated(populations)

# Respondents by age who have seen all six movies

populations = [ages_18_all, ages_30_all, ages_45_all, ages_60_all]
age_most_viewed(populations)
age_highest_rated(populations)

# Star Wars fans by age
populations = [ages_18_fan, ages_30_fan, ages_45_fan, ages_60_fan]
age_most_viewed(populations)
age_highest_rated(populations)

# True Star Wars fans by age
populations = [ages_18_true_fan, ages_30_true_fan, ages_45_true_fan, ages_60_true_fan]
age_highest_rated(populations)
