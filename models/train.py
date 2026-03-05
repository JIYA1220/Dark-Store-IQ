import pandas as pd
import numpy as np
import sqlite3
import pickle
import os
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, r2_score

def train_models():
    conn = sqlite3.connect("data/darkstore.db")
    df = pd.read_sql("SELECT * FROM zones", conn)
    conn.close()

    # Encode income level
    le = LabelEncoder()
    df["income_encoded"] = le.fit_transform(df["income_level"])

    FEATURES = [
        "population_density", "avg_order_value_inr", "daily_orders",
        "competitor_count", "delivery_time_min", "internet_penetration",
        "real_estate_cost_sqft", "road_connectivity_score",
        "young_population_pct", "working_professionals_pct",
        "weekend_order_spike", "avg_delivery_rating", "income_encoded"
    ]

    X = df[FEATURES]
    y_clf = df["recommend_darkstore"]
    y_reg = df["opportunity_score"]

    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 1. Classification
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_clf, test_size=0.2, random_state=42)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # 2. Regression
    reg = GradientBoostingRegressor(n_estimators=100, random_state=42)
    reg.fit(X_scaled, y_reg)

    # 3. Clustering
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    df["cluster"] = kmeans.fit_predict(X_scaled)
    sorted_clusters = df.groupby("cluster")["opportunity_score"].mean().sort_values(ascending=False)
    labels = ["Prime", "High Potential", "Emerging", "Wait and Watch"]
    cluster_label_map = {int(idx): label for idx, label in zip(sorted_clusters.index, labels)}
    df["zone_tier"] = df["cluster"].map(cluster_label_map)

    # 4. PCA for 2D visualization
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    df["pca_x"] = X_pca[:, 0]
    df["pca_y"] = X_pca[:, 1]

    # Feature importance
    feat_importance = pd.DataFrame({
        "feature": FEATURES,
        "importance": clf.feature_importances_
    }).sort_values("importance", ascending=False)

    # Save enriched data
    conn = sqlite3.connect("data/darkstore.db")
    df.to_sql("zones_enriched", conn, if_exists="replace", index=False)
    feat_importance.to_sql("feature_importance", conn, if_exists="replace", index=False)
    conn.close()

    # Save models
    os.makedirs("models", exist_ok=True)
    with open("models/classifier.pkl", "wb") as f: pickle.dump(clf, f)
    with open("models/regressor.pkl", "wb") as f: pickle.dump(reg, f)
    with open("models/scaler.pkl", "wb") as f: pickle.dump(scaler, f)
    with open("models/kmeans.pkl", "wb") as f: pickle.dump(kmeans, f)
    with open("models/label_encoder.pkl", "wb") as f: pickle.dump(le, f)

    print("✅ 2D Models trained and saved!")

if __name__ == "__main__":
    train_models()
