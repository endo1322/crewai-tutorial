import { useState, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import './App.css'

const API_BASE = 'http://localhost:8000'

type Status = 'idle' | 'running' | 'done' | 'error'

type CrewEvent =
  | { type: 'task_started';   taskIndex: number; taskLabel: string; detail: string }
  | { type: 'agent_step';     taskIndex: number; message: string }
  | { type: 'task_completed'; taskIndex: number; taskLabel: string; detail: string }
  | { type: 'crew_completed'; message: string; result: string }
  | { type: 'error';          message: string }

type Step = { kind: 'start' | 'step' | 'done'; text: string }

type TaskSection = {
  label: string
  steps: Step[]
  status: 'running' | 'done'
  isOpen: boolean
}

export default function App() {
  const [topic, setTopic] = useState('')
  const [status, setStatus] = useState<Status>('idle')
  const [sections, setSections] = useState<TaskSection[]>([])
  const [result, setResult] = useState('')
  const [error, setError] = useState('')
  const esRef = useRef<EventSource | null>(null)

  const toggleSection = (index: number) => {
    setSections((prev) =>
      prev.map((s, i) => (i === index ? { ...s, isOpen: !s.isOpen } : s))
    )
  }

  const handleEvent = (event: CrewEvent) => {
    switch (event.type) {
      case 'task_started':
        setSections((prev) => [
          ...prev,
          {
            label: event.taskLabel,
            steps: [{ kind: 'start', text: event.detail }],
            status: 'running',
            isOpen: true,
          },
        ])
        break

      case 'agent_step':
        setSections((prev) =>
          prev.map((s, i) =>
            i === event.taskIndex
              ? { ...s, steps: [...s.steps, { kind: 'step', text: event.message }] }
              : s
          )
        )
        break

      case 'task_completed':
        setSections((prev) =>
          prev.map((s, i) =>
            i === event.taskIndex
              ? {
                  ...s,
                  steps: [...s.steps, { kind: 'done', text: event.detail }],
                  status: 'done',
                  isOpen: false,
                }
              : s
          )
        )
        break

      case 'crew_completed':
        setResult(event.result)
        setStatus('done')
        break

      case 'error':
        setError(event.message)
        setStatus('error')
        break
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!topic.trim()) return

    esRef.current?.close()
    setStatus('running')
    setSections([])
    setResult('')
    setError('')

    try {
      const res = await fetch(`${API_BASE}/crew/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      })
      const { job_id } = await res.json()

      const es = new EventSource(`${API_BASE}/crew/stream/${job_id}`)
      esRef.current = es

      es.onmessage = (e) => {
        const event: CrewEvent = JSON.parse(e.data)
        handleEvent(event)
        if (event.type === 'crew_completed' || event.type === 'error') {
          es.close()
        }
      }

      es.onerror = () => {
        setError('サーバーとの接続が切れました')
        setStatus('error')
        es.close()
      }
    } catch (err) {
      setError(String(err))
      setStatus('error')
    }
  }

  return (
    <div className="container">
      <header>
        <h1>CrewAI リサーチエージェント</h1>
        <p>トピックを入力すると、AIエージェントがリサーチしてレポートを生成します。</p>
      </header>

      <form onSubmit={handleSubmit} className="form">
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="例: 生成AI の最新動向"
          disabled={status === 'running'}
          className="input"
        />
        <button
          type="submit"
          disabled={status === 'running' || !topic.trim()}
          className="button"
        >
          {status === 'running' ? '実行中...' : 'リサーチ開始'}
        </button>
      </form>

      {status === 'error' && (
        <div className="status-box error">エラー: {error}</div>
      )}

      {/* タスクセクション */}
      {sections.length > 0 && (
        <div className="task-sections">
          {sections.map((section, i) => (
            <div key={i} className={`task-section ${section.status}`}>
              <button
                className="task-header"
                onClick={() => toggleSection(i)}
              >
                <span className={`chevron ${section.isOpen ? 'open' : ''}`}>›</span>
                <span className="task-label">{section.label}</span>
                <span className={`task-badge ${section.status}`}>
                  {section.status === 'running' ? (
                    <><span className="spinner small" /> 実行中</>
                  ) : (
                    <>✓ 完了</>
                  )}
                </span>
              </button>

              {section.isOpen && (
                <ul className="step-list">
                  {section.steps.map((step, j) => (
                    <li key={j} className={`step-item ${step.kind}`}>
                      <span className="step-icon">
                        {step.kind === 'start' && '▶'}
                        {step.kind === 'step'  && '·'}
                        {step.kind === 'done'  && '✓'}
                      </span>
                      <span className="step-text">{step.text}</span>
                    </li>
                  ))}
                  {section.status === 'running' && (
                    <li className="step-item pending">
                      <span className="spinner small" />
                      <span className="step-text">処理中...</span>
                    </li>
                  )}
                </ul>
              )}
            </div>
          ))}
        </div>
      )}

      {status === 'done' && (
        <article className="result">
          <ReactMarkdown>{result}</ReactMarkdown>
        </article>
      )}
    </div>
  )
}
