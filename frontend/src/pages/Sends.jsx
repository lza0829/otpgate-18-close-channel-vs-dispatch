import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function Sends() {
  const [rows, setRows] = useState([])
  const [phone, setPhone] = useState('139****6602')
  const [scene, setScene] = useState('登录')
  const [msg, setMsg] = useState('')
  const load = () => api('/投递单').then(setRows).catch((e) => setMsg(e.message))
  useEffect(() => { load() }, [])
  const create = async () => {
    try {
      await api('/投递单', { method: 'POST', body: JSON.stringify({ 手机掩码: phone, 场景: scene }) })
      setMsg('已创建')
      load()
    } catch (e) { setMsg(e.message) }
  }
  const dispatch = async (id) => {
    try {
      const r = await api(`/投递单/${id}/投递`, { method: 'POST' })
      setMsg(`投递：${r.通道}`)
      load()
    } catch (e) { setMsg(e.message) }
  }
  return (
    <div className="panel">
      <h2>验码单</h2>
      <div className="row">
        <input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="手机掩码" />
        <select value={scene} onChange={(e) => setScene(e.target.value)}>
          <option value="登录">登录</option>
          <option value="支付">支付</option>
          <option value="改密">改密</option>
        </select>
        <button type="button" onClick={create}>新建投递单</button>
      </div>
      <div className="table-wrap">
        <table>
          <thead><tr><th>投递单号</th><th>手机掩码</th><th>场景</th><th>状态</th><th>通道</th><th>切备通道</th><th>操作</th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.编号}>
                <td>{r.投递单号}</td><td>{r.手机掩码}</td><td>{r.场景}</td><td>{r.状态}</td><td>{r.通道}</td><td>{r.切备通道}</td>
                <td><button type="button" onClick={() => dispatch(r.编号)} disabled={!['待投递','已切备'].includes(r.状态)}>投递</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="row"><span className="msg">{msg}</span><button type="button" className="secondary" onClick={load}>刷新</button></div>
    </div>
  )
}
