import numpy as np 
import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt 
import ipywidgets as widgets
from IPython.display import display, clear_output
from sklearn.model_selection import train_test_split, GridSearchCV, KFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.metrics import accuracy_score, confusion_matrix

sns.set_theme(style="whitegrid")
plt.rcParams["font.family"] = "arial"

np.random.seed(1)

# Import the data
heart_data = pd.read_csv("heart_disease_prediction.csv")
X = heart_data.iloc[:, :-1].values
y = heart_data.iloc[:, -1].values

# Explore the data
print(heart_data.head())
print(heart_data.shape)
print(heart_data.info())
heart_describe = heart_data.describe()

mean_lower = heart_describe.loc["mean", "Age"] - heart_describe.loc["std", "Age"]
mean_upper = heart_describe.loc["mean", "Age"] + heart_describe.loc["std", "Age"]
print(f"Average patient age range: ({round(mean_lower)}, {round(mean_upper)})")

cholesterol_median = heart_describe.loc["50%", "Cholesterol"]
cholesterol_mean = heart_describe.loc["mean", "Cholesterol"]
skew_direction = cholesterol_median - cholesterol_mean
print(f"Skewness direction: {round(skew_direction,2)}")

# Categorical data
categorical_cols = heart_data.select_dtypes(include=["object"]).columns
print(categorical_cols)

binary_cols = ["FastingBS", "HeartDisease"]
for col in binary_cols:
    print(f"{col}: {heart_data[col].unique()}")
    
print(categorical_cols.dtype)

categorical_cols = categorical_cols.union(binary_cols)
print(categorical_cols)

fig = plt.figure(figsize=(15,20))
for index, col in enumerate(categorical_cols):
    ax = plt.subplot(4, 2, index+1)
    sns.countplot(x=heart_data[col], ax=ax, hue=heart_data["HeartDisease"], palette="bright")
    plt.title(label=f"{col}", fontsize=14, loc="left", x=-0.06, y=1.03)
    plt.xlabel("")
    plt.ylabel("")
    sns.despine()
    for container in ax.containers:
        ax.bar_label(container, label_type="center", fontsize=12, fontweight="bold", color="white")
plt.suptitle("Categorical Heart Data Histograms", fontsize=20, x= 0.14, y=1)
plt.tight_layout(pad=1.0)

for col in categorical_cols:
    print(heart_data[col].value_counts(normalize=True))
    print('-'*30)
    
print(round(392/(392+104),2)) # pop with heart disease / pop with ASY chest pain
print(round(316/(316+55),2)) # pop with heart disease / pop with exercise-induced angina
print(round(170/(170+44),2)) # pop with heart disease / pop with FastingBS > 120 mg/dl
print(round(381/(381+79),2)) # pop with heart disease/ pop with flat ST slope
print(round((458+267)/(267+458+143+50),2)) # males / total dataset pop

# Clean the data
heart_data[heart_data["RestingBP"]==0]
heart_data[heart_data["Cholesterol"]==0]

heart_data_new = heart_data.copy()
heart_data_new = heart_data_new[heart_data_new["RestingBP"] != 0]

no_heart_disease = heart_data_new["HeartDisease"]==0

col_cholesterol_no_heart_disease = heart_data_new.loc[no_heart_disease, "Cholesterol"]
col_cholesterol_heart_disease = heart_data_new.loc[~no_heart_disease, "Cholesterol"]

heart_data_new.loc[no_heart_disease, "Cholesterol"] = col_cholesterol_no_heart_disease.replace(to_replace = 0, value = col_cholesterol_no_heart_disease.median())
heart_data_new.loc[~no_heart_disease, "Cholesterol"] = col_cholesterol_heart_disease.replace(to_replace = 0, value = col_cholesterol_heart_disease.median())
heart_data_new[["Cholesterol", "RestingBP"]].describe()

# Feature selection

print(heart_data_new.select_dtypes(include=["object"]).columns)
print(heart_data_new["ChestPainType"].value_counts())
print(categorical_cols)

heart_data_corr = heart_data_new.copy()
heart_data_corr = pd.get_dummies(heart_data_corr, drop_first=False)

