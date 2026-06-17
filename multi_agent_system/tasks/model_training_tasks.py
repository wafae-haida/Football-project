from crewai import Task


def create_model_training_task(agent, report_path: str):

    return Task(
        description="""
        Utiliser obligatoirement l'outil :

        outil_d_entrainement_du_modele

        L'outil doit être exécuté avec :

        train_action_batches_dir = {train_action_batches_dir}
        validation_action_batches_dir = {validation_action_batches_dir}
        test_action_batches_dir = {test_action_batches_dir}

        train_spatial_batches_dir = {train_spatial_batches_dir}
        validation_spatial_batches_dir = {validation_spatial_batches_dir}
        test_spatial_batches_dir = {test_spatial_batches_dir}

        train_graph_batches_dir = {train_graph_batches_dir}
        validation_graph_batches_dir = {validation_graph_batches_dir}
        test_graph_batches_dir = {test_graph_batches_dir}

        Ne jamais utiliser /path/to/.
        Ne jamais inventer un chemin.

        Après l'exécution de l'outil, lire le résumé JSON retourné.

        Ensuite, rédiger un rapport humain clair.

        Le rapport doit expliquer :
        - le rôle de l'Agent d'entraînement ;
        - les entrées utilisées ;
        - que train sert à l'entraînement ;
        - que validation sert à l'évaluation intermédiaire ;
        - que test sert à l'évaluation finale ;
        - le chemin du modèle .pkl généré ;
        - les métriques sauvegardées ;
        - les performances validation et test.

        Ne pas retourner un JSON.
        Retourner uniquement le rapport humain final.
        """,
        expected_output="""
        Rapport humain final de l'entraînement du modèle.
        """,
        agent=agent,
        output_file=report_path
    )