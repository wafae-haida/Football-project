import sys
from pathlib import Path
import json
from collections import defaultdict

import pandas as pd
import joblib
import streamlit as st
import networkx as nx
import plotly.graph_objects as go

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix
)

APP_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(APP_DIR))
sys.path.append(str(PROJECT_ROOT))

from theme import apply_theme
from multi_agent_system.tools.action_analysis_tools import ActionAnalysisTool
from multi_agent_system.tools.spatial_analysis_tools import SpatialAnalysisTool
from multi_agent_system.tools.graph_analysis_tools import GraphAnalysisTool

apply_theme()

MODEL_PATH = PROJECT_ROOT / "model" / "event_prediction_model.pkl"


st.sidebar.markdown("""
<div class="sidebar-logo">
    <div class="sidebar-title">⚽ Football AI</div>
    <div class="sidebar-subtitle">Event Detection Platform</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-card">
    <div class="small-badge">Event Detection</div>
    <div class="hero-title">Détection des événements clés</div>
    <div class="hero-subtitle">
        Uploadez un fichier JSON de match, lancez les agents d’analyse,
        puis visualisez les événements détectés, les séquences associées,
        la matrice de confusion colorée et le graphe global du match.
    </div>
</div>
""", unsafe_allow_html=True)


def safe_get(dct, keys, default=None):
    current = dct
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return current if current is not None else default


def prepare_x(df: pd.DataFrame) -> pd.DataFrame:
    excluded_columns = []

    for col in df.columns:
        if col == "target_label":
            continue

        if col.startswith("target_"):
            excluded_columns.append(col)
        elif col in [
            "match_id",
            "sequence_action_types",
            "sequence_players",
            "sequence_roles",
            "sequence_unique_players",
            "sequence_unique_teams",
            "sequence_unique_roles",
            "sequence_edges"
        ]:
            excluded_columns.append(col)
        elif "event_id" in col:
            excluded_columns.append(col)
        elif "timestamp" in col:
            excluded_columns.append(col)
        elif "player" in col:
            excluded_columns.append(col)
        elif "pass_recipient" in col:
            excluded_columns.append(col)

    return df.drop(columns=excluded_columns + ["target_label"], errors="ignore")


def save_uploaded_json(uploaded_file) -> Path:
    upload_dir = PROJECT_ROOT / "dataset" / "streamlit_uploaded"
    upload_dir.mkdir(parents=True, exist_ok=True)

    json_path = upload_dir / "uploaded_match.json"
    content = json.load(uploaded_file)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

    return json_path


def create_processing_data(json_path: Path) -> Path:
    processing_dir = PROJECT_ROOT / "dataset" / "streamlit_uploaded" / "processing"
    processing_dir.mkdir(parents=True, exist_ok=True)

    data_file = processing_dir / "uploaded_data.json"

    with open(json_path, "r", encoding="utf-8") as f:
        events = json.load(f)

    data_content = {
        "input_path": str(json_path),
        "split": "uploaded",
        "total_input_files": 1,
        "total_valid_files": 1,
        "total_invalid_files": 0,
        "total_events": len(events),
        "valid_files": [str(json_path)],
        "invalid_files": [],
        "status": "READY"
    }

    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data_content, f, ensure_ascii=False, indent=2)

    return data_file


def run_feature_pipeline(data_file: Path):
    action_tool = ActionAnalysisTool()
    spatial_tool = SpatialAnalysisTool()
    graph_tool = GraphAnalysisTool()

    action_tool._run(data_file=str(data_file))

    action_batches_dir = PROJECT_ROOT / "dataset" / "action_analysis" / "data" / "uploaded_batches"

    spatial_tool._run(
        data_file=str(data_file),
        action_batches_dir=str(action_batches_dir)
    )

    spatial_batches_dir = PROJECT_ROOT / "dataset" / "spatial_analysis" / "data" / "uploaded_batches"

    graph_tool._run(
        data_file=str(data_file),
        action_batches_dir=str(action_batches_dir),
        spatial_batches_dir=str(spatial_batches_dir)
    )

    return PROJECT_ROOT / "dataset" / "graph_analysis" / "data" / "uploaded_batches"


