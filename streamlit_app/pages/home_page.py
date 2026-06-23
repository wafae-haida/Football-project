import sys
from pathlib import Path
import streamlit as st
from theme import apply_theme

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))


apply_theme()

st.sidebar.markdown("""
<div class="sidebar-logo">
    <div class="sidebar-title">⚽ Football</div>
    <div class="sidebar-subtitle">SMA Event Detection Platform</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-card">
    <div class="small-badge">SMA • détection des événements</div>
    <div class="hero-title">Système multi-agent pour la détection <br> des événements clés d'un match de football</div>
    <div class="hero-subtitle">
            Plateforme intelligente dédiée à l’analyse des matchs de football. Elle permet de détecter automatiquement les événements clés, d’explorer les séquences d’actions et les graphes de jeu associés, ainsi que d’évaluer les performances des modèles de prédiction à l’aide de métriques.
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">Système multi-agent</div>
        <div class="feature-text">
            Architecture composée de plusieurs agents spécialisés collaborant pour analyser les données du match.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">Détection intelligente</div>
        <div class="feature-text">
        Uploadez un fichier JSON de match et lancez la prédiction automatique des événements clés.
        </div>
    </div>
    """, unsafe_allow_html=True)



with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">Détails du modèle</div>
        <div class="feature-text">
        Consultez les métriques, matrices de confusion et rapports générés par le système.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="section-box">
        <div class="services-title">Services inclus:</div>
        <div class="badge">Upload JSON</div>
        <div class="badge">Détection des événements</div>
        <div class="badge">Réel vs Prédit</div>
        <div class="badge">Séquences d'actions</div>
        <div class="badge">Graphe</div>
        <div class="badge">Métriques</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="section-box">      
        <div class="services-title">Événements ciblés:</div>
        <div class="badge-event">Goal</div>
        <div class="badge-event">Penalty</div>
        <div class="badge-event">Coup franc</div>
        <div class="badge-event">Corner</div>
        <div class="badge-event">Carton jaune</div>
        <div class="badge-event">Carton rouge</div>
        <div class="badge-event">Faute</div>
        <div class="badge-event">Hors-jeu</div>
    </div>
    """, unsafe_allow_html=True)