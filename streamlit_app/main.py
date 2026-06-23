import streamlit as st

st.set_page_config(
    page_title="MatchFlow",
    page_icon="🌀",
    layout="wide",
    initial_sidebar_state="expanded"
)

pages = [
    st.Page("pages/home_page.py", title="Accueil", icon="🏠"),
    st.Page("pages/detection_page.py", title="Détection", icon="🎯"),
    st.Page("pages/metrics_page.py", title="Métriques et rapports", icon="📊"),
]

pg = st.navigation(pages)
pg.run()