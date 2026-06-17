from crewai import Task


def create_action_analysis_task(agent, report_path: str):

    return Task(
        description="""
        Utiliser obligatoirement l'outil :

        outil_d_analyse_des_actions

        L'outil doit être exécuté avec :

        data_file = {data_file}

        Ne jamais utiliser /path/to/.
        Ne jamais inventer un chemin.

        Après l'exécution de l'outil, lire le résumé JSON retourné.

        Ensuite, rédiger un rapport humain clair en langage naturel.
        Le rapport doit expliquer en détail le travail réalisé par l'Agent d'Analyse des Actions.

        Le rapport doit obligatoirement décrire :

        1. L'objectif de l'agent.

        2. Les données reçues depuis l'Agent de Traitement des Données.

        3. Les événements considérés comme actions de jeu utilisables
        (passes, carries, dribbles, duels, récupérations, interceptions,
        pressions, tirs, etc.).

        4. Les événements clés exclus du contexte et utilisés comme cibles :
        - But
        - Penalty
        - Corner
        - Coup franc
        - Carton jaune
        - Carton rouge
        - Faute disciplinaire
        - Hors-jeu

        5. La méthode utilisée pour construire les séquences :
        pour chaque événement clé, récupérer les 10 actions précédentes.

        6. Le contenu des batches CSV générés :
        - informations des actions ;
        - joueurs impliqués ;
        - rôles des joueurs ;
        - ordre chronologique des actions ;
        - label cible à prédire.

        7. Les statistiques obtenues.

        8. L'utilité des données produites pour les étapes suivantes du pipeline :
        analyse spatiale, analyse de graphe et entraînement du modèle.

        Le rapport doit être rédigé comme si l'agent expliquait exactement ce qu'il a fait.

        Ne pas retourner un JSON.
        Ne pas retourner un tableau technique.
        Retourner uniquement le rapport humain final.
        """,
        expected_output="""
        Rapport humain final de l'analyse des actions.
        """,
        agent=agent,
        output_file=report_path
    )