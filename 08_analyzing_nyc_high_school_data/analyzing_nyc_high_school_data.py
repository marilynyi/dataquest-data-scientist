import numpy as np
import pandas as pd
import re
import logging
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
from IPython import display

# %matplotlib inline
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.CRITICAL)

# Import the data files
files = [
    "ap_2010.csv",
    "class_size.csv",
    "demographics.csv",
    "graduation.csv",
    "hs_directory.csv",
    "sat_results.csv",
]

data = {}

for file in files:
    contents = pd.read_csv(f"schools/{file}")
    file = file.replace(".csv", "")
    data[file] = contents
    
# Import the survey files
all_survey = pd.read_csv("schools/survey_all.txt", delimiter="\t", encoding='windows-1252')
d75_survey = pd.read_csv("schools/survey_d75.txt", delimiter="\t", encoding='windows-1252')
survey = pd.concat([all_survey, d75_survey], axis=0)

survey["DBN"] = survey["dbn"]

survey_fields = [
    "DBN", 
    "rr_s", 
    "rr_t", 
    "rr_p", 
    "N_s", 
    "N_t", 
    "N_p", 
    "saf_p_11", 
    "com_p_11", 
    "eng_p_11", 
    "aca_p_11", 
    "saf_t_11", 
    "com_t_11", 
    "eng_t_11", 
    "aca_t_11", 
    "saf_s_11", 
    "com_s_11", 
    "eng_s_11", 
    "aca_s_11", 
    "saf_tot_11", 
    "com_tot_11", 
    "eng_tot_11", 
    "aca_tot_11",
]

survey = survey.loc[:, survey_fields]
data["survey"] = survey

# Add DBN columns
data["hs_directory"]["DBN"] = data["hs_directory"]["dbn"]

def pad_csd(num):
    string_representation = str(num)
    if len(string_representation) > 1:
        return string_representation
    else:
        return "0" + string_representation
    
data["class_size"]["padded_csd"] = data["class_size"]["CSD"].apply(pad_csd)
data["class_size"]["DBN"] = data["class_size"]["padded_csd"] + data["class_size"]["SCHOOL CODE"]

# Convert columns to numeric
cols = ["SAT Math Avg. Score", "SAT Critical Reading Avg. Score", "SAT Writing Avg. Score"]
for c in cols:
    data["sat_results"][c] = pd.to_numeric(data["sat_results"][c], errors="coerce")

data["sat_results"]["sat_score"] = data["sat_results"][cols[0]] + data["sat_results"][cols[1]] + data["sat_results"][cols[2]]

def find_lat(loc):
    coords = re.findall("\(.+, .+\)", loc)
    lat = coords[0].split(",")[0].replace("(", "")
    return lat

def find_lon(loc):
    coords = re.findall("\(.+, .+\)", loc)
    lon = coords[0].split(",")[1].replace(")", "").strip()
    return lon

data["hs_directory"]["lat"] = data["hs_directory"]["Location 1"].apply(find_lat)
data["hs_directory"]["lon"] = data["hs_directory"]["Location 1"].apply(find_lon)

data["hs_directory"]["lat"] = pd.to_numeric(data["hs_directory"]["lat"], errors="coerce")
data["hs_directory"]["lon"] = pd.to_numeric(data["hs_directory"]["lon"], errors="coerce")

# Condense datasets
class_size = data["class_size"]
class_size = class_size[class_size["GRADE "] == "09-12"]
class_size = class_size[class_size["PROGRAM TYPE"] == "GEN ED"]

class_size = class_size.groupby("DBN").mean(numeric_only=True)
class_size.reset_index(inplace=True)
data["class_size"] = class_size

data["demographics"] = data["demographics"][data["demographics"]["schoolyear"] == 20112012]

data["graduation"] = data["graduation"][data["graduation"]["Cohort"] == "2006"]
data["graduation"] = data["graduation"][data["graduation"]["Demographic"] == "Total Cohort"]

# Convert AP scores to numeric
cols = ["AP Test Takers ", "Total Exams Taken", "Number of Exams with scores 3 4 or 5"]

for col in cols:
    data["ap_2010"][col] = pd.to_numeric(data["ap_2010"][col], errors="coerce")
    
