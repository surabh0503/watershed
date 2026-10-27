import numpy as np
import pandas as pd

# Set random seed for reproducibility
np.random.seed(42)

# 1. Define Time Steps: 21 Water Years (2000-01 to 2020-21) starting June 1, 2000
weeks_per_year = 52
start_year = 2000
total_years = 21
total_weeks = total_years * weeks_per_year

dates = pd.date_range(start="2000-06-01", periods=total_weeks, freq="W-SUN")

# 2. Generate Realistic Inflows (High during monsoon weeks ~15 to 30, low otherwise)
weeks = np.tile(np.arange(1, 53), total_years)
base_inflow = 50 + 200 * np.exp(-((weeks - 22) ** 2) / 20)  # Peak around monsoon
noise = np.random.gamma(shape=2, scale=20, size=total_weeks)
inflow = base_inflow + noise
inflow = np.clip(inflow, 10, 3500)  # Mm3 per week during extreme floods

# 3. Initialize Storage and Parameters
# Ukai Capacity bounds (Mm3)
min_storage = 1500.0
max_storage = 7414.0
storage = np.zeros(total_weeks)
release = np.zeros(total_weeks)
evaporation = np.zeros(total_weeks)

# Initial storage at start of June 2000 (set to 4000 Mm3)
current_storage = 4000.0

for t in range(total_weeks):
    # Seasonality check for release (higher release in dry season for irrigation/supply, controlled during monsoon)
    week_of_year = weeks[t]

    # Evaporation loss (higher in summer months weeks 40-52)
    evap_rate = 30.0 if (week_of_year > 35 or week_of_year < 10) else 15.0
    evaporation[t] = evap_rate

    # Operating policy rule: Target release based on current storage and season
    if 15 <= week_of_year <= 30:  # Monsoon: strict flood control / holding water
        rel = 80.0 if current_storage < 6500 else 300.0
    else:  # Non-monsoon: steady irrigation and water supply release
        rel = 120.0 if current_storage > 3000 else 60.0

    # Apply mass balance: S_next = S_current + Inflow - Release - Evaporation
    next_storage = current_storage + inflow[t] - rel - evaporation[t]

    # Clamp storage between physical dead storage and full capacity
    if next_storage > max_storage:
        # Excess water spills out as uncontrolled overflow/release
        excess = next_storage - max_storage
        rel += excess
        next_storage = max_storage
    elif next_storage < min_storage:
        # Prevent going below dead storage
        deficit = min_storage - next_storage
        rel -= deficit
        next_storage = min_storage

    release[t] = max(rel, 10.0)
    storage[t] = current_storage
    current_storage = next_storage

# 4. Create DataFrame and Export to CSV
df_synthetic = pd.DataFrame(
    {
        "Week_Index": np.arange(1, total_weeks + 1),
        "Date": dates,
        "Water_Year": np.repeat(
            [f"{y}-{y+1}" for y in range(2000, 2021)], weeks_per_year
        ),
        "Week_Of_Year": weeks,
        "Inflow_Mm3": np.round(inflow, 2),
        "Release_Mm3": np.round(release, 2),
        "Evaporation_Mm3": np.round(evaporation, 2),
        "Storage_Mm3": np.round(storage, 2),
    }
)

df_synthetic.to_csv("ukai_weekly_simulation_data.csv", index=False)
print("Synthetic dataset generated successfully: ukai_weekly_simulation_data.csv")
print(df_synthetic.head())