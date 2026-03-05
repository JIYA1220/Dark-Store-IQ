<div align="center">

# Dark Store IQ — Site Intelligence & Expansion Analytics

### A Production-Grade, End-to-End Location Intelligence System for Quick Commerce

**Multi-City Zone Database · ML Scoring (0–100) · Open/No-Open Recommendations · Tier Segmentation (KMeans) · Geospatial Map · Trends · Zone Comparator · Exportable Data Vault · Printable Executive Report · Interactive Dash UI**

<br/>

[Quick Start](#quick-start) &nbsp;·&nbsp; [Key Results](#key-results) &nbsp;·&nbsp; [Architecture](#architecture) &nbsp;·&nbsp; [Tech Stack](#tech-stack) &nbsp;·&nbsp; [Project Structure](#project-structure) &nbsp;·&nbsp; [Dashboard Pages](#dashboard-pages) &nbsp;·&nbsp; [ML Deep Dive](#ml-deep-dive) &nbsp;·&nbsp; [Troubleshooting](#troubleshooting)

---

</div>

## Overview

**Business Question:** *Where should a quick-commerce company open its next dark store — and how confident are we?*

Dark Store IQ is an end-to-end analytics + ML application that generates a market dataset, trains models, and launches a **decision-grade dashboard** for expansion planning. It helps teams evaluate zones using a blend of demand signals, operational feasibility metrics, competitive pressure, and socioeconomic indicators.

This is not just a UI—this repo includes:
- a **SQLite “analytics warehouse”**
- a **model training pipeline** that exports reusable artifacts (`.pkl`)
- a **Dash dashboard** with multiple decision workflows (map, predictor, compare, executive report)

---

## Key Results

<div align="center">

| Metric | What You Get |
|:---|:---:|
| Output | **Open / Don’t open recommendation** + **Opportunity Score (0–100)** |
| ML Models | **Random Forest (classifier)** · **Gradient Boosting (regressor)** |
| Segmentation | **KMeans (4 tiers)** + PCA-based 2D visual segmentation |
| Decision Workflows | Map · Data Vault · AI Predictor · Trends · ML Insights · Zone Compare · Executive Report |
| Exports | Filtered CSV export + print-ready report pages |

</div>

> Note: This project generates **synthetic but realistic** quick-commerce market data (so it runs immediately without private company data).

---

## Architecture

```text
+---------------------------------------------------------------------+
|                         DATA + MODEL ARTIFACTS                       |
|   Synthetic Zone Data (Cities)  ·  Trends  ·  Feature Importance     |
|                SQLite Warehouse: data/darkstore.db                   |
+-------------------------------+-------------------------------------+
                                |
                                v
                +------------------------------+
                | Stage 01 — Data Generation   |
                | - Synthetic zone-level data  |
                | - Monthly trends             |
                | - Writes SQLite tables       |
                +---------------+--------------+
                                |
                                v
                +------------------------------+
                | Stage 02 — ML Training       |
                | - Feature scaling            |
                | - Classifier (RF)            |
                | - Regressor (GB)             |
                | - Clustering (KMeans)        |
                | - PCA projection             |
                | - Exports .pkl artifacts     |
                +---------------+--------------+
                                |
                                v
                +------------------------------+
                | Stage 03 — Dash Application  |
                | - Map + tiers                |
                | - AI predictor simulation    |
                | - Trends + insights          |
                | - Compare zones + pinning    |
                | - Executive report view      |
                +------------------------------+
```

---

## Tech Stack

<div align="center">

| Layer | Technology | Purpose |
|:---|:---|:---|
| Language | Python | Core logic |
| UI / App | Dash + Dash Bootstrap Components | Interactive web dashboard |
| Charts | Plotly | KPIs, trends, radar, map visualizations |
| Data | SQLite + Pandas | Zone tables, trend tables, feature importance |
| ML | Scikit-learn | Classification, regression, clustering, scaling |
| Serving (optional) | Gunicorn | Production deployment |

</div>

---

## Quick Start

### Prerequisites
- Python **3.9+**
- pip

### 1) Install
```bash
pip install -r requirements.txt
```

### 2) Generate the database
Creates/updates the SQLite warehouse at `data/darkstore.db`.

```bash
python data/generate_data.py
```

### 3) Train models
Creates/updates the model artifacts in `models/`:

```bash
python models/train.py
```

### 4) Launch the dashboard
```bash
python app.py
```

Open: **http://127.0.0.1:8050**

---

## Project Structure

```text
Dark-Store-IQ/
|
+-- data/
|   +-- generate_data.py              <- Synthetic data generator
|   +-- darkstore.db                  <- SQLite warehouse (generated)
|
+-- models/
|   +-- train.py                      <- ML training pipeline
|   +-- classifier.pkl                <- Random Forest classifier
|   +-- regressor.pkl                 <- Gradient Boosting regressor
|   +-- scaler.pkl                    <- Feature scaler
|   +-- label_encoder.pkl             <- Encoder for predictor input
|   +-- kmeans.pkl                    <- 4-tier segmentation model
|
+-- app.py                            <- Dash app (UI + callbacks)
+-- requirements.txt
+-- README.md
```

---

## Dashboard Pages

### 1) Overview
- Executive KPIs (zones, recommendations, avg score, order volume)
- Top zones ranking
- Tier distribution

### 2) Site Map (Geospatial)
- Zone markers sized by opportunity score
- Colored by tier classification (Prime / High Potential / Emerging / Wait & Watch)

### 3) Data Vault
- Filtered table view for zones
- CSV export (filtered)

### 4) AI Predictor (Simulation)
Enter key assumptions (population density, AOV, daily orders, rent, income band) and get:
- **RECOMMENDED / NOT RECOMMENDED**
- confidence score (probability)
- opportunity score gauge

### 5) Trends
- Monthly city-level trend lines (order volume)

### 6) ML Insights
- Feature importance chart
- PCA projection + tier visualization

### 7) Zone Compare
- Side-by-side KPIs for two zones
- Radar chart comparison
- Pin favorite zones locally (browser storage)

### 8) Executive Report
- Top 5 strategic sites
- Estimated investment + ROI logic
- Print-friendly layout for stakeholder sharing

---

## ML Deep Dive

### Models
- **Classifier**: Random Forest → predicts whether a zone should host a dark store
- **Regressor**: Gradient Boosting → predicts an opportunity score (0–100)
- **Clusterer**: KMeans (4 clusters) → assigns zone tiers
- **PCA**: used for 2D visualization of segmentation

### Feature Inputs (high-level)
The system uses demand, competition, operations, and demographic signals, such as:
- population density, daily orders, avg order value
- competitor density, road connectivity
- delivery rating, delivery time
- internet penetration
- real-estate cost
- income band / demographics
- weekend spikes + trend patterns

---

## “Real-World” Use Cases

This kind of system mirrors how quick-commerce operators evaluate expansion:
- **identify high-demand clusters**
- **avoid saturated competitor-heavy zones**
- **balance rental cost vs. revenue potential**
- **optimize last-mile feasibility by city/zone profile**

---

## Troubleshooting

### App shows: “Data missing.”
This means the app couldn’t load the SQLite DB or required tables.

Fix:
```bash
python data/generate_data.py
python models/train.py
python app.py
```

### Missing model files in `models/`
Run:
```bash
python models/train.py
```

### Port already in use
Change the port in `app.py`:
```python
app.run(debug=False, port=8051)
```

---

## Notes / Production Improvements (Optional)

If you want to take this from “project” to “portfolio-grade production”:
- add a `.github/workflows/ci.yml` for lint + smoke test
- add `pytest` tests for DB schema + model artifact presence
- add a `Dockerfile` + `docker-compose.yml`
- add a real `src/` package structure and config management

---

## Connect

Built by **Jiya**

- GitHub: https://github.com/JIYA1220
- LinkedIn:[ www.linkedin.com/in/jiya-sharma-394565338](https://www.linkedin.com/in/jiya-sharma-394565338)

---

### If this project helped you
Consider starring the repo — it helps others find it.