# Combine the datasets
combined = data["sat_results"]

combined = combined.merge(data["ap_2010"], on="DBN", how="left")
combined = combined.merge(data["graduation"], on="DBN", how="left")

to_merge = ["class_size", "demographics", "survey", "hs_directory"]

for m in to_merge:
    combined = combined.merge(data[m], on="DBN", how="inner")

combined = combined.fillna(combined.mean(numeric_only=True))
combined = combined.fillna(0)

# Add a school district column for mapping
def get_first_two_chars(dbn):
    return dbn[0:2]

combined["school_dist"] = combined["DBN"].apply(get_first_two_chars)

# Define function to remove edges of visual charts
def remove_spines():
    for ax in axes:
        for spine in spines:
            ax.spines[spine].set_visible(False)
            ax.tick_params(left=0, bottom=0)
            ax.grid(alpha=0.5)

# Find correlations to SAT score
sat_score_corr = combined.corr(numeric_only=True)["sat_score"]
print(sat_score_corr)

# Plot survey correlations
# Remove DBN since it's a unique identifier, not a useful numerical value for correlation.
survey_fields.remove("DBN")
print(survey_fields)
sat_score_corr[survey_fields].plot.bar()
plt.show()

# Average SAT score of New York high school student
print(round(combined["sat_score"].mean(numeric_only=True)))

# Number of respondents vs. SAT score
fig, (ax1, ax2, ax3) = plt.subplots(1,3, figsize=(9,3))
fig.suptitle("Number of respondents vs. SAT score")
ax1.scatter(combined["N_s"], combined["sat_score"])
ax2.scatter(combined["N_p"], combined["sat_score"])
ax3.scatter(combined["N_t"], combined["sat_score"])

axes = [ax1, ax2, ax3]
spines = ["left", "right", "top", "bottom"]

remove_spines()

ax1.set_xlabel("# of Students")
ax2.set_xlabel("# of Parents")
ax3.set_xlabel("# of Teachers")
ax1.set_ylabel("SAT score")

ax2.set_yticklabels([])
ax3.set_yticklabels([])
plt.show()

# Safety and Respect score based on respondent response vs. SAT score
fig, (ax1, ax2) = plt.subplots(1,2, figsize=(7,3))
fig.suptitle("Safety and Respect score vs. SAT score")
ax1.scatter(x=combined["saf_s_11"], y=combined["sat_score"])
ax2.scatter(x=combined["saf_t_11"], y=combined["sat_score"])

axes = [ax1, ax2]
spines = ["left", "right", "top", "bottom"]

remove_spines()

for ax in axes:
    for spine in spines:
        ax.set_xlim(3, 10)
        ax.set_ylim(800, 2200)
        
ax1.set_xlabel("Student Score")
ax2.set_xlabel("Teacher Score")
ax1.set_ylabel("SAT score")
        
ax2.set_yticklabels([])
plt.show()

# Geographic correlations with SAT score (by borough)
display.Image("ny-boroughs.png", width=500)

# Number of respondents vs. SAT score (by borough)
boro_s = combined.groupby("boro").mean(numeric_only=True)["N_s"]
print(boro_s)

boro_t = combined.groupby("boro").mean(numeric_only=True)["N_t"]
print(boro_t)

boro_p = combined.groupby("boro").mean(numeric_only=True)["N_p"]
print(boro_p)

# Safety and Respect score vs. SAT score (by borough)
boro_safety_s = combined.groupby("boro").mean(numeric_only=True)["saf_s_11"]
print(boro_safety_s)

boro_safety_t = combined.groupby("boro").mean(numeric_only=True)["saf_t_11"]
print(boro_safety_t)

boro_safety_tot = combined.groupby("boro").mean(numeric_only=True)["saf_tot_11"]
print(boro_safety_tot)

# Borough vs. SAT score
boro_score = combined.groupby("boro").mean(numeric_only=True)["sat_score"]
print(boro_score)

# Race correlations with SAT score
race_fields = ["white_per", "asian_per", "black_per", "hispanic_per"]
sat_score_corr[race_fields].plot.bar()
plt.show()

