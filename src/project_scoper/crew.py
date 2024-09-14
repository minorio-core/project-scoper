from typing import List
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from crewai_tools import SerplyNewsSearchTool, SerplyWebpageToMarkdownTool, SerplyWebSearchTool
from pydantic import BaseModel, Field


class InvestmentReport(BaseModel):
	"""Investment Report Model"""
	company: str = Field(..., description="Company name")
	stock_symbol: str = Field(..., description="Stock symbol")
	stock_price: float = Field(..., description="Stock price")
	date: str = Field(..., description="Date of the report")
	business_model: str = Field(..., description="How does the company make money")
	pricing_power: str = Field(..., description="What kind of pricing power does the company have")
	cost_advantage: str = Field(..., description="What kind of cost advantage does the company have")
	scale_advantage: str = Field(..., description="What kind of scale advantage does the company have")
	market_dominance: str = Field(..., description="How dominant is the company in its market")
	demand_consistency: str = Field(..., description="How consistent is the demand for the company's products")
	managerial_quality: str = Field(..., description="How good is the management team")

@CrewBase
class ProjectScoperCrew():
	"""InvestmentThesis crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def financial_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['financial_analyst'],
			tools=[SerperDevTool(), ScrapeWebsiteTool(), SerplyWebpageToMarkdownTool(), SerplyWebSearchTool()],
			verbose=True,
			memory=False,
		) #TODO CalculatorTools.calculate,SECTools.search_10q,SECTools.search_10k

	@agent
	def business_strategist(self) -> Agent:
		return Agent(
			config=self.agents_config['business_strategist'],
			tools=[SerperDevTool(), ScrapeWebsiteTool()],
			verbose=True,
			memory=False
		) #TODO CalculatorTools.calculate,SECTools.search_10q,SECTools.search_10k


	@agent
	def investment_advisor(self) -> Agent:
		return Agent(
			config=self.agents_config['investment_advisor'],
			verbose=True,
			memory=False
			)
	#TODO     BrowserTools.scrape_and_summarize_website, SearchTools.search_internet, SearchTools.search_news,
        #CalculatorTools.calculate, YahooFinanceNewsTool()


	@agent
	def research_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['research_analyst'],
			tools=[SerperDevTool(), ScrapeWebsiteTool(), SerplyNewsSearchTool(), SerplyWebpageToMarkdownTool(),
		  SerplyWebSearchTool()],
			verbose=True,
			memory=False
		) #TODO SearchTools.search_internet, SearchTools.search_news, YahooFinanceNewsTool(), SECTools.search_10q, SECTools.search_10k

	@task
	def financial_analysis_task(self) -> Task:
		return Task(
			config=self.tasks_config['financial_analysis_task'],
			agent=self.financial_analyst()
		)
		
	@task
	def competition_analysis_task(self) -> Task:
		return Task(
			config=self.tasks_config['competition_analysis_task'],
			agent=self.business_strategist()
#			output_json=MarketStrategy
		)


	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
			agent=self.research_analyst()
		)

	@task
	def filing_analysis_task(self) -> Task:
		return Task(
			config=self.tasks_config['filing_analysis_task'],
			agent=self.financial_analyst()
#			output_json=MarketStrategy
		)


	@task
	def investment_recommendation_task(self) -> Task:
		return Task(
			config=self.tasks_config['investment_recommendation_task'],
			agent=self.investment_advisor(),
			context=[self.research_task(), self.financial_analysis_task(), self.filing_analysis_task(), self.competition_analysis_task()],
	   		output_json=InvestmentReport
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the MarketingPosts crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks= self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			#planning=True,
			verbose=True,
			output_log_file='output.log',
			log_file='crewai_logs.txt'
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)



	