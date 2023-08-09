import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings 
import seaborn as sns
from natsort import natsorted

warnings.filterwarnings("ignore")

# %matplotlib inline
sns.set_theme(style="whitegrid")
plt.rcParams["font.family"] = "arial"

# ------------------------------------------------------------------------------------#
# Import the data
# ------------------------------------------------------------------------------------#
df = pd.read_csv("2021 New Coder Survey.csv")

# ------------------------------------------------------------------------------------#
# Explore the data
# ------------------------------------------------------------------------------------#

print(df.head())

print(df.shape)

for column in df.columns:
    print(column)

learning_motivation = "1. What is your biggest reason for learning to code?"
career_interests = "14. Which of these careers are you interested in?"
weekly_learning_hours = "7. About how many hours do you spend learning each week?"
months_of_experience = "8. About how many months have you been programming?"
learning_cost = "9. Aside from university tuition, about how much money have you spent on learning to code so far (in US Dollars)?"
income = "22. About how much money did you earn last year from any job or employment (in US Dollars)? "
age = "23. How old are you?"
race = "25. With which of these groups do you primarily identify?"
location = "26. Which part of the world do you live in?"
state = "27. If you are living in the US, which state do you currently live in? "
highest_education = "32. What is the highest degree or level of school you have completed?"

# ------------------------------------------------------------------------------------#
# Analyze the data
# ------------------------------------------------------------------------------------#

# What careers are most learners interested in?

print(df[career_interests].value_counts(normalize=True).head(10))

prospects = ["Data Scientist", "Game Developer", "Information Security", "No Career Interest", "Data Engineer", "DevOps / SysAdmin"]
df[career_interests] = df[career_interests].replace("I am not interested in a software development career", "No Career Interest")
top_10 = df[career_interests].value_counts(normalize=True).head(10)
light = "#D8D9DA" # gray
dark = "#19376D" # blue

ax = top_10.plot.barh(color=[dark if career in prospects else light for career in top_10.index])
plt.title("Top 10 Career Interests", fontsize=20, x=-0.2, y=1.10)
plt.suptitle(f"Out of {len(df):,} developers", fontsize=13, x=-0.09, y=0.94)
ax.invert_yaxis()
plt.ylabel("")
plt.grid(False)
sns.despine()

# How much are people willing to pay?

df_new = df[df[career_interests].isin(prospects)].copy()

counts = df_new[career_interests].value_counts()
print(counts)

df_new[learning_cost].fillna(0, inplace=True)
df_new[learning_cost] = df_new[learning_cost].astype(float)

average_costs = []
total_costs = []
for prospect, count in zip(prospects, counts):
    average_cost = df_new[df_new[career_interests]==prospect][learning_cost].mean()
    average_costs.append(average_cost)
    total_cost = round(average_cost * count)
    total_costs.append(total_cost)
    print(f"{prospect}: ${total_cost:,}, averaging ${average_cost:.2f} per person")
    
bar_width = 0.35
x_pos = np.arange(len(prospects))
color1 = "#19376D"
color2 = "#FF8400"

fig, ax1 = plt.subplots(figsize=(12, 4))
ax1.bar(x_pos, total_costs, width=bar_width, label='Total Cost', color=color1)
ax2 = ax1.twinx()
ax2.bar(x_pos + bar_width, average_costs, width=bar_width, label='Average Cost', color=color2)

ax1.set_ylabel("Total Cost ($)", color=color1)
ax2.set_ylabel("Average Cost ($)", color=color2)
ax1.grid(axis="y", alpha=0.3)
ax2.grid(axis="y", alpha=0.3)
ax1.tick_params(axis="both", length=0)
ax2.tick_params(axis="both", length=0)

plt.xticks(x_pos + bar_width / 2, prospects)
plt.title("Learner OOP Cost by Career Interest", fontsize=20, x=0.15, y=1.10)
sns.despine(top=True, bottom=True, left=True, right=True)

top5_markets = ["Data Scientist", "Game Developer", "Information Security", "Data Engineer", "DevOps / SysAdmin"]
df_top5 = df_new[df_new[career_interests].isin(top5_markets)]

# What motivates learners to code?

top5_motivations = df_top5["1. What is your biggest reason for learning to code?"].value_counts().head()
print(top5_motivations)

pivot_table = df_top5.pivot_table(index=learning_motivation, columns=career_interests, aggfunc="size")
filtered_pivot_table = pivot_table[pivot_table.index.isin(top5_motivations.index)]

plt.figure(figsize=(7,3))
sns.heatmap(filtered_pivot_table, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=0.5)
plt.xticks(rotation=30, ha="right")
plt.xlabel("")
plt.ylabel("")
plt.suptitle("Learning Motivation Distribution by Career Interest", fontsize=20, x=.17, y=1.1)

top3_markets = ["Data Scientist", "Game Developer", "Information Security"]
df_top3 = df_top5[df_top5[career_interests].isin(top3_markets)]

# What do the demographics of potential markets look like?

# Geographic Location

