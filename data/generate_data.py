import pandas as pd
import numpy as np
import sqlite3
import os

np.random.seed(42)

# Real Indian cities with approximate lat/lon
CITIES = {
    "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.6139, 77.2090),
    "Bangalore": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Chennai": (13.0827, 80.2707),
    "Pune": (18.5204, 73.8567),
    "Kolkata": (22.5726, 88.3639),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur": (26.9124, 75.7873),
    "Surat": (21.1702, 72.8311),
}

# Zones per city
ZONES_PER_CITY = {
    "Mumbai": ["Andheri", "Bandra", "Dadar", "Kurla", "Thane", "Borivali", "Malad", "Goregaon"],
    "Delhi": ["Connaught Place", "Lajpat Nagar", "Rohini", "Dwarka", "Karol Bagh", "Saket", "Janakpuri", "Pitampura"],
    "Bangalore": ["Koramangala", "Indiranagar", "Whitefield", "HSR Layout", "JP Nagar", "Marathahalli", "Hebbal", "Jayanagar"],
    "Hyderabad": ["Banjara Hills", "Madhapur", "Gachibowli", "Secunderabad", "Kukatpally", "Ameerpet", "Jubilee Hills", "Kondapur"],
    "Chennai": ["Anna Nagar", "T. Nagar", "Adyar", "Velachery", "Tambaram", "Porur", "Chromepet", "Nungambakkam"],
    "Pune": ["Koregaon Park", "Kothrud", "Wakad", "Hadapsar", "Viman Nagar", "Aundh", "Baner", "Hinjewadi"],
    "Kolkata": ["Salt Lake", "Park Street", "Dum Dum", "Tollygunge", "Ballygunge", "Howrah", "Behala", "Rajarhat"],
    "Ahmedabad": ["SG Highway", "Navrangpura", "Vastrapur", "Satellite", "Bopal", "Maninagar", "Gota", "Chandkheda"],
    "Jaipur": ["Malviya Nagar", "Vaishali Nagar", "Mansarovar", "C-Scheme", "Jagatpura", "Sodala", "Tonk Road", "Sanganer"],
    "Surat": ["Adajan", "Vesu", "Piplod", "Katargam", "Udhna", "Varachha", "Althan", "City Light"],
}

records = []
zone_id = 1

for city, (base_lat, base_lon) in CITIES.items():
    zones = ZONES_PER_CITY[city]
    for zone in zones:
        lat = base_lat + np.random.uniform(-0.15, 0.15)
        lon = base_lon + np.random.uniform(-0.15, 0.15)

        # Simulate realistic features
        population_density = np.random.randint(5000, 80000)   # per sq km
        avg_order_value = np.random.randint(250, 950)          # INR
        daily_orders = np.random.randint(100, 3500)
        competitor_count = np.random.randint(0, 8)
        delivery_time_min = np.random.randint(8, 45)
        income_level = np.random.choice(["Low", "Middle", "Upper-Middle", "High"],
                                         p=[0.15, 0.40, 0.30, 0.15])
        internet_penetration = np.random.uniform(0.45, 0.97)
        has_existing_darkstore = np.random.choice([0, 1], p=[0.65, 0.35])
        real_estate_cost = np.random.randint(30, 350)          # INR per sqft per month
        road_connectivity_score = np.random.uniform(0.3, 1.0)
        young_population_pct = np.random.uniform(0.20, 0.65)
        working_professionals_pct = np.random.uniform(0.15, 0.70)
        weekend_order_spike = np.random.uniform(1.1, 2.5)
        avg_delivery_rating = np.random.uniform(3.2, 4.9)
        monthly_revenue_potential = daily_orders * avg_order_value * 30 * np.random.uniform(0.08, 0.15)

        # Composite opportunity score (what we want to predict/rank)
        score = (
            (population_density / 80000) * 25 +
            (daily_orders / 3500) * 30 +
            (1 - competitor_count / 8) * 15 +
            (internet_penetration) * 10 +
            (road_connectivity_score) * 10 +
            (young_population_pct) * 10
        )
        score = round(min(score + np.random.uniform(-5, 5), 100), 2)

        # Recommend dark store
        recommend = 1 if (score > 55 and has_existing_darkstore == 0) else 0

        records.append({
            "zone_id": zone_id,
            "city": city,
            "zone": zone,
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "population_density": population_density,
            "avg_order_value_inr": avg_order_value,
            "daily_orders": daily_orders,
            "competitor_count": competitor_count,
            "delivery_time_min": delivery_time_min,
            "income_level": income_level,
            "internet_penetration": round(internet_penetration, 3),
            "has_existing_darkstore": has_existing_darkstore,
            "real_estate_cost_sqft": real_estate_cost,
            "road_connectivity_score": round(road_connectivity_score, 3),
            "young_population_pct": round(young_population_pct, 3),
            "working_professionals_pct": round(working_professionals_pct, 3),
            "weekend_order_spike": round(weekend_order_spike, 2),
            "avg_delivery_rating": round(avg_delivery_rating, 2),
            "monthly_revenue_potential_inr": round(monthly_revenue_potential, 0),
            "opportunity_score": score,
            "recommend_darkstore": recommend,
        })
        zone_id += 1

df = pd.DataFrame(records)

# Save CSV
os.makedirs("data", exist_ok=True)
df.to_csv("data/zones.csv", index=False)

# Save to SQLite
conn = sqlite3.connect("data/darkstore.db")
df.to_sql("zones", conn, if_exists="replace", index=False)

# Monthly trend table
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
trend_records = []
for city in CITIES:
    base = np.random.randint(8000, 50000)
    for i, month in enumerate(months):
        seasonal = 1 + 0.3 * np.sin((i - 2) * np.pi / 6)
        orders = int(base * seasonal * np.random.uniform(0.95, 1.05))
        trend_records.append({"city": city, "month": month, "month_num": i+1, "total_orders": orders})

trend_df = pd.DataFrame(trend_records)
trend_df.to_sql("monthly_trends", conn, if_exists="replace", index=False)
conn.close()

print(f"✅ Generated {len(df)} zone records across {len(CITIES)} cities")
print(df.head(3))
