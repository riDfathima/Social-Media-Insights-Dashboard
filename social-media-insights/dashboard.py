# Generated from: dashboard.py.ipynb
# Converted at: 2026-06-27T17:50:38.357Z
# Next step (optional): refactor into modules & generate tests with RunCell
# Quick start: pip install runcell

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Facebook Insights", layout="wide")

st.title("Facebook User Behaviour Dashboard")
st.markdown("Analysing engagement patterns across age, gender and platform.")

# Sidebar — upload or use default
uploaded = st.sidebar.file_uploader("Upload your own CSV", type="csv")

if uploaded:
    df = pd.read_csv(uploaded)
    st.sidebar.success("Your file loaded!")
else:
    df = pd.read_csv("pseudo_facebook_clean.csv")
    st.sidebar.info("Using sample dataset")

# Clean
df = df[df['age'].between(13, 113)].copy()
numeric_cols = ['friend_count','likes','likes_received',
                'mobile_likes','www_likes','tenure']
df[numeric_cols] = df[numeric_cols].fillna(0)
df['age_group'] = pd.cut(df['age'],
    bins=[13,17,24,34,44,54,64,113],
    labels=['13-17','18-24','25-34','35-44','45-54','55-64','65+'])

# KPI row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Users", f"{len(df):,}")
col2.metric("Avg Friend Count", f"{df['friend_count'].mean():.1f}")
col3.metric("Mobile Likes %",
    f"{df['mobile_likes'].sum()/df['likes'].sum()*100:.1f}%")
col4.metric("Avg Likes Received", f"{df['likes_received'].mean():.1f}")

st.divider()

# Chart row 1
c1, c2 = st.columns(2)

with c1:
    st.subheader("Avg Friends by Age Group")
    age_data = df.groupby('age_group', observed=True)['friend_count'].mean().reset_index()
    fig1 = px.bar(age_data, x='age_group', y='friend_count',
                  color_discrete_sequence=['#9B5CF6'])
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.subheader("Mobile vs Web Likes")
    platform = pd.DataFrame({
        'Platform': ['Mobile', 'Web'],
        'Likes': [df['mobile_likes'].sum(), df['www_likes'].sum()]
    })
    fig2 = px.pie(platform, names='Platform', values='Likes',
                  color_discrete_sequence=['#E040A0','#9B5CF6'])
    st.plotly_chart(fig2, use_container_width=True)

# Chart row 2
c3, c4 = st.columns(2)

with c3:
    st.subheader("Likes Received by Gender")
    gen = df[df['gender'].isin(['male','female'])]
    fig3 = px.box(gen, x='gender', y='likes_received',
                  color='gender',
                  color_discrete_map={'female':'#E040A0','male':'#9B5CF6'})
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    st.subheader("Friends vs Tenure")
    sample = df.sample(min(2000, len(df)), random_state=42)
    fig4 = px.scatter(sample, x='tenure', y='friend_count',
                      color='gender',
                      color_discrete_map={'female':'#E040A0','male':'#9B5CF6'},
                      opacity=0.4)
    st.plotly_chart(fig4, use_container_width=True)

st.divider()
st.subheader("Key Findings")
st.markdown("""
- **25-34 age group** has the highest average friend count — 
  best target for organic reach campaigns
- **Mobile drives the majority of likes** — content should be 
  designed mobile-first
- **Female users receive more likes on average** — 
  relevant for influencer and creator targeting
- **Tenure correlates with connections** — 
  long-term users are your most networked audience
""")