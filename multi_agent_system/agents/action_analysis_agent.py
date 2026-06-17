from crewai import Agent, LLM

from multi_agent_system.tools.action_analysis_tools import ActionAnalysisTool
from multi_agent_system.tools.report_writer_tools import ReportWriterTool


def create_action_analysis_agent() -> Agent:
    llm = LLM(
        model="ollama/llama3.1:8b",
        base_url="http://localhost:11434",
        temperature=0
    )

    return Agent(
        role="Agent d'analyse des actions",
        goal=(
            "Construire des séquences d'actions précédant les événements clés "
            "et rédiger un rapport humain sur le résultat de l'analyse."
        ),
        backstory=(
            "Cet agent analyse les événements d'un match de football. "
            "Il utilise l'outil d'analyse pour générer les batches de séquences, "
            "puis il rédige et sauvegarde un rapport humain décrivant le résultat."
        ),
        tools=[
            ActionAnalysisTool(),
            ReportWriterTool()
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=2
    )