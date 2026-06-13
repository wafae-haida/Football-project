from crewai import Agent, LLM

from multi_agent_system.tools.data_processing_tools import DataProcessingTool


def create_data_processing_agent() -> Agent:
    llm = LLM(
        model="ollama/llama3.1:8b",
        base_url="http://localhost:11434",
        temperature=0
    )

    return Agent(
        role="Agent de traitement des données",
        goal="Préparer les données StatsBomb avant leur analyse.",
        backstory=(
            "Agent responsable du chargement, du contrôle et de la préparation "
            "des fichiers StatsBomb afin de fournir aux autres agents une liste "
            "de fichiers exploitables et un rapport de traitement."
        ),
        tools=[DataProcessingTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=1
    )