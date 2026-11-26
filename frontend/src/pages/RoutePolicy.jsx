import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function RoutePolicy() {
  const [mode, setMode] = useState('权重')
  const [updated, setUpdated] = useState('')
  const [msg, setMsg] = useState('')
  const load = () => api('/选路').then((d) => { setMode(d.模式); setUpdated(d.更新时间) }).catch((e) => setMsg(e.message))
  useEffect(() => { load() }, [])
  const save = async () => {
    try {
      await api('/选路', { method: 'PUT', body: JSON.stringify({ 模式: mode }) })
      setMsg('已保存')
      load()
    } catch (e) { setMsg(e.message) }
  }
  return (
    <div className="panel">
      <h2>择路</h2>
      <div className="row">
        <select value={mode} onChange={(e) => setMode(e.target.value)}>
          <option value="权重">权重</option>
          <option value="强制主路">强制主路</option>
          <option value="强制备路">强制备路</option>
        </select>
        <button type="button" onClick={save}>保存</button>
        <span className="msg">更新时间 {updated || '-'}</span>
      </div>
      <p className="msg">{msg}</p>
    </div>
  )
}