df_geo_heatmap = pd.DataFrame()
for interest in top3_markets:
    count_by_region = df_top3[df_top3[career_interests] == interest][location].value_counts().head()
    print(f"{interest}:")
    print(count_by_region)
    print(f"{'-'*30}")
    df_geo_heatmap[interest] = count_by_region
plt.figure(figsize=(7, 3))
sns.heatmap(data=df_geo_heatmap, annot=True, fmt="d", cmap="YlGnBu", linewidths=0.5)
plt.title("Top 5 Geographic Locations of Learners", fontsize=20, x=0.02, y=1.1)
plt.xlabel("")
plt.ylabel("")
plt.show()

for interest in top3_markets:
    count_by_state = df_top3[(df_top3[career_interests] == interest) & (df_top3[location] == "North America")][state].value_counts().head(4)
    print(f"{interest}:")
    print(count_by_state)
    print(f"{'-'*30}")

df_top = df_top3[df_top3[location] == "North America"]

# Learning Motivation

top_motivations = df_top[learning_motivation].value_counts().head()
pivot_table = df_top.pivot_table(index=learning_motivation, columns=career_interests, aggfunc="size")
filtered_pivot_table = pivot_table[pivot_table.index.isin(top_motivations.index)]
filtered_pivot_table

plt.figure(figsize=(7,3))
sns.heatmap(filtered_pivot_table, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=0.5)
plt.xticks()
plt.xlabel("")
plt.ylabel("")
plt.suptitle("Top Learning Motivations by Career Interest", fontsize=20, x=.14, y=1.05)

# Age

df_age = df_top[df_top[age] < 90]
df_age.groupby(career_interests).agg({age: pd.Series.mean}).round()

sns.set_palette("husl")
plt.figure(figsize=(6,4))
sns.boxplot(data=df_top, x=career_interests, y=age)
plt.xlabel("")
plt.ylabel("")
sns.despine()
plt.title("Average Age by Career Interest", fontsize=20, x=.25, y=1.1)
sns.despine(top=True, bottom=True, left=True, right=True)

# Race

fig, axes= plt.subplots(nrows=1, ncols=3, figsize=(6,2), sharey=True)
unique_race_values = natsorted(df_top[race].astype(str).unique())

for index, interest in enumerate(top3_markets):
    race_counts = df_top[df_top[career_interests]==interest][race].value_counts().head()

    axes[index].barh(race_counts.index, race_counts.values, color="#19376D")
    axes[index].set_xlabel(interest)
    axes[index].invert_yaxis()
    axes[index].grid(alpha=0.4)
    
plt.suptitle("Top 5 Counts by Race and Career Interest", fontsize=20, x=0.25, y=1.1)
sns.despine(top=True, bottom=True, left=True, right=True)

# Education

for interest in top3_markets:
    edu_counts = df_top[df_top[career_interests]==interest][highest_education].value_counts(normalize=True).head()
    print(edu_counts)

stacked_data = pd.DataFrame()

for interest in top3_markets:
    df_education = df_top[(df_top[career_interests] == interest) & (df_top[highest_education] != 'nan')]
    edu_counts = df_education[highest_education].value_counts()
    stacked_data[interest] = edu_counts

total_counts = stacked_data.sum(axis=1)
sorted_levels = total_counts.sort_values(ascending=False).index
stacked_data = stacked_data.loc[sorted_levels]
stacked_data.plot.barh(stacked=True)

plt.legend(title='Interests')
plt.xlabel("")
plt.ylabel("")
plt.title("Counts of Highest Education Level by Career Interest", fontsize=20, x=0.01, y=1.1)
sns.despine(top=True, bottom=True, left=True, right=True)
plt.gca().invert_yaxis()

# Income

df_top[income] = df_top[income].str.replace("$","").str.replace(",", "").str.replace("to", " - ")
df_top[income] = df_top[income].str.replace("Under 1000", "0 - 1000").str.replace("I don’t know", "nan").str.replace("I don't want  -  answer", "nan")

fig, axes= plt.subplots(nrows=1, ncols=3, figsize=(8,7), sharey=True)
unique_income_values = natsorted(df_top[income].astype(str).unique())
c1 = "#D8D9DA" # gray
c2 = "#19376D" # blue

colors=[
        [c1,c1,c1,c1,c1,c1,c1,c1,c1,c1,c1,c1,c2,c1,c1,c1,c1,c1,c1,c1],
        [c1,c1,c1,c1,c1,c1,c1,c1,c2,c1,c1,c1,c1,c1,c1,c1,c1,c1,c1,c1],
        [c1,c1,c1,c1,c1,c1,c1,c1,c1,c1,c1,c2,c1,c1,c1,c1,c1,c1,c1,c1]
        ]

