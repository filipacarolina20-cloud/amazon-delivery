import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Logistics Performance Dashboard",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Logistics Performance & Scheduling Dashboard")
st.markdown("**Operational analysis and scheduling recommendations based on 43,000+ deliveries**")
st.markdown("---")

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("amazon_delivery.csv")
    df = df.dropna()
    return df

df = load_data()

# ── Feature engineering ───────────────────────────────────────────────────────
avg_delivery = df["Delivery_Time"].mean()
df["Status"] = df["Delivery_Time"].apply(
    lambda x: "Delayed" if x > avg_delivery else "On-Time"
)

# ── KPI Metrics ───────────────────────────────────────────────────────────────
total       = len(df)
on_time     = (df["Status"] == "On-Time").sum()
delayed     = (df["Status"] == "Delayed").sum()
pct_on_time = round(on_time / total * 100, 1)
avg_time    = round(avg_delivery, 1)

col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Total Deliveries",   f"{total:,}")
col2.metric("✅ On-Time",            f"{on_time:,}",  f"{pct_on_time}%")
col3.metric("⚠️ Delayed",           f"{delayed:,}",  f"-{100 - pct_on_time}%")
col4.metric("⏱️ Avg Delivery Time", f"{avg_time} min")

st.markdown("---")

# ── Chart 1 — On-Time vs Delayed ─────────────────────────────────────────────
st.subheader("📊 On-Time vs. Delayed Deliveries")

fig1, ax1 = plt.subplots(figsize=(4, 4))
ax1.pie(
    [on_time, delayed],
    labels=["On-Time", "Delayed"],
    colors=["#2ecc71", "#e74c3c"],
    autopct="%1.1f%%",
    startangle=90,
    wedgeprops={"edgecolor": "white", "linewidth": 2}
)
ax1.set_title("Delivery Status Distribution", fontsize=12, fontweight="bold")
st.pyplot(fig1)

# ── Chart 2 — Avg Delivery Time by Traffic ────────────────────────────────────
st.subheader("🚦 Average Delivery Time by Traffic Level")

traffic_avg = (
    df.groupby("Traffic")["Delivery_Time"]
    .mean().reset_index().sort_values("Delivery_Time")
)
color_map  = {"Low": "#2ecc71", "Medium": "#f39c12", "High": "#e74c3c", "Jam": "#8e44ad"}
bar_colors = [color_map.get(t, "#3498db") for t in traffic_avg["Traffic"]]

fig2, ax2 = plt.subplots(figsize=(7, 4))
bars = ax2.bar(traffic_avg["Traffic"], traffic_avg["Delivery_Time"],
               color=bar_colors, edgecolor="white", linewidth=1.5)
ax2.set_xlabel("Traffic Level", fontsize=11)
ax2.set_ylabel("Avg Delivery Time (min)", fontsize=11)
ax2.set_title("Average Delivery Time by Traffic Level", fontsize=13, fontweight="bold")
ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)
for bar, val in zip(bars, traffic_avg["Delivery_Time"]):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height()+0.5,
             f"{val:.1f} min", ha="center", fontweight="bold", fontsize=10)
st.pyplot(fig2)

# ── Chart 3 — Delay Rate by Vehicle Type ─────────────────────────────────────
st.subheader("🚗 Delay Rate by Vehicle Type")

vehicle_stats = (
    df.groupby("Vehicle")["Status"]
    .apply(lambda x: (x == "Delayed").sum() / len(x) * 100)
    .reset_index().rename(columns={"Status": "Delay_Rate"})
    .sort_values("Delay_Rate")
)
h_colors = ["#2ecc71" if v < 40 else "#f39c12" if v < 55 else "#e74c3c"
            for v in vehicle_stats["Delay_Rate"]]
fig3, ax3 = plt.subplots(figsize=(7, 4))
h_bars = ax3.barh(vehicle_stats["Vehicle"], vehicle_stats["Delay_Rate"],
                  color=h_colors, edgecolor="white", linewidth=1.5)
ax3.set_xlabel("Delay Rate (%)", fontsize=11)
ax3.set_title("Delay Rate by Vehicle Type", fontsize=13, fontweight="bold")
ax3.spines["top"].set_visible(False); ax3.spines["right"].set_visible(False)
for bar, val in zip(h_bars, vehicle_stats["Delay_Rate"]):
    ax3.text(val+0.3, bar.get_y()+bar.get_height()/2,
             f"{val:.1f}%", va="center", fontweight="bold", fontsize=10)
st.pyplot(fig3)

# ── Chart 4 — Avg Delivery Time by Area ──────────────────────────────────────
st.subheader("🗺️ Average Delivery Time by Area")

