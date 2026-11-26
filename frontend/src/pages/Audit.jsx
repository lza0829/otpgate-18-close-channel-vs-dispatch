import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function Audit() {
  const [rows, setRows] = useState([])
  const [err, setErr] = useState('')
  const load = () => api('/审计').then(setRows).catch((e) => setErr(e.message))
  useEffect(() => { load() }, [])
  if (err) return <div className="panel err">{err}</div>
  return (
    <div className="panel">
      <h2>事件痕</h2>
      <div className="table-wrap">
        <table>
          <thead><tr><th>类别</th><th>关联</th><th>动作</th><th>时间</th><th>备注</th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.编号}><td>{r.类别}</td><td>{r.关联 ?? '-'}</td><td>{r.动作}</td><td>{r.时间}</td><td>{r.备注}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="row"><button type="button" className="secondary" onClick={load}>刷新</button></div>
    </div>
  )
}