for index, interest in enumerate(top3_markets):
    income_counts = df_top[df_top[career_interests]==interest][income].value_counts()
    income_counts = income_counts.reindex(unique_income_values, fill_value=0)
    income_counts = income_counts.drop("nan")

    income_midpoints = []
    for value in unique_income_values:
        if value == "nan":
            income_midpoint = 0
        elif value == "250000 or over":
            income_midpoint = 250000
        else:
            income_midpoint = (float(value.split(" - ")[0])+float(value.split(" - ")[1]))/2
        income_midpoints.append(income_midpoint)

    income_midpoints = sorted(income_midpoints[:-1])

    avg_income = np.dot(income_midpoints, income_counts)/income_counts.sum()  
    print(f"Average income of {interest} learners: ${round(avg_income):,}")

    axes[index].barh(income_counts.index, income_counts.values, color=colors[index])
    axes[index].set_xlabel(interest)
    axes[index].invert_yaxis()
    axes[index].grid(alpha=0.4)
    
plt.suptitle("Income Histograms by Career Interest", fontsize=20, x=0.2)
plt.title("Average income marked in blue", x=-2.55, y=1.02, fontsize=15)
sns.despine(top=True, bottom=True, left=True, right=True)
axes[0].set_ylabel("Income ($)")

# Developer Experience vs. Learning Hours

df_filtered = df_top[df_top[career_interests].isin(top3_markets)]
df_filtered[weekly_learning_hours] = pd.to_numeric(df_filtered[weekly_learning_hours], errors="coerce")
df_filtered[months_of_experience] = pd.to_numeric(df_filtered[months_of_experience], errors="coerce")
df_filtered = df_filtered.dropna(subset=[weekly_learning_hours, months_of_experience])

sns.set_palette("muted")
plt.figure(figsize=(6,3))
for interest in top3_markets:
    sns.scatterplot(x=months_of_experience, y=weekly_learning_hours, data=df_filtered[df_filtered[career_interests] == interest], label=interest)

plt.xlabel("Months of Experience")
plt.ylabel("Weekly Learning Hours")
plt.title("Months of Experience vs. Weekly Learning Hours")
sns.despine(top=True, bottom=True, left=True, right=True)
plt.legend()

plt.figure(figsize=(10,4))
for interest in top3_markets:
    sns.scatterplot(x=months_of_experience, y=weekly_learning_hours, data=df_filtered[df_filtered[career_interests] == interest], label=interest)
plt.xlim(0,48)
plt.ylim(0, 80)
plt.xlabel("Months of Experience")
plt.ylabel("Weekly Learning Hours")
plt.legend()
plt.suptitle("Months of Experience vs. Weekly Learning Hours", fontsize=20, x=0.35, y=1.1)
plt.title("For learners with up to 48 months of experience", fontsize=15, x=0.185, y=1.1)

plt.figure(figsize=(10,4))
for interest in top3_markets:
    sns.scatterplot(x=months_of_experience, y=weekly_learning_hours, data=df_filtered[df_filtered[career_interests] == interest], label=interest)
plt.xlim(48,500)
plt.ylim(0, 50)
plt.xlabel("Months of Experience")
plt.ylabel("Weekly Learning Hours")
plt.legend()
plt.suptitle("Months of Experience vs. Weekly Learning Hours", fontsize=20, x=0.35, y=1.1)
plt.title("For learners with 4+ years of experience", fontsize=15, x=0.14, y=1.1)

df_top[months_of_experience]=df_top[months_of_experience].astype(float)
df_top = df_top[df_top[months_of_experience] < 500.0]
print(df_top.groupby(career_interests)[months_of_experience].mean(numeric_only=True))

df_top = df_top[df_top[weekly_learning_hours] <= 80]
print(df_top.groupby(career_interests)[weekly_learning_hours].mean())

# Cost of Learning

counts = df_top[career_interests].value_counts()
print(counts)
df_top[learning_cost].fillna(0, inplace=True)
df_top[learning_cost] = df_top[learning_cost].astype(int)

average_costs = []
total_costs = []
for interest, count in zip(top3_markets, counts):
    average_cost = df_top[df_top[career_interests]==interest][learning_cost].mean()
    average_costs.append(average_cost)
    total_cost = round(average_cost * count,1)
    total_costs.append(total_cost)
    print(f"{interest}: ${total_cost:,}, averaging ${average_cost:.2f} per person")
    bar_width = 0.35
    
x_pos = np.arange(len(top3_markets))
color1 = "#19376D" # blue
color2 = "#FF8400" # orange

fig, ax1 = plt.subplots(figsize=(7, 3))
ax1.bar(x_pos, total_costs, width=bar_width, label='Total Cost', color=color1)
ax2 = ax1.twinx()
ax2.bar(x_pos + bar_width, average_costs, width=bar_width, label='Average Cost', color=color2)

ax1.set_ylabel("Total Cost ($)", color=color1)
ax2.set_ylabel("Average Cost ($)", color=color2)
ax1.grid(axis="y", alpha=0.3)
ax2.grid(axis="y", alpha=0.3)
ax1.tick_params(axis="both", length=0)
ax2.tick_params(axis="both", length=0)

plt.xticks(x_pos + bar_width / 2, top3_markets)
plt.title("Learner OOP Cost by Career Interest", fontsize=20, x=0.2, y=1.10)
sns.despine(top=True, bottom=True, left=True, right=True)
