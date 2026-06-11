import numpy as np
import pandas as pd
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score

# List of target crops supported by South Indian agriculture
CROPS = [
    "Rice", "Banana", "Coconut", "Turmeric", "Pepper", "Cardamom",
    "Mango", "Jackfruit", "Arecanut", "Tapioca", "Sugarcane", "Drumstick"
]

def generate_synthetic_data(num_samples=1200):
    """
    Generates synthetic agricultural data representing South Indian soil and weather profiles
    for training models.
    """
    np.random.seed(42)
    data = []
    
    for _ in range(num_samples):
        # Pick a target crop and generate realistic parameters for it
        crop = np.random.choice(CROPS)
        
        if crop == "Rice":
            n, p, k = np.random.uniform(70, 95), np.random.uniform(35, 50), np.random.uniform(35, 45)
            ph = np.random.uniform(5.5, 6.8)
            temp = np.random.uniform(22, 32)
            hum = np.random.uniform(75, 90)
            rain = np.random.uniform(180, 250)
        elif crop == "Banana":
            n, p, k = np.random.uniform(90, 120), np.random.uniform(40, 60), np.random.uniform(110, 140)
            ph = np.random.uniform(6.0, 7.5)
            temp = np.random.uniform(24, 35)
            hum = np.random.uniform(70, 85)
            rain = np.random.uniform(140, 200)
        elif crop == "Coconut":
            n, p, k = np.random.uniform(40, 60), np.random.uniform(25, 35), np.random.uniform(70, 100)
            ph = np.random.uniform(5.2, 8.0)
            temp = np.random.uniform(25, 33)
            hum = np.random.uniform(65, 80)
            rain = np.random.uniform(100, 180)
        elif crop == "Turmeric":
            n, p, k = np.random.uniform(50, 75), np.random.uniform(30, 45), np.random.uniform(60, 80)
            ph = np.random.uniform(5.0, 6.5)
            temp = np.random.uniform(20, 30)
            hum = np.random.uniform(60, 75)
            rain = np.random.uniform(120, 160)
        elif crop == "Pepper":
            n, p, k = np.random.uniform(35, 55), np.random.uniform(20, 35), np.random.uniform(40, 60)
            ph = np.random.uniform(5.5, 6.5)
            temp = np.random.uniform(18, 28)
            hum = np.random.uniform(70, 85)
            rain = np.random.uniform(180, 280)
        elif crop == "Cardamom":
            n, p, k = np.random.uniform(30, 50), np.random.uniform(25, 40), np.random.uniform(50, 75)
            ph = np.random.uniform(4.8, 6.0)
            temp = np.random.uniform(15, 24)
            hum = np.random.uniform(75, 95)
            rain = np.random.uniform(200, 320)
        elif crop == "Sugarcane":
            n, p, k = np.random.uniform(110, 140), np.random.uniform(50, 70), np.random.uniform(60, 90)
            ph = np.random.uniform(6.5, 7.8)
            temp = np.random.uniform(26, 38)
            hum = np.random.uniform(55, 75)
            rain = np.random.uniform(110, 160)
        elif crop == "Tapioca":
            n, p, k = np.random.uniform(40, 60), np.random.uniform(30, 50), np.random.uniform(70, 95)
            ph = np.random.uniform(5.5, 7.0)
            temp = np.random.uniform(22, 30)
            hum = np.random.uniform(50, 70)
            rain = np.random.uniform(80, 130)
        else: # Mango, Jackfruit, Arecanut, Drumstick
            n, p, k = np.random.uniform(40, 80), np.random.uniform(20, 45), np.random.uniform(40, 85)
            ph = np.random.uniform(6.0, 7.5)
            temp = np.random.uniform(24, 34)
            hum = np.random.uniform(50, 80)
            rain = np.random.uniform(90, 150)
            
        data.append([n, p, k, ph, temp, hum, rain, crop])

    cols = ["nitrogen", "phosphorus", "potassium", "ph", "temperature", "humidity", "rainfall", "crop"]
    return pd.DataFrame(data, columns=cols)

def train_and_select_best_model():
    print("Generating agricultural training dataset...")
    df = generate_synthetic_data(1500)
    
    X = df.drop("crop", axis=1)
    y = df["crop"]
    
    # Encode crop classes
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    
    print("Training models...")
    
    # 1. Random Forest
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    rf_acc = accuracy_score(y_test, rf.predict(X_test))
    print(f"Random Forest Accuracy: {rf_acc * 100:.2f}%")
    
    # 2. XGBoost
    xgb = XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='mlogloss')
    xgb.fit(X_train, y_train)
    xgb_acc = accuracy_score(y_test, xgb.predict(X_test))
    print(f"XGBoost Accuracy: {xgb_acc * 100:.2f}%")
    
    # 3. LightGBM
    lgb = LGBMClassifier(random_state=42, verbose=-1)
    lgb.fit(X_train, y_train)
    lgb_acc = accuracy_score(y_test, lgb.predict(X_test))
    print(f"LightGBM Accuracy: {lgb_acc * 100:.2f}%")
    
    # Select best model
    models = {
        "Random Forest": (rf, rf_acc),
        "XGBoost": (xgb, xgb_acc),
        "LightGBM": (lgb, lgb_acc)
    }
    
    best_name, (best_model, best_accuracy) = max(models.items(), key=lambda item: item[1][1])
    print(f"\nWinner: {best_name} with Accuracy {best_accuracy * 100:.2f}%")
    
    # Save the best model and LabelEncoder
    payload = {
        "model": best_model,
        "model_name": best_name,
        "label_encoder": le,
        "accuracy": best_accuracy
    }
    
    output_dir = "backend/app/ml_models"
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, "crop_model.pkl")
    
    with open(model_path, "wb") as f:
        pickle.dump(payload, f)
    
    print(f"Best crop model serialized successfully to {model_path}")

if __name__ == "__main__":
    train_and_select_best_model()
