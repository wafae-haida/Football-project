from crewai import Task


def create_data_processing_task(agent, input_path: str) -> Task:
    return Task(
        description=(
            "Utilise l'outil_de_traitement_des_donnees avec l'argument exact suivant :\n"
            f"input_path = {input_path}\n\n"
            "Règles obligatoires :\n"
            "- Ne remplace jamais ce chemin par un exemple.\n"
            "- N'ajoute jamais /path/to/.\n"
            "- N'invente aucun autre chemin.\n"
            "- Utilise exactement la valeur donnée."
        ),
        expected_output=(
            "Le chemin du fichier data généré et le chemin du rapport texte généré."
        ),
        agent=agent,
    )