def load_batches(batch_dir: Path) -> pd.DataFrame:
    files = sorted(batch_dir.glob("*.csv"))

    if not files:
        return pd.DataFrame()

    return pd.concat(
        [pd.read_csv(file, low_memory=False) for file in files],
        ignore_index=True
    )


def short_name(name):
    if not isinstance(name, str):
        return ""
    parts = name.split()
    if len(parts) <= 2:
        return name
    return f"{parts[0]} {parts[-1]}"


def extract_pass_network(events, selected_team="Toutes", selected_period="Tout le match", min_passes=2):
    edges = defaultdict(int)
    node_team = {}
    node_count = defaultdict(int)

    for event in events:
        event_type = safe_get(event, ["type", "name"], "")
        if event_type != "Pass":
            continue

        period = event.get("period")
        if selected_period == "1ère mi-temps" and period != 1:
            continue
        if selected_period == "2ème mi-temps" and period != 2:
            continue

        team = safe_get(event, ["team", "name"], "Équipe inconnue")
        if selected_team != "Toutes" and team != selected_team:
            continue

        player = safe_get(event, ["player", "name"])
        recipient = safe_get(event, ["pass", "recipient", "name"])

        if not player or not recipient:
            continue

        source = short_name(player)
        target = short_name(recipient)

        edges[(source, target)] += 1
        node_count[source] += 1
        node_count[target] += 1
        node_team[source] = team
        node_team[target] = team

    filtered_edges = {
        edge: weight for edge, weight in edges.items()
        if weight >= min_passes
    }

    return filtered_edges, node_team, node_count


def build_plotly_network(edges, node_team, node_count):
    G = nx.DiGraph()

    for (source, target), weight in edges.items():
        G.add_edge(source, target, weight=weight)

    if G.number_of_nodes() == 0:
        return None, pd.DataFrame()

    pos = nx.spring_layout(G, k=0.9, iterations=80, seed=42)

    teams = sorted(set(node_team.values()))
    palette = ["#4E9A8A", "#D9D957", "#8AB6D6", "#F4A261", "#B56576"]
    team_colors = {team: palette[i % len(palette)] for i, team in enumerate(teams)}

    edge_traces = []

    for source, target, data in G.edges(data=True):
        x0, y0 = pos[source]
        x1, y1 = pos[target]
        weight = data.get("weight", 1)

        edge_trace = go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode="lines",
            line=dict(
                width=max(1.2, min(weight, 7)),
                color="rgba(78,154,138,0.35)"
            ),
            hoverinfo="text",
            text=f"{source} → {target}<br>Passes : {weight}",
            showlegend=False
        )
        edge_traces.append(edge_trace)

    node_x = []
    node_y = []
    node_text = []
    node_size = []
    node_color = []
    centrality_rows = []

    degree_centrality = nx.degree_centrality(G)
    betweenness = nx.betweenness_centrality(G)
    pagerank = nx.pagerank(G, weight="weight")

    for node in G.nodes():
        x, y = pos[node]
        team = node_team.get(node, "Équipe inconnue")
        passes = node_count.get(node, 1)

        node_x.append(x)
        node_y.append(y)
        node_text.append(
            f"<b>{node}</b><br>"
            f"Équipe : {team}<br>"
            f"Implication passes : {passes}<br>"
            f"Degree : {degree_centrality.get(node, 0):.3f}<br>"
            f"Betweenness : {betweenness.get(node, 0):.3f}<br>"
            f"PageRank : {pagerank.get(node, 0):.3f}"
        )

        node_size.append(18 + passes * 2)
        node_color.append(team_colors.get(team, "#4E9A8A"))

        centrality_rows.append({
            "Joueur": node,
            "Équipe": team,
            "Implication passes": passes,
            "Degree": round(degree_centrality.get(node, 0), 4),
            "Betweenness": round(betweenness.get(node, 0), 4),
            "PageRank": round(pagerank.get(node, 0), 4)
        })

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=list(G.nodes()),
        textposition="top center",
        hovertext=node_text,
        hoverinfo="text",
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(width=1.5, color="#2F5D50"),
            opacity=0.92
        ),
        textfont=dict(size=12, color="#16352F"),
        showlegend=False
    )

    fig = go.Figure(data=edge_traces + [node_trace])

    fig.update_layout(
        title=dict(
            text="Réseau de passes du match",
            font=dict(size=22, color="#16352F"),
            x=0.02
        ),
        paper_bgcolor="rgba(248,251,247,0)",
        plot_bgcolor="rgba(248,251,247,0)",
        height=650,
        margin=dict(l=20, r=20, t=60, b=20),
        hovermode="closest",
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            visible=False
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            visible=False
        )
    )

    centrality_df = pd.DataFrame(centrality_rows).sort_values(
        by="PageRank",
        ascending=False
    )

    return fig, centrality_df


