import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split

# Sample dataset
food_names = [
    'bánh mì', 'mì tôm', 'lẩu', 'pizza', 'cơm', 'xôi', 'bún bò',
    'phở', 'cháo', 'hủ tiếu', 'sushi', 'bánh cuốn', 'bánh bao', 'bánh giò',
    'bánh xèo', 'gỏi cuốn', 'trà sữa', 'nước ép', 'trà đào', 'chè đậu xanh',
    'bánh kem', 'bánh trung thu', 'gà rán', 'khoai tây chiên', 'salad', 'cà phê',
    'trứng ốp la', 'bánh tráng trộn', 'mì ý', 'hamburger', 'bò né', 'súp cua',
    'canh chua', 'cơm tấm', 'bún thịt nướng', 'sữa chua', 'kem', 'bò kho',
    'bánh đúc', 'mì quảng', 'bánh bèo', 'chả cá', 'mực nướng', 'bánh mì pate',
    'cá kho tộ', 'cà ri gà', 'bánh ít', 'bánh cốm', 'nem lụi', 'bánh bột lọc',
    'bánh tằm bì', 'cá lóc nướng', 'tào phớ', 'mắm tôm', 'bún mắm', 'nem nướng',
    'bánh hỏi', 'bún chả', 'cơm cháy', 'bún đậu mắm tôm', 'canh khổ qua',
    'canh bún', 'bánh gai', 'mì cay', 'bánh canh', 'gỏi gà', 'bánh ít trần',
    'lẩu thái', 'cháo vịt', 'lòng nướng', 'bún măng vịt', 'gỏi sứa',
    'chè khúc bạch', 'chè thưng', 'gỏi bưởi', 'bánh tiêu', 'xôi gấc', 'xôi gà',
    'xôi xéo', 'lẩu rêu cua', 'lẩu ếch', 'lẩu cá', 'cơm gà', 'cơm sườn', 'cơm chiên', 'bia', 'rượu', 'nước ngọt',
    'cafe', 'cafe', 'cafe',
    'chiên rán', 'chiên rán'

]

time_ranges = [
    'morning', 'morning', 'evening', 'evening', 'afternoon', 'morning', 'night',
    'morning', 'morning', 'morning', 'evening', 'morning', 'morning', 'morning',
    'afternoon', 'afternoon', 'afternoon', 'afternoon', 'afternoon', 'afternoon',
    'night', 'night', 'evening', 'evening', 'evening', 'morning',
    'afternoon', 'evening', 'evening', 'morning', 'morning',
    'evening', 'morning', 'morning', 'night', 'night', 'morning',
    'afternoon', 'afternoon', 'afternoon', 'afternoon', 'evening', 'morning',
    'afternoon', 'afternoon', 'afternoon', 'afternoon', 'evening', 'morning',
    'evening', 'evening', 'afternoon', 'afternoon', 'morning', 'evening',
    'morning', 'evening', 'afternoon', 'afternoon', 'afternoon',
    'afternoon', 'afternoon', 'afternoon', 'evening', 'morning',
    'evening', 'morning', 'evening', 'night', 'night', 'afternoon',
    'afternoon', 'evening', 'evening', 'afternoon', 'night', 'morning',
    'morning', 'morning', 'evening', 'evening', 'evening', 'evening', 'evening', 'evening', 'evening', 'evening',
    'all_day', 'morning', 'afternoon', 'evening', 'afternoon', 'evening'
]

print("Số lượng food_names:", len(food_names))
print("Số lượng time_ranges:", len(time_ranges))
# Convert to feature vectors
# Chuyển đổi thành vector đặc trưng
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(food_names)

# Chia dữ liệu huấn luyện và kiểm thử
X_train, X_test, y_train, y_test = train_test_split(X, time_ranges, test_size=0.2, random_state=42)

# Huấn luyện mô hình Naive Bayes
clf = MultinomialNB()
clf.fit(X_train, y_train)

# Lưu mô hình và vectorizer
joblib.dump(clf, 'food_time_model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')
