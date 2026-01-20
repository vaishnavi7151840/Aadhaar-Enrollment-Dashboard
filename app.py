import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# keep analysis logic separate (from your notebook)
from model_logic import load_data, preprocess, get_age_cols, add_total, yearly_trend, monthly_age_trend, top_districts_monthly_trend

st.set_page_config(page_title="Aadhaar Enrollment Analysis", layout="wide")

def safe_to_datetime(s):
    # Handles formats like 01-09-2025
    return pd.to_datetime(s, errors="coerce", dayfirst=True)

st.title("Aadhaar Enrollment Analysis Dashboard")
st.caption("Filters: Date • State • District • Pincode | Metrics by Age Buckets")

st.sidebar.header("Upload")
uploaded = st.sidebar.file_uploader("Upload your dataset", type=["csv","xls","xlsx"])

if uploaded is None:
    st.info("Upload a dataset file to start.")
    st.stop()

df = load_data(uploaded)

df = preprocess(df)
if "date" not in df.columns or df["date"].isna().all():
    st.error("No valid 'date' values found in the dataset.")
    st.stop()

# Expected dimension columns
dim_cols = [c for c in ["state","district","pincode"] if c in df.columns]

age_cols = get_age_cols(df)

df["Year"] = df["date"].dt.year
df["Month"] = df["date"].dt.to_period("M").astype(str)

# Sidebar filters
st.sidebar.header("Filters")

# Date range filter
dmin = df["date"].min().date()
dmax = df["date"].max().date()
start, end = st.sidebar.date_input("Date range", (dmin, dmax))
df_f = df[(df["date"] >= pd.to_datetime(start)) & (df["date"] <= pd.to_datetime(end))].copy()

# Add total column after filtering
df_f = add_total(df_f, age_cols)

# State & district filters
if "state" in df_f.columns:
    states = sorted(df_f["state"].dropna().unique().tolist())
    selected_states = st.sidebar.multiselect("State", states, default=states[: min(5, len(states))])
    if selected_states:
        df_f = df_f[df_f["state"].isin(selected_states)]

if "district" in df_f.columns:
    districts = sorted(df_f["district"].dropna().unique().tolist())
    selected_districts = st.sidebar.multiselect("District", districts, default=districts[: min(10, len(districts))])
    if selected_districts:
        df_f = df_f[df_f["district"].isin(selected_districts)]

# Optional pincode filter via text box (good when many pincodes)
if "pincode" in df_f.columns:
    pin_text = st.sidebar.text_input("Pincode(s) (optional, comma-separated)", "")
    if pin_text.strip():
        try:
            pins = [int(x.strip()) for x in pin_text.split(",") if x.strip()]
            df_f = df_f[df_f["pincode"].isin(pins)]
        except Exception:
            st.sidebar.warning("Invalid pincodes. Example: 411001, 400001")

total_enrollments = int(df_f["total"].sum()) if len(df_f) else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Rows (filtered)", f"{len(df_f):,}")
k2.metric("Total (all ages)", f"{total_enrollments:,}")
if "state" in df_f.columns:
    k3.metric("States", f"{df_f['state'].nunique():,}")
else:
    k3.metric("States", "—")
if "district" in df_f.columns:
    k4.metric("Districts", f"{df_f['district'].nunique():,}")
else:
    k4.metric("Districts", "—")

tab1, tab2, tab3 = st.tabs(["Preview", "Charts", "Downloads"])

with tab1:
    st.subheader("Data Preview")
    st.dataframe(df_f.head(300), use_container_width=True)

with tab2:
  st.divider()
st.subheader("Graphs (Easy)")

# 1) Month-wise Total (सबसे easy graph)
st.markdown("### 1) Month-wise Total Enrollment")
df_f["Month"] = df_f["date"].dt.to_period("M").astype(str)
month_total = df_f.groupby("Month")["total"].sum().sort_index()

fig, ax = plt.subplots()
ax.bar(month_total.index.astype(str), month_total.values)
ax.set_xlabel("Month")
ax.set_ylabel("Total Enrollment")
ax.tick_params(axis="x", rotation=45)
st.pyplot(fig)

# 2) Age group share (clear comparison)
if all(col in df_f.columns for col in ["age_0_5", "age_5_17", "age_18_greater"]):
    st.markdown("### 2) Age Group Total (0–5 vs 5–17 vs 18+)")
    age_totals = df_f[["age_0_5", "age_5_17", "age_18_greater"]].sum()

    fig2, ax2 = plt.subplots()
    ax2.bar(age_totals.index, age_totals.values)
    ax2.set_xlabel("Age Group")
    ax2.set_ylabel("Total")
    st.pyplot(fig2)

# 3) Top 5 Districts (less confusing than top 10)
if "district" in df_f.columns:
    st.markdown("### 3) Top 5 Districts by Total")
    top5 = df_f.groupby("district")["total"].sum().sort_values(ascending=False).head(5)

    fig3, ax3 = plt.subplots()
    ax3.bar(top5.index.astype(str), top5.values)
    ax3.set_xlabel("District")
    ax3.set_ylabel("Total Enrollment")
    ax3.tick_params(axis="x", rotation=30)
    st.pyplot(fig3)

 
    

with tab3:
    st.subheader("Download filtered data")
    csv = df_f.drop(columns=["total"], errors="ignore").to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", data=csv, file_name="aadhaar_filtered.csv", mime="text/csv")

    st.subheader("Download summary tables")
    # Year summary
    year_sum = df_f.groupby("Year")[age_cols + ["total"]].sum().reset_index()
    st.dataframe(year_sum, use_container_width=True)
    csv2 = year_sum.to_csv(index=False).encode("utf-8")
    st.download_button("Download Year Summary CSV", data=csv2, file_name="aadhaar_year_summary.csv", mime="text/csv")



