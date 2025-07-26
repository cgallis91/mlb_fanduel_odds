import streamlit as st
from scrape_odds import scrape_odds

st.set_page_config(page_title="MLB FanDuel Odds", layout="wide")
st.title("MLB FanDuel Odds")

@st.cache_data(show_spinner=True)
def get_data():
    return scrape_odds()

st.info("Fetching latest MLB odds from FanDuel. This may take a few seconds...")

df = get_data()

if df.empty:
    st.warning("No data available. Please try again later.")
else:
    st.dataframe(df, use_container_width=True)