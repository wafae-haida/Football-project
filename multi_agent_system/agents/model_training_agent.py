from crewai import Agent, LLM

from multi_agent_system.tools.model_training_tools import ModelTrainingTool


def create_model_training_agent() -> Agent:
    llm = LLM(
        model="ollama/llama3.1:8b",
        base_url="http://localhost:11434",
        temperature=0
    )

    return Agent(
        role="Agent d'entraînement du modèle",
        goal=(
            "Entraîner un modèle de prédiction des événements clés "
            "à partir des sorties des agents précédents."
        ),
        backstory=(
            "Cet agent utilise les caractéristiques produites par les agents "
            "d'analyse des actions, d'analyse spatiale et d'analyse de graphe. "
            "Il entraîne le modèle sur le split train, l'évalue sur validation "
            "et effectue l'évaluation finale sur test."
        ),
        tools=[
            ModelTrainingTool()
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=1
    )