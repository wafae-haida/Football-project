from crewai import Agent, LLM

from multi_agent_system.tools.action_analysis_tools import ActionAnalysisTool


def create_action_analysis_agent() -> Agent:
    llm = LLM(
        model="ollama/llama3.1:8b",
        base_url="http://localhost:11434",
        temperature=0
    )

    return Agent(
        role="Agent d'analyse des actions",
        goal=(
            "Analyser les actions de jeu présentes dans les matchs "
            "et extraire les caractéristiques nécessaires pour les étapes suivantes."
        ),
        backstory=(
            "Cet agent est responsable de l'analyse des événements de football. "
            "Il conserve uniquement les actions de jeu utiles et exclut les événements "
            "critiques à prédire afin d'éviter toute fuite d'information."
        ),
        tools=[
            ActionAnalysisTool()
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=1
    )