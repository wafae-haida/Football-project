from crewai import Task


def create_graph_analysis_task(agent, report_path: str):

    return Task(
        description="""
        Utiliser obligatoirement l'outil :

        outil_d_analyse_de_graphe

        L'outil doit être exécuté avec :

        data_file = {data_file}

        action_batches_dir = {action_batches_dir}

        spatial_batches_dir = {spatial_batches_dir}

        Ne jamais utiliser /path/to/.
        Ne jamais inventer un chemin.

        Après l'exécution de l'outil, lire le résumé JSON retourné.

        Ensuite, rédiger un rapport humain clair.

        Le rapport doit expliquer :

        1. Le rôle de l'Agent d'Analyse de Graphe.

        2. Le split analysé :
           - train : données utilisées pour l'apprentissage ;
           - validation : données utilisées pour l'évaluation intermédiaire ;
           - test : données réservées à l'évaluation finale.

        3. Les trois entrées utilisées :
           - output de l'Agent 1 : fichier data du split ;
           - output de l'Agent 2 : batches d'analyse des actions ;
           - output de l'Agent 3 : batches d'analyse spatiale.

        4. Le travail réalisé :
           - lecture des séquences enrichies ;
           - extraction des joueurs impliqués ;
           - construction de relations entre joueurs ;
           - comptage des relations ;
           - identification du joueur principal ;
           - calcul des transitions entre équipes ;
           - génération de variables relationnelles.

        5. Les sorties produites :
           - batches de caractéristiques de graphe dans dataset/graph_analysis/data/ ;
           - trace dans multi_agent_system/traces_crewai_report/.

        6. Préciser que les graphes visuels ne sont pas générés ici.
           Ils seront générés plus tard dans Streamlit.

        Ne pas retourner un JSON.
        Retourner uniquement le rapport humain final.
        """,
        expected_output="""
        Rapport humain final de l'analyse de graphe.
        """,
        agent=agent,
        output_file=report_path
    )