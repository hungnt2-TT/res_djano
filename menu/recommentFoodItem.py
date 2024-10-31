import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split

# Sample dataset
food_names = ['bánh mì', 'mì tôm', 'lẩu', 'pizza', 'cơm', 'xôi', 'bún bò']
time_ranges = ['morning', 'morning', 'evening', 'evening', 'afternoon', 'morning', 'night']

# Convert to feature vectors
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(food_names)

# Train a Naive Bayes model
X_train, X_test, y_train, y_test = train_test_split(X, time_ranges, test_size=0.2)
clf = MultinomialNB()
clf.fit(X_train, y_train)

# Save the model and vectorizer
joblib.dump(clf, 'food_time_model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')
