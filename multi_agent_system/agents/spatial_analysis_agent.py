from crewai import Agent, LLM

from multi_agent_system.tools.spatial_analysis_tools import SpatialAnalysisTool


def create_spatial_analysis_agent() -> Agent:
    llm = LLM(
        model="ollama/llama3.1:8b",
        base_url="http://localhost:11434",
        temperature=0
    )

    return Agent(
        role="Agent d'analyse spatiale",
        goal=(
            "Enrichir les séquences d'actions avec des informations spatiales "
            "afin d'aider le modèle à prédire les événements clés."
        ),
        backstory=(
            "Cet agent utilise les séquences générées par l'Agent d'analyse des actions "
            "et les fichiers validés par l'Agent de traitement des données. "
            "Il ajoute les coordonnées, les zones du terrain et les distances au but "
            "pour représenter le contexte spatial précédant les événements clés."
        ),
        tools=[
            SpatialAnalysisTool()
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=1
    )