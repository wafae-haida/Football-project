from pathlib import Path
from crewai import Crew, Process

from multi_agent_system.agents.model_training_agent import (
    create_model_training_agent
)

from multi_agent_system.tasks.model_training_tasks import (
    create_model_training_task
)


def run_model_training_crew():

    report_dir = Path("model/metrics")
    report_dir.mkdir(parents=True, exist_ok=True)

    report_path = report_dir / "model_training_report.txt"

    agent = create_model_training_agent()

    task = create_model_training_task(
        agent=agent,
        report_path=str(report_path)
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff(
        inputs={
            "train_action_batches_dir": "dataset/action_analysis/data/train_batches",
            "validation_action_batches_dir": "dataset/action_analysis/data/validation_batches",
            "test_action_batches_dir": "dataset/action_analysis/data/test_batches",

            "train_spatial_batches_dir": "dataset/spatial_analysis/data/train_batches",
            "validation_spatial_batches_dir": "dataset/spatial_analysis/data/validation_batches",
            "test_spatial_batches_dir": "dataset/spatial_analysis/data/test_batches",

            "train_graph_batches_dir": "dataset/graph_analysis/data/train_batches",
            "validation_graph_batches_dir": "dataset/graph_analysis/data/validation_batches",
            "test_graph_batches_dir": "dataset/graph_analysis/data/test_batches"
        }
    )

    return result