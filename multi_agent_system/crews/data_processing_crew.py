from crewai import Crew, Process

from multi_agent_system.agents.data_processing_agent import create_data_processing_agent
from multi_agent_system.tasks.data_processing_tasks import create_data_processing_task


def run_data_processing_crew(input_path: str):
    agent = create_data_processing_agent()

    task = create_data_processing_task(
        agent=agent,
        input_path=input_path
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()

    return result