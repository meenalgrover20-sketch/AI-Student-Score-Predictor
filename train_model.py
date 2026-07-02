import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

# Dataset load karo
data = pd.read_csv("student_scores.csv")

# Input aur Output define karo
X = data[['Hours_Studied', 'Attendance', 'Previous_Score']]
y = data['Score']

# Model banao
model = LinearRegression()

# Model train karo
model.fit(X, y)

# Model save karo
joblib.dump(model, "model.pkl")

print("✅ Model trained successfully!")
print("✅ model.pkl file created.")