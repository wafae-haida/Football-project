from pathlib import Path
from crewai import Crew, Process

from multi_agent_system.agents.graph_analysis_agent import (
    create_graph_analysis_agent
)

from multi_agent_system.tasks.graph_analysis_tasks import (
    create_graph_analysis_task
)


def run_graph_analysis_crew(
    data_file: str,
    action_batches_dir: str,
    spatial_batches_dir: str
):

    data_path = Path(data_file)
    split_name = data_path.stem.replace("_data", "")

    report_dir = Path("dataset/graph_analysis/reports")
    report_dir.mkdir(parents=True, exist_ok=True)

    report_path = report_dir / f"{split_name}_graph_analysis_report.txt"

    agent = create_graph_analysis_agent()

    task = create_graph_analysis_task(
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
            "data_file": data_file,
            "action_batches_dir": action_batches_dir,
            "spatial_batches_dir": spatial_batches_dir
        }
    )

    return result