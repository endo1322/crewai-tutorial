import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import './App.css'

const API_BASE = 'http://localhost:8000'

type Status = 'idle' | 'running' | 'done' | 'error'

async function pollStatus(jobId: string): Promise<{ result?: string; error?: string }> {
  while (true) {
    const res = await fetch(`${API_BASE}/crew/status/${jobId}`)
    const data = await res.json()
    if (data.status === 'done') return { result: data.result }
    if (data.status === 'error') return { error: data.error }
    await new Promise((r) => setTimeout(r, 5000))
  }
}

export default function App() {
  const [topic, setTopic] = useState('')
  const [status, setStatus] = useState<Status>('idle')
  const [result, setResult] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!topic.trim()) return

    setStatus('running')
    setResult('')
    setError('')

    try {
      const res = await fetch(`${API_BASE}/crew/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      })
      const { job_id } = await res.json()
      const outcome = await pollStatus(job_id)

      if (outcome.result) {
        setResult(outcome.result)
        setStatus('done')
      } else {
        setError(outcome.error ?? '不明なエラーが発生しました')
        setStatus('error')
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
        <button type="submit" disabled={status === 'running' || !topic.trim()} className="button">
          {status === 'running' ? '実行中...' : 'リサーチ開始'}
        </button>
      </form>

      {status === 'running' && (
        <div className="status-box running">
          <span className="spinner" />
          エージェントがリサーチ中です。数分かかることがあります...
        </div>
      )}

      {status === 'error' && (
        <div className="status-box error">
          エラー: {error}
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
