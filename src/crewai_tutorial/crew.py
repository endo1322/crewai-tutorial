from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
# Crew の開始前後にコードを実行したい場合は @before_kickoff / @after_kickoff デコレータを使用できます
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class CrewaiTutorial():
    """CrewaiTutorial crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    # YAML 設定ファイルの詳細:
    # エージェント: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # タスク: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended

    # エージェントにツールを追加する方法:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            verbose=True
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'], # type: ignore[index]
            verbose=True
        )

    # 構造化タスク出力・タスク依存関係・タスクコールバックの詳細:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'], # type: ignore[index]
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """CrewaiTutorial crew を生成する"""
        # ナレッジソースの追加方法:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # @agent デコレータにより自動生成
            tasks=self.tasks,   # @task デコレータにより自動生成
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # 階層型プロセスを使う場合 https://docs.crewai.com/how-to/Hierarchical/
        )
