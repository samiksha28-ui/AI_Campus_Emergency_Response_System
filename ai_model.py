from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


# Training data
texts = [
    "fire in campus",
    "building is burning",
    "smoke and fire",
    "medical emergency",
    "student is injured",
    "person is unconscious",
    "accident happened",
    "road accident",
    "vehicle accident",
    "security threat",
    "fight in campus",
    "unknown person entered campus",
    "lost item",
    "minor issue"
]

labels = [
    "High",
    "High",
    "High",
    "High",
    "High",
    "High",
    "High",
    "High",
    "High",
    "Medium",
    "Medium",
    "Medium",
    "Low",
    "Low"
]


# Convert text into numerical features
vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(texts)


# Train ML model
model = LogisticRegression()

model.fit(X, labels)


# Prediction function
def predict_priority(description):

    data = vectorizer.transform([description])

    prediction = model.predict(data)

    return prediction[0]


# Test
if __name__ == "__main__":

    test = "There is a fire in the college building"

    result = predict_priority(test)

    print("Emergency:", test)
    print("Predicted Priority:", result)