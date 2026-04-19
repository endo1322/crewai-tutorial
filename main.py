
from crewai import Agent, Crew, Task
from dotenv import load_dotenv

load_dotenv(override=True)

question = input("質問を入力してください: ")

researcher = Agent(
    role="Research Analyst",
    goal="与えられたトピックについて簡潔にまとめる",
    backstory="あなたは情報収集と要約が得意なアナリストです。",
    verbose=True,
    llm="gpt-4o-mini",
)

task = Task(
    description="{question}",
    expected_output="日本語で回答してください",
    agent=researcher,
    human_input=True,
)

crew = Crew(agents=[researcher], tasks=[task], verbose=True, tracing=True)

result = crew.kickoff(inputs={"question": question})
