import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function Breaker() {
  const [sends, setSends] = useState([])
  const [events, setEvents] = useState([])
  const [msg, setMsg] = useState('')
  const load = async () => {
    try {
      setSends(await api('/投递单'))
      setEvents(await api('/熔断事件'))
    } catch (e) { setMsg(e.message) }
  }
  useEffect(() => { load() }, [])
  const fail = async (id) => {
    try {
      const r = await api(`/投递单/${id}/失败`, { method: 'POST', body: JSON.stringify({ 备注: '页面模拟失败' }) })
      setMsg(JSON.stringify(r))
      load()
    } catch (e) { setMsg(e.message) }
  }
  return (
    <div className="panel">
      <h2>切备</h2>
      <div className="table-wrap">
        <table>
          <thead><tr><th>投递单号</th><th>状态</th><th>通道</th><th>操作</th></tr></thead>
          <tbody>
            {sends.filter((s) => s.状态 === '投递中').map((r) => (
              <tr key={r.编号}>
                <td>{r.投递单号}</td><td>{r.状态}</td><td>{r.通道}</td>
                <td><button type="button" onClick={() => fail(r.编号)}>记失败</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <h2>切备事件</h2>
      <div className="table-wrap">
        <table>
          <thead><tr><th>通道</th><th>动作</th><th>投递单</th><th>时间</th><th>备注</th></tr></thead>
          <tbody>
            {events.map((e) => (
              <tr key={e.编号}><td>{e.通道}</td><td>{e.动作}</td><td>{e.投递单 || '-'}</td><td>{e.时间}</td><td>{e.备注}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="row"><span className="msg">{msg}</span><button type="button" className="secondary" onClick={load}>刷新</button></div>
    </div>
  )
}
