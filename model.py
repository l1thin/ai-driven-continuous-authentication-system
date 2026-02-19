from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd

df=pd.read_csv('final_ml_dataset.csv')

X = df.drop(columns=["label"])
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier()
model.fit(X_train, y_train)

pred = model.predict(X_test)

from sklearn.model_selection import cross_val_score

scores = cross_val_score(model, X, y, cv=10)
print(scores)
print("Average:", scores.mean())


