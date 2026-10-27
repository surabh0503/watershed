import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 1. Set seed for reproducible synthetic dataset
np.random.seed(42)

weeks_per_year = 52
total_years = 21
total_weeks = total_years * weeks_per_year
dates = pd.date_range(start="2000-06-01", periods=total_weeks, freq="W-SUN")

# 2. Simulate Hydrological Inflows & Releases
weeks = np.tile(np.arange(1, 53), total_years)
base_inflow = 50 + 200 * np.exp(-((weeks - 22) ** 2) / 20)
noise = np.random.gamma(shape=2, scale=20, size=total_weeks)
inflow = np.clip(base_inflow + noise, 10, 3500)

min_storage = 1500.0  # Dead Storage Capacity
max_storage = 7414.0  # Full Reservoir Level (FRL)
storage = np.zeros(total_weeks)
release = np.zeros(total_weeks)
evaporation = np.zeros(total_weeks)

current_storage = 4000.0

for t in range(total_weeks):
    week_of_year = weeks[t]
    evap_rate = 30.0 if (week_of_year > 35 or week_of_year < 10) else 15.0
    evaporation[t] = evap_rate

    if 15 <= week_of_year <= 30:  # Monsoon season rule
        rel = 80.0 if current_storage < 6500 else 300.0
    else:  # Dry season rule
        rel = 120.0 if current_storage > 3000 else 60.0

    # Weekly Continuity Mass Balance: S(t+1) = S(t) + Inflow - Outflow - Evaporation
    next_storage = current_storage + inflow[t] - rel - evaporation[t]

    if next_storage > max_storage:
        excess = next_storage - max_storage
        rel += excess
        next_storage = max_storage
    elif next_storage < min_storage:
        deficit = min_storage - next_storage
        rel -= deficit
        next_storage = min_storage

    release[t] = max(rel, 10.0)
    storage[t] = current_storage
    current_storage = next_storage

df = pd.DataFrame(
    {
        "Date": dates,
        "Inflow_Mm3": inflow,
        "Release_Mm3": release,
        "Storage_Mm3": storage,
    }
)

# 3. Create High-Resolution Figure
fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(12, 7), sharex=True, gridspec_kw={"height_ratios": [2, 1.2]}
)

# Top Panel: Storage Trajectory
ax1.plot(
    df["Date"],
    df["Storage_Mm3"],
    color="#1f77b4",
    linewidth=1.2,
    label="Simulated Storage ($Mm^3$)",
)
ax1.axhline(
    y=7414,
    color="red",
    linestyle="--",
    linewidth=1.2,
    label="Full Reservoir Level (FRL = 7414 $Mm^3$)",
)
ax1.axhline(
    y=1500,
    color="black",
    linestyle=":",
    linewidth=1.2,
    label="Dead Storage Level (1500 $Mm^3$)",
)
ax1.set_ylabel("Storage ($Mm^3$)", fontsize=11, fontweight="bold")
ax1.set_title(
    "Ukai Reservoir Baseline Weekly Mass-Balance Simulation (2000–2021)",
    fontsize=13,
    fontweight="bold",
    pad=12,
)
ax1.legend(loc="upper right", frameon=True)
ax1.grid(True, linestyle=":", alpha=0.6)

# Bottom Panel: Inflow vs Outflow Dynamics
ax2.plot(
    df["Date"],
    df["Inflow_Mm3"],
    color="#2ca02c",
    linewidth=0.8,
    alpha=0.85,
    label="Inflow ($Mm^3$/week)",
)
ax2.plot(
    df["Date"],
    df["Release_Mm3"],
    color="#ff7f0e",
    linewidth=0.8,
    alpha=0.85,
    label="Release / Outflow ($Mm^3$/week)",
)
ax2.set_ylabel("Flow Rate ($Mm^3$/week)", fontsize=11, fontweight="bold")
ax2.set_xlabel("Water Year", fontsize=11, fontweight="bold")
ax2.legend(loc="upper right", frameon=True)
ax2.grid(True, linestyle=":", alpha=0.6)

plt.tight_layout()
plt.savefig("ukai_baseline_simulation.png", dpi=300)
plt.show()