plt.figure(figsize=(12,5))
sns.heatmap(abs(heart_data_corr.corr()), 
            fmt=".2f",
            annot=True, 
            annot_kws={"size": 9})

plt.figure(figsize=(10,5))
sns.heatmap(abs(heart_data_corr.corr())[abs(heart_data_corr.corr())>0.4], 
            annot=True, 
            annot_kws={"size": 9})

# Split the dataset
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.15)

# One-hot encoding
print(heart_data_new.columns)

heart_data_features = heart_data_new.drop("HeartDisease", axis=1)
cat_features = heart_data_features.columns
print(cat_features)

cat_indices = [i for i, cat in enumerate(cat_features) if cat in categorical_cols]
print(cat_indices)

ct = ColumnTransformer(
    transformers=[
        ("encoder", OneHotEncoder(), cat_indices)], remainder="passthrough")
X_train = ct.fit_transform(X_train)
X_val = ct.transform(X_val)

# Feature scaling
scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)

# Build the model
knn = KNeighborsClassifier(n_neighbors=2)
knn.fit(X_train_scaled, y_train)
train_accuracy = knn.score(X_train_scaled, y_train)
print(f"Model accuracy on training set: {train_accuracy*100:.2f}%")
test_accuracy = knn.score(X_val_scaled, y_val)
print(f"Model accuracy on test set: {test_accuracy*100:.2f}%")

# Tune the model
knn = KNeighborsClassifier()
grid_params = {"n_neighbors": range(1, 21),
               "metric": ["minkowski", "manhattan"]
              }
fold_values = range(2, 21)

mean_scores = {}
max_score = 0.0
best_fold_value = 0
best_n_neighbors = 0
for fold_value in fold_values:
    kf = KFold(n_splits = fold_value, shuffle=True)
    knn_grid = GridSearchCV(knn, grid_params, scoring="accuracy", cv=kf)
    knn_grid.fit(X_train_scaled, y_train)
    best_params = knn_grid.best_params_
    best_score = knn_grid.best_score_
    mean_scores[fold_value]={"n": best_params["n_neighbors"], "best_score": best_score}
    
    if best_score > max_score:
        max_score = best_score
        best_fold_value = fold_value
        best_n_neighbors = best_params["n_neighbors"]
        best_metric = best_params["metric"]
        
print(f"Best k-folds: {best_fold_value}, Best n-neighbors: {best_n_neighbors}, Best score: {max_score*100:.2f}%, Best metric: {best_metric}")

x_values = []
y_values = []
sizes = []

for fold_value, scores in mean_scores.items():
    x_values.append(fold_value)
    y_values.append(scores["n"])
    sizes.append(scores["best_score"])

plt.figure(figsize=(6, 7))
sns.scatterplot(x=x_values, y=y_values, hue=sizes, size=sizes, sizes=(100, 1000), legend=False)
plt.xlabel("Number of Cross Validation Folds (k)")
plt.ylabel("Number of Nearest Neighbors (n)")
plt.title("Mean Cross-Validation Scores of Training Set", fontsize=20)
plt.grid(True)
plt.show()

for fold_value, nested_dict in mean_scores.items():
    n_neighbors = nested_dict["n"]
    score = nested_dict["best_score"]
    if score > max_score-0.005:
        print(f"k: {fold_value}, n: {n_neighbors}, best score: {score*100:.2f}%")
        
# Evaluate the model on the test set
knn_best = KNeighborsClassifier(n_neighbors=best_n_neighbors, metric=best_metric)
knn_best.fit(X_train_scaled, y_train)

X_val_scaled = scaler.transform(X_val)
predictions = knn_best.predict(X_val_scaled)
accuracy = accuracy_score(y_val, predictions)
print(f" Model accuracy on test set: {accuracy*100:.2f}%")

print(len(X_val))

cm = confusion_matrix(y_val, predictions)
names = [0, 1]

plt.figure(figsize=(4, 3))
sns.heatmap(cm, 
            annot=True, 
            fmt='d',
            xticklabels=names, 
            yticklabels=names)
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix for Test Set', fontsize=20, y=1.04)
plt.show()

