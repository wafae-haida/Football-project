from crewai import Task


def create_spatial_analysis_task(agent, report_path: str):

    return Task(
        description="""
        Utiliser obligatoirement l'outil :

        outil_d_analyse_spatiale

        L'outil doit être exécuté avec :

        data_file = {data_file}

        action_batches_dir = {action_batches_dir}

        Ne jamais utiliser /path/to/.
        Ne jamais inventer un chemin.

        Après l'exécution de l'outil, lire le résumé JSON retourné.

        Ensuite, rédiger un rapport humain clair en langage naturel.

        Le rapport doit expliquer en détail :

        1. Le rôle de l'Agent d'Analyse Spatiale.

        2. Le split analysé :
           - train : données utilisées pour l'apprentissage du modèle ;
           - validation : données utilisées pour l'évaluation intermédiaire ;
           - test : données réservées à l'évaluation finale.

        3. Les entrées utilisées :
           - le fichier data produit par l'Agent 1 ;
           - les batches de séquences produits par l'Agent d'analyse des actions.

        4. Le travail réalisé :
           - lecture des séquences d'actions ;
           - récupération des identifiants des actions précédentes ;
           - recherche des coordonnées dans les fichiers JSON originaux ;
           - ajout des coordonnées x et y ;
           - calcul de la zone du terrain ;
           - calcul de la distance au but ;
           - création de variables spatiales au niveau de la séquence.

        5. Les sorties produites :
           - batches spatiaux dans dataset/spatial_analysis/data/ ;
           - trace d'exécution dans multi_agent_system/traces_crewai_report/.

        6. L'utilité des données spatiales pour la prédiction :
           elles permettent au modèle de comprendre où les actions précédentes
           ont eu lieu sur le terrain avant l'apparition d'un événement clé.

        Ne pas retourner un JSON.
        Ne pas retourner un tableau technique.
        Retourner uniquement le rapport humain final.
        """,
        expected_output="""
        Rapport humain final de l'analyse spatiale.
        """,
        agent=agent,
        output_file=report_path
    )