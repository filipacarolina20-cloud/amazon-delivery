import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Amazon Delivery Performance",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Amazon Delivery Performance Dashboard")
st.markdown("**Logistics performance analysis based on 13,000+ deliveries**")
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

# ── Key Insights ──────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("💡 Key Insights")
st.markdown(f"""
- **{pct_on_time}%** of deliveries are completed within the average delivery time benchmark
- **Traffic level** is one of the strongest predictors of delivery delays
- **Vehicle type** significantly impacts delay rates — useful for fleet allocation decisions
- **Area type** (Urban vs. Metropolitian) shows different performance patterns
- These insights can support **real-time operational decisions**, such as route prioritization and vehicle reallocation
""")

st.markdown("---")
st.caption("Data Analysis Project | Dataset: Amazon Delivery Dataset (Kaggle) | Built with Python, Pandas, Matplotlib & Streamlit")
