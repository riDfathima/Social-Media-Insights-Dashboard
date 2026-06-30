# Generated from: dashboard.ipynb
# Converted at: 2026-06-28T10:05:13.488Z
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
def norm_col(name):
    return str(name).strip().lower().replace(" ", "_").replace("-", "_")

column_lookup = {norm_col(c): c for c in df.columns}

def col(*names):
    for name in names:
        found = column_lookup.get(norm_col(name))
        if found is not None:
            return found
    return None

is_pseudo_fb = "age" in df.columns and "friend_count" in df.columns
is_social_usage = "App" in df.columns and "Daily_Minutes_Spent" in df.columns
tweet_text_col = col("text", "tweet_text", "full_text", "content")
tweet_url_col = col("tweet_url", "status_url", "url", "link")
tweet_author_col = col("author_username", "username", "screen_name", "handle", "author")
tweet_like_col = col("like_count", "likes", "favorite_count")
tweet_reply_col = col("reply_count", "replies", "comments")
tweet_repost_col = col("retweet_count", "repost_count", "shares")
tweet_quote_col = col("quote_count", "quotes")
tweet_impression_col = col("impression_count", "impressions", "views", "view_count")
tweet_date_col = col("created_at", "published_at", "date", "timestamp")
is_tweetclaw_export = tweet_text_col is not None and (tweet_url_col is not None or tweet_author_col is not None)

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
# LAYOUT C — TweetClaw-style X/Twitter export
# ══════════════════════════════════════════
elif is_tweetclaw_export:

    work = df.copy()
    for metric_col in [tweet_like_col, tweet_reply_col, tweet_repost_col, tweet_quote_col, tweet_impression_col]:
        if metric_col is not None:
            work[metric_col] = pd.to_numeric(work[metric_col], errors="coerce").fillna(0)

    engagement_parts = [c for c in [tweet_like_col, tweet_reply_col, tweet_repost_col, tweet_quote_col] if c is not None]
    work["Engagement"] = work[engagement_parts].sum(axis=1) if engagement_parts else 0
    author_label = tweet_author_col or "Author"
    if tweet_author_col is None:
        work[author_label] = "unknown"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Posts", f"{len(work):,}")
    col2.metric("Unique Authors", f"{work[author_label].nunique():,}")
    col3.metric("Total Engagement", f"{int(work['Engagement'].sum()):,}")
    if tweet_impression_col is not None:
        col4.metric("Avg Views", f"{work[tweet_impression_col].mean():.1f}")
    else:
        col4.metric("Avg Engagement", f"{work['Engagement'].mean():.1f}")

    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Top Authors by Engagement")
        author_engagement = work.groupby(author_label)["Engagement"].sum().reset_index().sort_values("Engagement", ascending=False).head(10)
        fig1 = px.bar(author_engagement, x=author_label, y="Engagement",
                      color_discrete_sequence=["#9B5CF6"])
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.subheader("Engagement Distribution")
        fig2 = px.histogram(work, x="Engagement", nbins=20,
                            color_discrete_sequence=["#E040A0"])
        st.plotly_chart(fig2, use_container_width=True)

    if tweet_impression_col is not None and engagement_parts:
        c3, c4 = st.columns(2)
        with c3:
            st.subheader("Views vs Engagement")
            fig3 = px.scatter(work, x=tweet_impression_col, y="Engagement",
                              color=author_label,
                              opacity=0.7,
                              labels={tweet_impression_col: "Views"})
            st.plotly_chart(fig3, use_container_width=True)

        with c4:
            st.subheader("Top Posts")
            preview_cols = [c for c in [tweet_author_col, tweet_text_col, tweet_url_col, tweet_date_col, "Engagement", tweet_impression_col] if c is not None]
            st.dataframe(work.sort_values("Engagement", ascending=False)[preview_cols].head(10), use_container_width=True)
    else:
        st.subheader("Top Posts")
        preview_cols = [c for c in [tweet_author_col, tweet_text_col, tweet_url_col, tweet_date_col, "Engagement"] if c is not None]
        st.dataframe(work.sort_values("Engagement", ascending=False)[preview_cols].head(20), use_container_width=True)

    st.markdown("---")
    st.subheader("Key Findings")
    top_author = work.groupby(author_label)["Engagement"].sum().sort_values(ascending=False).index[0]
    top_post = work.sort_values("Engagement", ascending=False).iloc[0]
    top_text = str(top_post[tweet_text_col])[:140]
    st.markdown(f"""
    - **{top_author}** generated the most total engagement in this export
    - The strongest post starts with: **{top_text}**
    - Use high-engagement posts as qualitative examples before turning them into strategy
    - Compare engagement with views when impression data is present
    """)

# ══════════════════════════════════════════
# FALLBACK — unknown CSV
# ══════════════════════════════════════════
else:
    st.warning("Showing a raw preview — column names did not match a known format.")
    st.dataframe(df.head(50), use_container_width=True)
    st.info("Expected columns: age, gender, friend_count, likes, mobile_likes, www_likes  —  OR  —  App, Daily_Minutes_Spent, Posts_Per_Day, Likes_Per_Day, Follows_Per_Day  —  OR  —  tweet_url, author_username, text, created_at, like_count")

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
