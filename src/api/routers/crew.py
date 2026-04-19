import asyncio
import json
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from api.schemas.crew import JobResponse, RunRequest, StatusResponse
from api.services import job_store
from crewai_tutorial.crew import CrewaiTutorial

router = APIRouter()

TASK_CONFIG = [
    {
        "label": "リサーチ",
        "start_detail": "「{topic}」に関する最新情報を収集・調査します",
    },
    {
        "label": "レポート作成",
        "start_detail": "収集した情報をもとに詳細なレポートを作成します",
    },
]


def _format_step(output) -> str | None:
    """エージェントのステップ出力を人が読める文字列に変換する。"""
    try:
        # ツール使用（AgentAction 相当）
        if hasattr(output, 'tool') and hasattr(output, 'tool_input'):
            tool_input = str(output.tool_input)[:120]
            return f"{output.tool} → {tool_input}"
        # 最終回答（AgentFinish 相当）は task_completed でカバーするためスキップ
        if hasattr(output, 'return_values'):
            return None
        text = str(output).strip()
        if not text or text == 'None':
            return None
        # 文字列表現が AgentFinish / AgentAction の場合もスキップ
        if text.startswith('AgentFinish(') or text.startswith('AgentAction('):
            return None
        return text[:150] + ("..." if len(text) > 150 else "")
    except Exception:
        return None


@router.post("/run", response_model=JobResponse)
async def run(request: RunRequest):
    job_id = str(uuid.uuid4())
    job_store.create(job_id)

    async def _execute():
        try:
            inputs = {
                "topic": request.topic,
                "current_year": str(datetime.now().year),
            }

            crew = CrewaiTutorial().crew()
            current_task = [0]  # ステップコールバックで参照するタスクインデックス

            # エージェントのステップごとにイベントを発行
            def step_callback(output):
                message = _format_step(output)
                if message:
                    job_store.publish(job_id, {
                        "type": "agent_step",
                        "taskIndex": current_task[0],
                        "message": message,
                    })

            for agent in crew.agents:
                agent.step_callback = step_callback

            # タスク完了コールバックを設定
            task_labels = [t["label"] for t in TASK_CONFIG]

            for i, task in enumerate(crew.tasks):
                label = task_labels[i] if i < len(task_labels) else f"タスク {i + 1}"
                next_config = TASK_CONFIG[i + 1] if i + 1 < len(TASK_CONFIG) else None

                def make_callback(idx: int, lbl: str, n_config: dict | None):
                    def callback(output):
                        current_task[0] = idx + 1
                        raw = output.raw if hasattr(output, 'raw') else str(output)
                        job_store.publish(job_id, {
                            "type": "task_completed",
                            "taskIndex": idx,
                            "taskLabel": lbl,
                            "detail": str(raw)[:400],
                        })
                        if n_config:
                            job_store.publish(job_id, {
                                "type": "task_started",
                                "taskIndex": idx + 1,
                                "taskLabel": n_config["label"],
                                "detail": n_config["start_detail"].format(topic=request.topic),
                            })
                    return callback

                task.callback = make_callback(i, label, next_config)

            # 最初のタスク開始を発行
            job_store.publish(job_id, {
                "type": "task_started",
                "taskIndex": 0,
                "taskLabel": task_labels[0],
                "detail": TASK_CONFIG[0]["start_detail"].format(topic=request.topic),
            })

            result = await crew.akickoff(inputs=inputs)
            job_store.complete(job_id, str(result))
            job_store.publish(job_id, {
                "type": "crew_completed",
                "message": "すべてのタスクが完了しました",
                "result": str(result),
            })

        except Exception as e:
            job_store.fail(job_id, str(e))
            job_store.publish(job_id, {"type": "error", "message": str(e)})

        finally:
            job_store.publish(job_id, None)

    asyncio.create_task(_execute())
    return JobResponse(job_id=job_id)


@router.get("/stream/{job_id}")
async def stream(job_id: str):
    queue = job_store.get_event_queue(job_id)
    if not queue:
        raise HTTPException(status_code=404, detail="Job not found")

    async def generator():
        while True:
            event = await queue.get()
            if event is None:
                break
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/status/{job_id}", response_model=StatusResponse)
async def status(job_id: str):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return StatusResponse(
        job_id=job.job_id,
        status=job.status,
        result=job.result,
        error=job.error,
    )