area_avg = (
    df.groupby("Area")["Delivery_Time"]
    .mean().reset_index().sort_values("Delivery_Time", ascending=False)
)
fig4, ax4 = plt.subplots(figsize=(7, 4))
ax4.barh(area_avg["Area"], area_avg["Delivery_Time"],
         color="#3498db", edgecolor="white", linewidth=1.5)
ax4.set_xlabel("Avg Delivery Time (min)", fontsize=11)
ax4.set_title("Average Delivery Time by Area Type", fontsize=13, fontweight="bold")
ax4.spines["top"].set_visible(False); ax4.spines["right"].set_visible(False)
for i, val in enumerate(area_avg["Delivery_Time"]):
    ax4.text(val+0.3, i, f"{val:.1f} min", va="center", fontweight="bold", fontsize=10)
st.pyplot(fig4)

# ── Interactive Table ─────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🔍 Explore the Data")

col_f1, col_f2 = st.columns(2)
with col_f1:
    traffic_filter = st.selectbox("Filter by Traffic Level:",
                                  ["All"] + sorted(df["Traffic"].unique().tolist()))
with col_f2:
    status_filter = st.selectbox("Filter by Status:", ["All", "On-Time", "Delayed"])

df_filtered = df.copy()
if traffic_filter != "All":
    df_filtered = df_filtered[df_filtered["Traffic"] == traffic_filter]
if status_filter != "All":
    df_filtered = df_filtered[df_filtered["Status"] == status_filter]

st.dataframe(
    df_filtered[["Order_ID","Delivery_Time","Traffic","Vehicle","Area","Weather","Status"]].head(20),
    use_container_width=True
)

# ══════════════════════════════════════════════════════════════════════════════
# ── OPERATIONAL RECOMMENDATIONS ENGINE ───────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("🧠 Operational Recommendations Engine")
st.markdown("*Simulate a delivery scenario and get data-driven scheduling recommendations*")

st.markdown("#### Set Current Conditions")

rec_col1, rec_col2, rec_col3 = st.columns(3)

with rec_col1:
    sel_traffic = st.selectbox("Traffic Level:",
                               ["Low", "Medium", "High", "Jam"])
with rec_col2:
    sel_area = st.selectbox("Delivery Area:",
                            sorted(df["Area"].dropna().unique().tolist()))
with rec_col3:
    sel_vehicle = st.selectbox("Current Vehicle:",
                               sorted(df["Vehicle"].dropna().unique().tolist()))

sel_weather = st.selectbox("Weather Condition:",
                           sorted(df["Weather"].dropna().unique().tolist()))

# ── Calculate expected delivery time based on selected conditions ─────────────
mask = (
    (df["Traffic"]  == sel_traffic)  &
    (df["Area"]     == sel_area)     &
    (df["Vehicle"]  == sel_vehicle)  &
    (df["Weather"]  == sel_weather)
)
filtered = df[mask]

if len(filtered) > 0:
    expected_time = round(filtered["Delivery_Time"].mean(), 1)
    delay_rate    = round((filtered["Status"] == "Delayed").sum() / len(filtered) * 100, 1)
    sample_size   = len(filtered)
else:
    # fallback — use traffic + area only
    mask2 = (df["Traffic"] == sel_traffic) & (df["Area"] == sel_area)
    filtered2 = df[mask2]
    if len(filtered2) > 0:
        expected_time = round(filtered2["Delivery_Time"].mean(), 1)
        delay_rate    = round((filtered2["Status"] == "Delayed").sum() / len(filtered2) * 100, 1)
        sample_size   = len(filtered2)
    else:
        expected_time = avg_time
        delay_rate    = round((1 - pct_on_time/100) * 100, 1)
        sample_size   = 0

# ── Risk level ────────────────────────────────────────────────────────────────
if delay_rate >= 60:
    risk_level = "🔴 HIGH RISK"
    risk_color = "#e74c3c"
elif delay_rate >= 40:
    risk_level = "🟡 MEDIUM RISK"
    risk_color = "#f39c12"
else:
    risk_level = "🟢 LOW RISK"
    risk_color = "#2ecc71"

# ── Display scenario summary ──────────────────────────────────────────────────
st.markdown("#### Scenario Analysis")

m1, m2, m3 = st.columns(3)
m1.metric("📍 Expected Delivery Time", f"{expected_time} min",
          f"{round(expected_time - avg_time, 1):+.1f} min vs. avg")
m2.metric("⚠️ Delay Risk",            f"{delay_rate}%")
m3.metric("📊 Based on",              f"{sample_size:,} similar deliveries")

st.markdown(f"**Route Risk Level: {risk_level}**")

