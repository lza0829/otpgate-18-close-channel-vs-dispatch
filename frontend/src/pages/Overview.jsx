import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function Overview() {
  const [data, setData] = useState(null)
  const [err, setErr] = useState('')
  const load = () => api('/总览').then(setData).catch((e) => setErr(e.message))
  useEffect(() => { load() }, [])
  if (err) return <div className="panel err">{err}</div>
  if (!data) return <div className="panel">加载中</div>
  const d = data.分布 || {}
  return (
    <div className="panel">
      <h2>路况</h2>
      <div className="grid">
        {Object.entries(d).map(([k, v]) => (
          <div className="stat" key={k}><div className="n">{v}</div><div className="l">{k}</div></div>
        ))}
      </div>
      <h2>在途投递</h2>
      <div className="table-wrap">
        <table>
          <thead><tr><th>投递单号</th><th>手机掩码</th><th>场景</th><th>状态</th><th>当前通道</th></tr></thead>
          <tbody>
            {(data.在途 || []).map((r) => (
              <tr key={r.编号}><td>{r.投递单号}</td><td>{r.手机掩码}</td><td>{r.场景}</td><td>{r.状态}</td><td>{r.当前通道 || '-'}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
      <h2>通道态势</h2>
      <div className="table-wrap">
        <table>
          <thead><tr><th>代号</th><th>名称</th><th>角色</th><th>状态</th><th>权重</th><th>连续失败</th></tr></thead>
          <tbody>
            {(data.通道 || []).map((c) => (
              <tr key={c.代号}><td>{c.代号}</td><td>{c.名称}</td><td>{c.角色}</td><td>{c.状态}</td><td>{c.权重}</td><td>{c.连续失败}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="row"><button type="button" className="secondary" onClick={load}>刷新</button></div>
    </div>
  )
}
