# 🛒 Dark Store Site Intelligence Platform
### Quick Commerce Expansion Planner — Powered by ML & Dash

---

## 🌍 Real-Life Usage

This project solves an **actual problem** being tackled by:

| Company | How They Use It |
|---|---|
| **Blinkit (Zomato)** | Identifies new dark store locations before competitors |
| **Swiggy Instamart** | Scores zones by demand density & delivery feasibility |
| **Zepto** | Optimizes 10-minute delivery by minimizing last-mile distance |
| **BigBasket BB Now** | Prioritizes high-income, high-internet zones for expansion |
| **Dunzo / BlinkIt** | Balances real estate cost vs order volume potential |

---

## 🧱 Project Architecture

```
.
├── data/
│   ├── generate_data.py      # Realistic synthetic data for 10 Indian cities
│   └── darkstore.db          # SQLite database (zones + trends)
│
├── models/
│   ├── train.py              # ML training (RF Classifier + GB Regressor + KMeans)
│   ├── classifier.pkl        # Recommend YES/NO
│   ├── regressor.pkl         # Predict opportunity score
│   ├── scaler.pkl            # Feature scaler
│   └── kmeans.pkl            # Zone tier clustering
│
├── app.py                    # Dash dashboard (Interactive UI)
├── requirements.txt
└── README.md
```

---

## 🤖 ML Models Used

| Model | Purpose | Algorithm |
|---|---|---|
| **Classifier** | Should we open a dark store here? | Random Forest |
| **Regressor** | What is the opportunity score? | Gradient Boosting |
| **Clusterer** | Zone tier segmentation | KMeans (4 clusters) |
| **Visualizer** | 2D cluster plot | PCA |

---

## 📊 Features Analyzed (13 signals)

- Population density, Avg order value, Daily orders
- Competitor density, Delivery time, Internet penetration
- Real estate cost, Road connectivity, Demographics
- Weekend spike, Delivery rating, Income level

---

## 🚀 How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate data
python data/generate_data.py

# 3. Train ML models
python models/train.py

# 4. Launch dashboard
python app.py
```

---

## 📁 Dataset

Synthetic but realistic data generated using:
- Real Indian city coordinates
- Industry-standard quick commerce metrics
- Seasonal demand patterns
- Competitive density modeling
