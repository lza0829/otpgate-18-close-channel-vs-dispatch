import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function Channels() {
  const [rows, setRows] = useState([])
  const [msg, setMsg] = useState('')
  const load = () => api('/通道').then(setRows).catch((e) => setMsg(e.message))
  useEffect(() => { load() }, [])
  const patch = async (id, body) => {
    try {
      await api(`/通道/${id}`, { method: 'PATCH', body: JSON.stringify(body) })
      setMsg('已更新')
      load()
    } catch (e) { setMsg(e.message) }
  }
  return (
    <div className="panel">
      <h2>通道册</h2>
      <p className="msg">主备短信通道登记、启停与恢复</p>
      <div className="table-wrap">
        <table>
          <thead><tr><th>名称</th><th>角色</th><th>状态</th><th>权重</th><th>并发上限</th><th>连续失败</th><th>操作</th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.编号}>
                <td>{r.名称}</td><td>{r.角色}</td><td>{r.状态}</td><td>{r.权重}</td><td>{r.并发上限}</td><td>{r.连续失败}</td>
                <td className="row">
                  <button type="button" className="secondary" onClick={() => patch(r.编号, { 状态: '启用' })}>启用</button>
                  <button type="button" className="secondary" onClick={() => patch(r.编号, { 状态: '停用' })}>停用</button>
                  <button type="button" onClick={() => api(`/通道/${r.编号}/恢复`, { method: 'POST' }).then(load).catch((e) => setMsg(e.message))}>恢复</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="row"><span className="msg">{msg}</span><button type="button" className="secondary" onClick={load}>刷新</button></div>
    </div>
  )
}
