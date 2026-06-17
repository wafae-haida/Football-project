from crewai import Agent, LLM

from multi_agent_system.tools.graph_analysis_tools import GraphAnalysisTool


def create_graph_analysis_agent() -> Agent:
    llm = LLM(
        model="ollama/llama3.1:8b",
        base_url="http://localhost:11434",
        temperature=0
    )

    return Agent(
        role="Agent d'analyse de graphe",
        goal=(
            "Extraire des caractéristiques relationnelles entre les joueurs "
            "à partir des séquences d'actions enrichies spatialement."
        ),
        backstory=(
            "Cet agent reçoit les sorties de l'Agent de traitement des données, "
            "de l'Agent d'analyse des actions et de l'Agent d'analyse spatiale. "
            "Il transforme les séquences en relations entre joueurs afin de produire "
            "des variables de graphe utilisables par le modèle."
        ),
        tools=[
            GraphAnalysisTool()
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=1
    )