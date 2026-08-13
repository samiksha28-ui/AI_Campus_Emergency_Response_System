from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


# Training data
texts = [
    "fire in college building",
    "building is burning",
    "smoke and fire in campus",
    "there is a fire",

    "student is injured",
    "person is unconscious",
    "medical emergency",
    "student needs medical help",

    "car accident happened",
    "two vehicles collided",
    "road accident in campus",
    "bike accident",

    "fight in campus",
    "security threat",
    "unknown person entered campus",
    "student is being threatened"
]


labels = [
    "Fire",
    "Fire",
    "Fire",
    "Fire",

    "Medical",
    "Medical",
    "Medical",
    "Medical",

    "Accident",
    "Accident",
    "Accident",
    "Accident",

    "Security",
    "Security",
    "Security",
    "Security"
]


# Convert text into numerical features
vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(texts)


# Create ML model
model = LogisticRegression()

model.fit(X, labels)


# Prediction function
def predict_emergency_type(description):

    data = vectorizer.transform([description])

    prediction = model.predict(data)

    return prediction[0]


# Test model
if __name__ == "__main__":

    test_description = "There is a fire in the college building"

    result = predict_emergency_type(test_description)

    print("Description:", test_description)
    print("Predicted Emergency Type:", result)