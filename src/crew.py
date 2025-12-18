import os
from typing import List
from dotenv import load_dotenv

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool

from tools.product_search_tool import ProductDataTool
from tools.price_calculating_tool import PricingCalculatorTool
from tools.risk_assessment_tool import RiskAssessmentTool

load_dotenv(override=True)

llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.0
)

product_data_tool = ProductDataTool()
pricing_calculator_tool = PricingCalculatorTool()
risk_assessment_tool = RiskAssessmentTool()

serper_search_tool = SerperDevTool(api_key=os.getenv("SERPER_API_KEY"))

@CrewBase
class QuotationGeneratorAzure1():
    """QuotationGeneratorAzure1 crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def data_fetcher_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['data_fetcher_agent'],
            tools=[product_data_tool],
            verbose=True,
            llm=llm
        )
    @agent
    def pricing_strategy_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['pricing_strategy_agent'],
            tools=[pricing_calculator_tool],
            verbose=True,
            llm=llm
       )
    @agent
    def event_scout_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['event_scout_agent'],
            tools=[serper_search_tool],
            verbose=True,
            llm=llm
        )
    @agent
    def price_impact_analyst_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['price_impact_analyst_agent'],
            verbose=True,
            llm=llm
        )
    @agent
    def approval_logic_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['approval_logic_agent'],
            tools=[risk_assessment_tool],
            verbose=True,
            llm=llm
        )
    @agent
    def discount_strategist_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['discount_strategist_agent'],
            verbose=True,
            llm=llm
        )
    @agent
    def quotation_formatter_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['quotation_formatter_agent'],
            verbose=True,
            llm=llm
        )


    @task
    def data_fetcher_task(self) -> Task:
        return Task(
            config=self.tasks_config['data_fetcher_task'],
            agent=self.data_fetcher_agent(),
            output_file='src/outputs/report_agent_1.md'
        )
    @task
    def pricing_strategy_task(self) -> Task:
        return Task(
            config=self.tasks_config['pricing_strategy_task'],
            agent=self.pricing_strategy_agent(),
            context=[self.data_fetcher_task()],
            output_file='src/outputs/report_agent_2.md'
        )
    @task
    def event_scouting_task(self) -> Task:
        return Task(
            config=self.tasks_config['event_scouting_task'],
            agent=self.event_scout_agent(),
        )
    @task
    def price_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['price_analysis_task'],
            agent=self.price_impact_analyst_agent(),
            context=[self.event_scouting_task()],
            output_file='src/outputs/report_agent_3.md'
        )
    @task
    def assess_risk_task(self) -> Task:
        return Task(
            config=self.tasks_config['assess_risk_task'],
            agent=self.approval_logic_agent(),
            context=[self.pricing_strategy_task()]
        )
    @task
    def strategic_discount_task(self) -> Task:
        return Task(
            config=self.tasks_config['strategic_discount_task'],
            agent=self.discount_strategist_agent(),
            context=[self.pricing_strategy_task(), self.price_analysis_task(), self.assess_risk_task()],
            output_file="src/outputs/report_agent_4.md"
        )
    @task
    def generate_quotation_document_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_quotation_document_task'],
            agent=self.quotation_formatter_agent(),
            context=[self.strategic_discount_task()],
            output_file="src/outputs/report_agent_5.md"
        )



    @crew
    def crew(self) -> Crew:
        """Creates the QuotationGeneratorAzure1 crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