fig, (ax1, ax2, ax3, ax4) = plt.subplots(1,4, figsize=(9,3))
fig.suptitle("Race vs. SAT score")
ax1.scatter(x=combined["white_per"], y=combined["sat_score"])
ax2.scatter(x=combined["asian_per"], y=combined["sat_score"])
ax3.scatter(x=combined["black_per"], y=combined["sat_score"])
ax4.scatter(x=combined["hispanic_per"], y=combined["sat_score"])

axes = [ax1, ax2, ax3, ax4]
spines = ["left", "right", "top", "bottom"]

remove_spines()

for ax in axes:
    for spine in spines:
        ax.set_xlim(-5, 105)
        ax.set_ylim(800, 2200)
        
ax1.set_xlabel("% White")
ax2.set_xlabel("% Asian")
ax3.set_xlabel("% Black")
ax4.set_xlabel("% Hispanic")
ax1.set_ylabel("SAT Score")
        
ax2.set_yticklabels([])
ax3.set_yticklabels([])
ax4.set_yticklabels([])
plt.show()

fig, (ax1, ax2, ax3, ax4) = plt.subplots(1,4, figsize=(9,3))
fig.suptitle("Race vs. Safety and Respect Score")
ax1.scatter(x=combined["white_per"], y=combined["saf_s_11"])
ax2.scatter(x=combined["asian_per"], y=combined["saf_s_11"])
ax3.scatter(x=combined["black_per"], y=combined["saf_s_11"])
ax4.scatter(x=combined["hispanic_per"], y=combined["saf_s_11"])

axes = [ax1, ax2, ax3, ax4]
spines = ["left", "right", "top", "bottom"]

remove_spines()

for ax in axes:
    for spine in spines:
        ax.set_xlim(-5, 105)
        ax.set_ylim(4.5, 9.5)

ax1.set_xlabel("% White")
ax2.set_xlabel("% Asian")
ax3.set_xlabel("% Black")
ax4.set_xlabel("% Hispanic")
ax1.set_ylabel("Safety and Respect Score")
        
ax2.set_yticklabels([])
ax3.set_yticklabels([])
ax4.set_yticklabels([])
plt.show()

high_hispanic_pop = combined["hispanic_per"] > 95
print(combined[high_hispanic_pop][["SCHOOL NAME", "boro"]])

# Gender correlations with SAT score
gender_fields = ["male_per", "female_per"]
sat_score_corr[gender_fields].plot.bar()
plt.show()

fig, (ax1, ax2) = plt.subplots(1,2, figsize=(7,3))
fig.suptitle("Gender vs. SAT score")
ax1.scatter(x=combined["male_per"], y=combined["sat_score"])
ax2.scatter(x=combined["female_per"], y=combined["sat_score"])

axes = [ax1, ax2]
spines = ["left", "right", "top", "bottom"]

remove_spines()

for ax in axes:
    for spine in spines:
        ax.set_xlim(-5, 105)
        ax.set_ylim(800, 2200)
        
ax1.set_xlabel("% Male")
ax2.set_xlabel("% Female")
ax1.set_ylabel("SAT Score")
        
ax2.set_yticklabels([])
plt.show()

# High male population and high SAT score
high_male_perf = (combined["male_per"] > 55) & (combined["sat_score"] > 1700)
print(combined[high_male_perf][["SCHOOL NAME", "boro"]])

print(combined[high_male_perf][["saf_s_11", "boro", "white_per", "asian_per", "black_per", "hispanic_per"]])

# High female population and high SAT score
high_female_perf = (combined["female_per"] > 65) & (combined["sat_score"] > 1700)
print(combined[high_female_perf][["SCHOOL NAME", "boro"]])

print(combined[high_female_perf][["saf_s_11", "boro", "white_per", "asian_per", "black_per", "hispanic_per"]])

# 100% female population and low SAT score
high_female_pop = combined["female_per"] > 95
print(combined[high_female_pop][["SCHOOL NAME", "boro"]])

print(combined[high_female_pop][["saf_s_11", "boro", "white_per", "asian_per", "black_per", "hispanic_per"]])

# AP exam scores vs. SAT score
combined["ap_per"] = combined["AP Test Takers "]/combined["total_enrollment"]
combined.plot.scatter(x="ap_per", y="sat_score")
plt.show()
