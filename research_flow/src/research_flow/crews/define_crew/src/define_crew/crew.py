from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os
from research_flow.src.research_flow.config import RESEARCH_FLOW_INPUT_VARIABLES

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class DefineCrew():
	input_variables = RESEARCH_FLOW_INPUT_VARIABLES
	"""Define crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	def __post_init__(self):
		self.ensure_output_folder_exists()

	def ensure_output_folder_exists(self):
		"""Ensure the output folder exists."""
		output_folder = self.input_variables["output_folder"]
		if not os.path.exists(output_folder):
			os.makedirs(output_folder)

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def content_writer(self) -> Agent:
		return Agent(
			config=self.agents_config['content_writer'],
			verbose=True
		)

	@agent
	def editor(self) -> Agent:
		return Agent(
			config=self.agents_config['editor'],
			verbose=True
		)

	@agent
	def quality_reviewer(self) -> Agent:
		return Agent(
			config=self.agents_config['quality_reviewer'],
			verbose=True
		)

	@task
	def writing_task(self) -> Task:
		return Task(
			config=self.tasks_config['writing_task'],
		)

	@task
	def editing_task(self) -> Task:
		topic = self.input_variables["topic"]
		audience_level = self.input_variables["audience_level"]
		file_name = f"{topic}_{audience_level}.md".replace(" ", "_")
		output_file_path = os.path.join(self.input_variables["output_folder"], file_name)
		
		return Task(
			config=self.tasks_config['editing_task'],
			output_file=output_file_path
		)

	@task
	def quality_review_task(self) -> Task:
		return Task(
			config=self.tasks_config['quality_review_task'],
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the DefineCrew crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