def style_confusion_matrix(cm_df):
    return (
        cm_df.style
        .background_gradient(cmap="YlGnBu", axis=None)
        .set_properties(**{
            "text-align": "center",
            "font-weight": "700",
            "border": "1px solid #B7C5B5"
        })
    )


def build_events_global_table(df_result):
    rows = []

    for _, row in df_result.iterrows():
        details = []

        for i in range(1, 11):
            action = row.get(f"action_{i}_type")
            player = row.get(f"action_{i}_player")
            role = row.get(f"action_{i}_role")

            if pd.notna(action):
                details.append(
                    f"{i}. {action} | {player if pd.notna(player) else ''} | {role if pd.notna(role) else ''}"
                )

        rows.append({
            "Minute": row.get("target_minute"),
            "Seconde": row.get("target_second"),
            "Événement réel": row.get("target_label"),
            "Événement prédit": row.get("predicted_event"),
            "Confiance": round(float(row.get("prediction_confidence", 0)), 4),
            "Séquence d'actions": row.get("sequence_action_types"),
            "Joueurs": row.get("sequence_players"),
            "Rôles": row.get("sequence_roles"),
            "Détail actions / joueurs / rôles": "\n".join(details)
        })

    return pd.DataFrame(rows)


uploaded_file = st.file_uploader(
    "Uploader un fichier JSON StatsBomb",
    type=["json"]
)

if uploaded_file is None:
    st.info("Veuillez uploader un fichier JSON pour lancer la détection.")
    st.stop()

st.success("Fichier chargé avec succès.")

