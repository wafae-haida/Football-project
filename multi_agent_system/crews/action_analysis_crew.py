from pathlib import Path
from crewai import Crew, Process

from multi_agent_system.agents.action_analysis_agent import (
    create_action_analysis_agent
)

from multi_agent_system.tasks.action_analysis_tasks import (
    create_action_analysis_task
)


def run_action_analysis_crew(data_file: str):

    data_path = Path(data_file)
    split_name = data_path.stem.replace("_data", "")

    report_dir = Path("dataset/action_analysis/reports")
    report_dir.mkdir(parents=True, exist_ok=True)

    report_path = report_dir / f"{split_name}_action_analysis_report.txt"

    agent = create_action_analysis_agent()

    task = create_action_analysis_task(
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
            "data_file": data_file
        }
    )

    return result