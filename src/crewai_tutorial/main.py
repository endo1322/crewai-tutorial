#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from crewai_tutorial.crew import CrewaiTutorial

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# このファイルはローカルで crew を実行するためのエントリポイントです。
# 不要なロジックは追加せず、テストしたい inputs を設定してください。
# タスクおよびエージェント情報は自動的に補間されます。

def run():
    """
    crew を実行する。
    """
    inputs = {
        'topic': 'AI LLMs',
        'current_year': str(datetime.now().year)
    }

    try:
        CrewaiTutorial().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"crew の実行中にエラーが発生しました: {e}")


def train():
    """
    指定したイテレーション回数だけ crew をトレーニングする。
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        CrewaiTutorial().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"crew のトレーニング中にエラーが発生しました: {e}")

def replay():
    """
    特定のタスクから crew の実行を再生する。
    """
    try:
        CrewaiTutorial().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"crew の再生中にエラーが発生しました: {e}")

def test():
    """
    crew の実行をテストし、結果を返す。
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }

    try:
        CrewaiTutorial().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"crew のテスト中にエラーが発生しました: {e}")

def run_with_trigger():
    """
    トリガーペイロードを受け取って crew を実行する。
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("トリガーペイロードが指定されていません。JSON ペイロードを引数として渡してください。")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("引数として渡された JSON ペイロードが不正です。")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "topic": "",
        "current_year": ""
    }

    try:
        result = CrewaiTutorial().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"トリガーを使った crew の実行中にエラーが発生しました: {e}")