if st.button("Lancer la détection"):
    if not MODEL_PATH.exists():
        st.error(f"Modèle introuvable : {MODEL_PATH}")
        st.stop()

    with st.spinner("Préparation des séquences, prédiction et visualisations..."):
        json_path = save_uploaded_json(uploaded_file)

        with open(json_path, "r", encoding="utf-8") as f:
            match_events = json.load(f)

        data_file = create_processing_data(json_path)
        graph_batches_dir = run_feature_pipeline(data_file)
        df = load_batches(graph_batches_dir)

        if df.empty:
            st.error("Aucune séquence générée pour ce fichier.")
            st.stop()

        model = joblib.load(MODEL_PATH)

        X = prepare_x(df)
        y_true = df["target_label"]

        predictions = model.predict(X)

        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(X)
            confidence = probabilities.max(axis=1)
        else:
            confidence = [0] * len(predictions)

        df_result = df.copy()
        df_result["predicted_event"] = predictions
        df_result["prediction_confidence"] = confidence

    st.success("Détection terminée.")

    st.subheader("📊 Métriques générales")

    accuracy = accuracy_score(y_true, predictions)

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true,
        predictions,
        average="weighted",
        zero_division=0
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Accuracy", round(accuracy, 4))
    c2.metric("Precision", round(precision, 4))
    c3.metric("Recall", round(recall, 4))
    c4.metric("F1-score", round(f1, 4))

    st.subheader("🧩 Matrice de confusion colorée")

    labels = sorted(y_true.unique().tolist())
    cm = confusion_matrix(y_true, predictions, labels=labels)
    cm_df = pd.DataFrame(cm, index=labels, columns=labels)

    st.dataframe(
        style_confusion_matrix(cm_df),
        use_container_width=True
    )

    st.subheader("🌐 Graphe global du match")

    teams = sorted({
        safe_get(event, ["team", "name"])
        for event in match_events
        if safe_get(event, ["team", "name"]) is not None
    })

    f1_col, f2_col, f3_col = st.columns(3)

    with f1_col:
        selected_team = st.selectbox(
            "Équipe",
            ["Toutes"] + teams
        )

    with f2_col:
        selected_period = st.selectbox(
            "Période",
            ["Tout le match", "1ère mi-temps", "2ème mi-temps"]
        )

    with f3_col:
        min_passes = st.slider(
            "Seuil minimal de passes",
            min_value=1,
            max_value=10,
            value=2
        )

    edges, node_team, node_count = extract_pass_network(
        match_events,
        selected_team=selected_team,
        selected_period=selected_period,
        min_passes=min_passes
    )

    fig, centrality_df = build_plotly_network(edges, node_team, node_count)

    if fig is None:
        st.warning("Aucun graphe lisible avec ces filtres. Diminue le seuil minimal de passes.")
    else:
        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "Design appliqué : fond épuré, palette limitée, nœuds ronds, "
            "taille selon l'implication, épaisseur selon la fréquence des passes, "
            "étiquettes courtes et détails au survol."
        )

        st.subheader("⭐ Joueurs les plus influents")

        st.dataframe(
            centrality_df.head(10),
            use_container_width=True,
            hide_index=True
        )

    st.subheader("📌 Liste globale des événements détectés avec séquences et rôles")

    events_global_df = build_events_global_table(df_result)

    st.dataframe(
        events_global_df,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("🔍 Détail d'un événement")

    selected_index = st.selectbox(
        "Choisir un événement",
        df_result.index.tolist()
    )

    selected_row = df_result.loc[selected_index]

    confidence_value = selected_row.get("prediction_confidence", 0)

    try:
        confidence_value = round(float(confidence_value), 4)
    except Exception:
        confidence_value = 0

    st.markdown(f"""
    <div class="section-box">
        <h3>Résultat sélectionné</h3>
        <p><b>Événement réel :</b> {selected_row.get("target_label")}</p>
        <p><b>Événement prédit :</b> {selected_row.get("predicted_event")}</p>
        <p><b>Confiance :</b> {confidence_value}</p>
        <p><b>Séquence :</b> {selected_row.get("sequence_action_types")}</p>
        <p><b>Joueurs :</b> {selected_row.get("sequence_players")}</p>
        <p><b>Rôles :</b> {selected_row.get("sequence_roles")}</p>
    </div>
    """, unsafe_allow_html=True)

    action_rows = []

    for i in range(1, 11):
        action_type = selected_row.get(f"action_{i}_type")

        if pd.notna(action_type):
            action_rows.append({
                "Ordre": i,
                "Action": action_type,
                "Joueur": selected_row.get(f"action_{i}_player"),
                "Rôle": selected_row.get(f"action_{i}_role"),
                "Équipe": selected_row.get(f"action_{i}_team"),
                "Zone": selected_row.get(f"action_{i}_zone"),
                "Distance au but": selected_row.get(f"action_{i}_distance_to_goal")
            })

    st.dataframe(
        pd.DataFrame(action_rows),
        use_container_width=True,
        hide_index=True
    )