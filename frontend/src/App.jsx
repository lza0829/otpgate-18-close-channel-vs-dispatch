import React from 'react'
import { NavLink, Route, Routes } from 'react-router-dom'
import Overview from './pages/Overview'
import Channels from './pages/Channels'
import RoutePolicy from './pages/RoutePolicy'
import Sends from './pages/Sends'
import Breaker from './pages/Breaker'
import Receipts from './pages/Receipts'
import Reconcile from './pages/Reconcile'
import Settings from './pages/Settings'
import Audit from './pages/Audit'

const links = [
  ['/', '路况'],
  ['/通道册', '通道册'],
  ['/择路', '择路'],
  ['/验码单', '验码单'],
  ['/切备', '切备'],
  ['/回执簿', '回执簿'],
  ['/轧差', '轧差'],
  ['/渠规', '渠规'],
  ['/事件痕', '事件痕'],
]

export default function App() {
  return (
    <div className="shell">
      <header className="mast">
        <div className="mast-mark" aria-hidden="true" />
        <div className="mast-brand">
          <h1 className="brand">验码渠</h1>
          <p className="brand-sub">验证码通道：注册 · 择路投递 · 熔断切备 · 回执轧差</p>
        </div>
        <nav className="nav">
          {links.map(([to, label]) => (
            <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => (isActive ? 'active' : '')}>
              {label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="main">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/通道册" element={<Channels />} />
          <Route path="/择路" element={<RoutePolicy />} />
          <Route path="/验码单" element={<Sends />} />
          <Route path="/切备" element={<Breaker />} />
          <Route path="/回执簿" element={<Receipts />} />
          <Route path="/轧差" element={<Reconcile />} />
          <Route path="/渠规" element={<Settings />} />
          <Route path="/事件痕" element={<Audit />} />
        </Routes>
      </main>
    </div>
  )
}
