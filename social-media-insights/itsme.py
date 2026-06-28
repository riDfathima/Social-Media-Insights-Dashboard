# Generated from: itsme.ipynb
# Converted at: 2026-06-28T09:54:42.120Z
# Next step (optional): refactor into modules & generate tests with RunCell
# Quick start: pip install runcell

dashboard_code = '''
import streamlit as st
import pandas as pd
import plotly.express as px
import io
from openpyxl import Workbook

st.set_page_config(page_title="Social Analytics Dashboard", layout="wide")
st.title("Social Analytics Dashboard")
st.markdown("Upload any social media CSV and get instant insights.")

uploaded = st.sidebar.file_uploader("Upload your own CSV", type="csv")

if uploaded:
    df = pd.read_csv(uploaded)
    st.sidebar.success("Your file loaded!")
    st.sidebar.markdown("**Columns found:**")
    st.sidebar.write(list(df.columns))
else:
    df = pd.read_csv("pseudo_facebook_clean.csv")
    st.sidebar.info("Using sample dataset")

# ── Detect dataset type ──
is_pseudo_fb = "age" in df.columns and "friend_count" in df.columns
is_social_usage = "App" in df.columns and "Daily_Minutes_Spent" in df.columns

# ══════════════════════════════════════════
# LAYOUT A — pseudo_facebook.csv
# ══════════════════════════════════════════
if is_pseudo_fb:

    df = df[df["age"].between(13, 113)].copy()
    numeric_cols = [c for c in ["friend_count","likes","likes_received",
                    "mobile_likes","www_likes","tenure"] if c in df.columns]
    df[numeric_cols] = df[numeric_cols].fillna(0)
    df["age_group"] = pd.cut(df["age"],
        bins=[13,17,24,34,44,54,64,113],
        labels=["13-17","18-24","25-34","35-44","45-54","55-64","65+"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Users", f"{len(df):,}")
    col2.metric("Avg Friend Count", f"{df['friend_count'].mean():.1f}")
    mobile_pct = df["mobile_likes"].sum()/df["likes"].sum()*100 if df["likes"].sum()>0 else 0
    col3.metric("Mobile Likes %", f"{mobile_pct:.1f}%")
    col4.metric("Avg Likes Received", f"{df['likes_received'].mean():.1f}")

    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Avg Friends by Age Group")
        age_data = df.groupby("age_group", observed=True)["friend_count"].mean().reset_index()
        fig1 = px.bar(age_data, x="age_group", y="friend_count",
                      color_discrete_sequence=["#9B5CF6"])
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.subheader("Mobile vs Web Likes")
        platform = pd.DataFrame({
            "Platform": ["Mobile", "Web"],
            "Likes": [df["mobile_likes"].sum(), df["www_likes"].sum()]
        })
        fig2 = px.pie(platform, names="Platform", values="Likes",
                      color_discrete_sequence=["#E040A0","#9B5CF6"])
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Likes Received by Gender")
        gen = df[df["gender"].isin(["male","female"])]
        fig3 = px.box(gen, x="gender", y="likes_received",
                      color="gender",
                      color_discrete_map={"female":"#E040A0","male":"#9B5CF6"})
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.subheader("Friends vs Tenure")
        sample = df.sample(min(2000, len(df)), random_state=42)
        fig4 = px.scatter(sample, x="tenure", y="friend_count",
                          color="gender",
                          color_discrete_map={"female":"#E040A0","male":"#9B5CF6"},
                          opacity=0.4)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")
    st.subheader("Key Findings")
    st.markdown("""
    - **25-34 age group** has the highest average friend count — best target for organic reach
    - **Mobile drives the majority of likes** — content should be designed mobile-first
    - **Female users receive more likes on average** — relevant for creator targeting
    - **Tenure correlates with connections** — long-term users are your most networked audience
    """)

# ══════════════════════════════════════════
# LAYOUT B — social_media_usage.csv
# ══════════════════════════════════════════
elif is_social_usage:

    df["Daily_Minutes_Spent"] = pd.to_numeric(df["Daily_Minutes_Spent"], errors="coerce").fillna(0)
    df["Likes_Per_Day"]       = pd.to_numeric(df["Likes_Per_Day"],       errors="coerce").fillna(0)
    df["Posts_Per_Day"]       = pd.to_numeric(df["Posts_Per_Day"],       errors="coerce").fillna(0)
    df["Follows_Per_Day"]     = pd.to_numeric(df["Follows_Per_Day"],     errors="coerce").fillna(0)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Users",        f"{len(df):,}")
    col2.metric("Avg Mins/Day",       f"{df['Daily_Minutes_Spent'].mean():.1f}")
    col3.metric("Avg Likes/Day",      f"{df['Likes_Per_Day'].mean():.1f}")
    col4.metric("Avg Posts/Day",      f"{df['Posts_Per_Day'].mean():.1f}")

    st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Avg Time Spent by App")
        app_time = df.groupby("App")["Daily_Minutes_Spent"].mean().reset_index().sort_values("Daily_Minutes_Spent", ascending=False)
        fig1 = px.bar(app_time, x="App", y="Daily_Minutes_Spent",
                      color="App",
                      color_discrete_sequence=px.colors.sequential.Purples_r,
                      labels={"Daily_Minutes_Spent":"Avg Minutes/Day"})
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.subheader("Avg Likes Per Day by App")
        app_likes = df.groupby("App")["Likes_Per_Day"].mean().reset_index().sort_values("Likes_Per_Day", ascending=False)
        fig2 = px.bar(app_likes, x="App", y="Likes_Per_Day",
                      color="App",
                      color_discrete_sequence=px.colors.sequential.RdPu_r,
                      labels={"Likes_Per_Day":"Avg Likes/Day"})
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Posts vs Likes per Day")
        fig3 = px.scatter(df, x="Posts_Per_Day", y="Likes_Per_Day",
                          color="App",
                          opacity=0.6,
                          color_discrete_sequence=px.colors.qualitative.Vivid,
                          labels={"Posts_Per_Day":"Posts/Day",
                                  "Likes_Per_Day":"Likes/Day"})
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.subheader("Share of Time Spent by App")
        app_share = df.groupby("App")["Daily_Minutes_Spent"].sum().reset_index()
        fig4 = px.pie(app_share, names="App", values="Daily_Minutes_Spent",
                      color_discrete_sequence=px.colors.sequential.Purples_r)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")

    # App comparison table
    st.subheader("App by App Breakdown")
    summary = df.groupby("App").agg(
        Users=("User_ID","count"),
        Avg_Mins=("Daily_Minutes_Spent","mean"),
        Avg_Posts=("Posts_Per_Day","mean"),
        Avg_Likes=("Likes_Per_Day","mean"),
        Avg_Follows=("Follows_Per_Day","mean")
    ).round(1).reset_index()
    st.dataframe(summary, use_container_width=True)

    st.markdown("---")
    st.subheader("Key Findings")

    top_time_app  = app_time.iloc[0]["App"]
    top_likes_app = app_likes.iloc[0]["App"]
    st.markdown(f"""
    - **{top_time_app}** gets the most daily time from users on average
    - **{top_likes_app}** generates the most likes per day — highest engagement platform
    - More posts per day does not always mean more likes — quality beats quantity
    - Follow behaviour varies significantly across platforms
    """)

# ══════════════════════════════════════════
# FALLBACK — unknown CSV
# ══════════════════════════════════════════
else:
    st.warning("Showing a raw preview — column names did not match a known format.")
    st.dataframe(df.head(50), use_container_width=True)
    st.info("Expected columns: age, gender, friend_count, likes, mobile_likes, www_likes  —  OR  —  App, Daily_Minutes_Spent, Posts_Per_Day, Likes_Per_Day, Follows_Per_Day")

# ══════════════════════════════════════════
# DOWNLOAD — works for any layout
# ══════════════════════════════════════════
st.markdown("---")
st.subheader("Download Your Report")

def generate_excel(df):
    wb = Workbook()
    ws = wb.active
    ws.title = "Summary"
    ws.append(["Metric", "Value"])
    ws.append(["Total Rows", len(df)])
    for col in df.select_dtypes(include="number").columns:
        ws.append([f"Avg {col}", round(df[col].mean(), 2)])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()

st.download_button(
    label="Download Excel Report",
    data=generate_excel(df),
    file_name="social_analytics_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
'''

with open("dashboard.py", "w") as f:
    f.write(dashboard_code)

print("dashboard.py updated ✅")

import subprocess, sys, time
proc = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", "dashboard.py",
     "--server.port=8501", "--server.headless=true"]
)
time.sleep(4)
print("Open http://localhost:8501")