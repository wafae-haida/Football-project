import sys
from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

APP_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(APP_DIR))
sys.path.append(str(PROJECT_ROOT))

from theme import apply_theme

apply_theme()

METRICS_DIR = PROJECT_ROOT / "model" / "metrics"

st.sidebar.markdown("""
<div class="sidebar-logo">
    <div class="sidebar-title">⚽ Football AI</div>
    <div class="sidebar-subtitle">Event Detection Platform</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-card">
    <div class="small-badge">Model Evaluation</div>
    <div class="hero-title">Métriques du modèle et rapports des agents</div>
    <div class="hero-subtitle">
        Consultez les performances du modèle, les matrices de confusion
        et les rapports générés par les différents agents du système.
    </div>
</div>
""", unsafe_allow_html=True)


def block_title(title, icon):
    st.markdown(f"""
    <div class="metrics-block-title">
        <span>{icon}</span>
        <span>{title}</span>
    </div>
    """, unsafe_allow_html=True)


def metric_card(title, value):
    try:
        value = float(value)
    except Exception:
        value = 0

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-value">{value:.4f}</div>
    </div>
    """, unsafe_allow_html=True)


def plot_confusion_matrix(cm_df, title):
    fig, ax = plt.subplots(figsize=(3.5, 3.5))

    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    matrix = cm_df.values

    im = ax.imshow(
        matrix,
        cmap="Greens",
        interpolation="nearest"
    )

    ax.set_xlabel("Classe prédite", fontsize=6)
    ax.set_ylabel("Classe réelle", fontsize=6)

    ax.set_xticks(range(len(cm_df.columns)))
    ax.set_yticks(range(len(cm_df.index)))

    ax.set_xticklabels(cm_df.columns, fontsize=4)
    ax.set_yticklabels(cm_df.index, fontsize=4)

    plt.setp(ax.get_xticklabels(), rotation=90)

    max_value = matrix.max() if matrix.max() != 0 else 1
    threshold = max_value / 2

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            value = matrix[i, j]
            text_color = "white" if value > threshold else "black"

            if value == 0:
                text_color = "#B8B8B8"

            ax.text(
                j,
                i,
                str(value),
                ha="center",
                va="center",
                fontsize=6,
                color=text_color
            )

    for i in range(min(matrix.shape[0], matrix.shape[1])):
        rect = plt.Rectangle(
            (i - 0.5, i - 0.5),
            1,
            1,
            fill=False,
            edgecolor="black",
            linewidth=1
        )
        ax.add_patch(rect)

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.tick_params(length=0)

    cbar = fig.colorbar(
        im,
        ax=ax,
        fraction=0.03,
        pad=0.02,
        shrink=0.70
    )

    cbar.outline.set_visible(False)
    cbar.ax.tick_params(labelsize=6)

    plt.tight_layout()
    st.pyplot(fig, transparent=True)


# =========================
# 1. MÉTRIQUES DU MODÈLE
# =========================

summary_file = METRICS_DIR / "metrics_summary.json"

if summary_file.exists():
    with open(summary_file, "r", encoding="utf-8") as f:
        metrics_summary = json.load(f)

    validation_metrics = metrics_summary.get("validation_metrics", {})
    test_metrics = metrics_summary.get("test_metrics", {})

    st.markdown("""
    <div class="matrix-card-title">
        Métriques de validation
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Accuracy", validation_metrics.get("accuracy", 0))
    with c2:
        metric_card("Precision", validation_metrics.get("precision_weighted", 0))
    with c3:
        metric_card("Recall", validation_metrics.get("recall_weighted", 0))
    with c4:
        metric_card("F1-score", validation_metrics.get("f1_weighted", 0))

    st.markdown("""
    <div class="matrix-card-title">
        Métriques du test
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Accuracy", test_metrics.get("accuracy", 0))
    with c2:
        metric_card("Precision", test_metrics.get("precision_weighted", 0))
    with c3:
        metric_card("Recall", test_metrics.get("recall_weighted", 0))
    with c4:
        metric_card("F1-score", test_metrics.get("f1_weighted", 0))

else:
    st.warning("Aucun fichier metrics_summary.json trouvé.")


# =========================
# 2. MATRICES DE CONFUSION
# =========================

st.markdown("""
<div class="matrix-card-title">
    Matrice de confusion - test
</div>
""", unsafe_allow_html=True)

cm_file = METRICS_DIR / "test_confusion_matrix.csv"

if cm_file.exists():
    cm_df = pd.read_csv(cm_file, index_col=0)
    plot_confusion_matrix(cm_df, "Test")
else:
    st.warning("Matrice de confusion introuvable pour test.")
# =========================
# 3. RAPPORTS DES AGENTS
# =========================


report_paths = {
    "Agent de traitement des données - train": PROJECT_ROOT / "dataset" / "processing" / "rapports" / "train_report.txt",
    "Agent de traitement des données - validation": PROJECT_ROOT / "dataset" / "processing" / "rapports" / "validation_report.txt",
    "Agent de traitement des données - test": PROJECT_ROOT / "dataset" / "processing" / "rapports" / "test_report.txt",

    "Agent d'analyse des actions - train": PROJECT_ROOT / "dataset" / "action_analysis" / "reports" / "train_action_analysis_report.txt",
    "Agent d'analyse des actions - validation": PROJECT_ROOT / "dataset" / "action_analysis" / "reports" / "validation_action_analysis_report.txt",
    "Agent d'analyse des actions - test": PROJECT_ROOT / "dataset" / "action_analysis" / "reports" / "test_action_analysis_report.txt",

    "Agent d'analyse spatiale - train": PROJECT_ROOT / "dataset" / "spatial_analysis" / "reports" / "train_spatial_analysis_report.txt",
    "Agent d'analyse spatiale - validation": PROJECT_ROOT / "dataset" / "spatial_analysis" / "reports" / "validation_spatial_analysis_report.txt",
    "Agent d'analyse spatiale - test": PROJECT_ROOT / "dataset" / "spatial_analysis" / "reports" / "test_spatial_analysis_report.txt",

    "Agent d'analyse de graphe - train": PROJECT_ROOT / "dataset" / "graph_analysis" / "reports" / "train_graph_analysis_report.txt",
    "Agent d'analyse de graphe - validation": PROJECT_ROOT / "dataset" / "graph_analysis" / "reports" / "validation_graph_analysis_report.txt",
    "Agent d'analyse de graphe - test": PROJECT_ROOT / "dataset" / "graph_analysis" / "reports" / "test_graph_analysis_report.txt",

    "Agent d'entraînement du modèle": PROJECT_ROOT / "model" / "metrics" / "model_training_report.txt",
}

st.markdown("""
<div class="report-box">
    <div class="report-label">Choisir un rapport</div>
</div>
""", unsafe_allow_html=True)

selected_report = st.selectbox(
    "",
    list(report_paths.keys()),
    label_visibility="collapsed"
)

report_file = report_paths[selected_report]

st.markdown("""
<div class="report-box">
    <div class="report-label">Contenu du rapport</div>
</div>
""", unsafe_allow_html=True)

if report_file.exists():
    with open(report_file, "r", encoding="utf-8") as f:
        report_text = f.read()

    st.text_area(
        "",
        report_text,
        height=420,
        label_visibility="collapsed"
    )
else:
    st.warning(f"Rapport introuvable : {report_file}")