# ── Recommendations ───────────────────────────────────────────────────────────
st.markdown("#### Scheduling Recommendations")

recommendations = []

# Traffic-based recommendations
if sel_traffic == "Jam":
    recommendations.append("🚛 **Reallocate to larger vehicle (van/truck)** — motorcycles and scooters underperform in jam conditions")
    recommendations.append("⏰ **Adjust SLA by +25 min** — communicate updated ETA to customer proactively")
    recommendations.append("🗺️ **Prioritize dispatch before peak congestion window** — schedule pickups in early morning or late evening")
elif sel_traffic == "High":
    recommendations.append("🔄 **Consider route reallocation** — explore alternative corridors to reduce exposure to high-traffic zones")
    recommendations.append("⏰ **Adjust SLA by +10–15 min** — buffer time recommended")
elif sel_traffic == "Medium":
    recommendations.append("✅ **Maintain current scheduling** — medium traffic is within acceptable performance range")
else:
    recommendations.append("✅ **Optimal dispatch window** — low traffic conditions support on-time delivery")

# Vehicle-based recommendations
if sel_vehicle == "bicycle":
    recommendations.append("🚲 **Limit bicycle dispatch to Urban areas only** — bicycles show highest delay rates in Metropolitan zones")
elif sel_vehicle == "motorcycle":
    if sel_traffic in ["High", "Jam"]:
        recommendations.append("🏍️ **Swap motorcycle for scooter or van** — motorcycles underperform under high congestion")
elif sel_vehicle == "electric_scooter":
    recommendations.append("⚡ **Electric scooter suitable for short Urban routes** — monitor battery range for Metropolitan deliveries")

# Area-based recommendations
if sel_area == "Metropolitian":
    recommendations.append("🏙️ **Metropolitan area detected** — assign higher-rated agents (rating ≥ 4.5) to improve performance")
    recommendations.append("📦 **Consider batch scheduling** — group nearby deliveries to reduce per-route time in dense zones")
else:
    recommendations.append("🏘️ **Urban area** — standard scheduling applies, no additional adjustments needed")

# Weather-based recommendations
if sel_weather in ["Stormy", "Sandstorms", "Fog"]:
    recommendations.append(f"🌩️ **Adverse weather ({sel_weather}) detected** — increase SLA by +15 min and notify dispatch team")
    recommendations.append("📋 **Activate weather contingency protocol** — prioritize covered vehicles and reduce load per agent")
elif sel_weather == "Windy":
    recommendations.append("💨 **Windy conditions** — avoid bicycle and electric scooter dispatch; prefer motorcycle or van")

# Overall risk recommendation
if delay_rate >= 60:
    recommendations.append("🚨 **High delay risk scenario** — escalate to operations manager before dispatch confirmation")

# Display recommendations
for rec in recommendations:
    st.markdown(f"- {rec}")

# ── Summary box ───────────────────────────────────────────────────────────────
st.markdown("#### Action Summary")
sla_adjustment = 0
if sel_traffic == "Jam":       sla_adjustment += 25
elif sel_traffic == "High":    sla_adjustment += 12
if sel_weather in ["Stormy", "Sandstorms", "Fog"]: sla_adjustment += 15
elif sel_weather == "Windy":   sla_adjustment += 5

best_vehicle = "Van" if sel_traffic in ["High","Jam"] and sel_area == "Metropolitian" \
               else "Motorcycle" if sel_traffic in ["Low","Medium"] \
               else sel_vehicle.title()

st.info(f"""
**Recommended SLA:** {avg_time + sla_adjustment:.0f} min ({f'+{sla_adjustment}' if sla_adjustment > 0 else '0'} min adjustment)
**Recommended Vehicle:** {best_vehicle}
**Dispatch Priority:** {'🔴 Delay — review conditions' if delay_rate >= 60 else '🟡 Proceed with caution' if delay_rate >= 40 else '🟢 Proceed as planned'}
""")

# ── Key Insights ──────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("💡 Key Insights")
st.markdown(f"""
- **{pct_on_time}%** of deliveries are completed within the average delivery time benchmark of {avg_time} min
- **Traffic level** is the strongest predictor of delivery delays — jam conditions add 25+ minutes on average
- **Vehicle type** significantly impacts delay rates and should be matched to route conditions
- **Metropolitan areas** consistently show longer delivery times and benefit from experienced agent allocation
- **Adverse weather** compounds existing delays — SLA adjustments are critical for customer experience
- The **Recommendations Engine** above translates these patterns into real-time scheduling decisions
""")

st.markdown("---")
st.caption("Logistics Performance & Scheduling Dashboard | Public delivery dataset (Kaggle) | Built with Python, Pandas, Matplotlib & Streamlit")
