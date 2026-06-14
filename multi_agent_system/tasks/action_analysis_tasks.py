from crewai import Task


def create_action_analysis_task(
    agent,
    data_file: str
):

    return Task(
        description=f"""
        Utiliser obligatoirement l'outil
        outil_d_analyse_des_actions.

        Ne jamais effectuer l'analyse manuellement.

        Ne jamais essayer de lire les fichiers
        ou de produire les résultats par raisonnement.

        L'outil doit obligatoirement être exécuté
        avec le paramètre suivant :

        data_file = {data_file}

        L'outil est responsable de :

        - Charger le fichier de données produit par l'Agent 1.
        - Lire la liste des matchs exploitables.
        - Parcourir les événements de chaque match.

        - Exclure les événements suivants :

            * Goal
            * Foul Committed
            * Foul Won
            * Penalty
            * Offside
            * Free Kick
            * Corner
            * Yellow Card
            * Red Card

        - Conserver uniquement les actions de jeu.

        - Extraire les caractéristiques des actions conservées.

        - Générer les batches CSV de caractéristiques.

        - Générer le rapport d'analyse.

        - Générer la trace d'exécution.

        Une fois le traitement terminé,
        retourner uniquement le résultat
        fourni par l'outil.
        """,
        expected_output="""
        Résultat retourné par l'outil
        outil_d_analyse_des_actions contenant :

        - Le dossier des batches générés.
        - Le rapport d'analyse.
        - Le fichier de trace.
        - Le statut final du traitement.
        """,
        agent=agent
    )