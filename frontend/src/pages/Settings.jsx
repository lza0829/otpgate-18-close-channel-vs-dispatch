import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function Settings() {
  const [items, setItems] = useState({})
  const [msg, setMsg] = useState('')
  const load = () => api('/设置').then(setItems).catch((e) => setMsg(e.message))
  useEffect(() => { load() }, [])
  const save = async () => {
    try {
      await api('/设置', { method: 'PUT', body: JSON.stringify({ 项: items }) })
      setMsg('已保存')
      load()
    } catch (e) { setMsg(e.message) }
  }
  return (
    <div className="panel">
      <h2>渠规</h2>
      {Object.entries(items).map(([k, v]) => (
        <div className="row" key={k}>
          <span style={{ minWidth: 140 }}>{k}</span>
          <select value={v} onChange={(e) => setItems({ ...items, [k]: e.target.value })}>
            <option value="是">是</option>
            <option value="否">否</option>
          </select>
        </div>
      ))}
      <div className="row"><button type="button" onClick={save}>保存</button><span className="msg">{msg}</span></div>
    </div>
  )
}
