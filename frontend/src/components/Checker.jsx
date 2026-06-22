import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import StatsCard from './StatsCard'
import useWebSocket from '../hooks/useWebSocket'

export default function Checker() {
  const { user } = useAuth()
  const [combo, setCombo] = useState('')
  const [proxies, setProxies] = useState('')
  const [format, setFormat] = useState('email:password')
  const [captchaMode, setCaptchaMode] = useState('auto')
  const [stats, setStats] = useState({ working: 0, invalid: 0, banned: 0, errors: 0 })
  const [isChecking, setIsChecking] = useState(false)
  const { lastMessage, sendMessage } = useWebSocket(user?.id)

  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage)
        if (data.type === 'stats') {
          setStats(data.payload)
        }
      } catch (e) {}
    }
  }, [lastMessage])

  const startCheck = () => {
    if (!combo.trim()) return
    setIsChecking(true)
    const comboLines = combo.split('\n').filter(l => l.trim())
    const proxyLines = proxies.split('\n').filter(l => l.trim())
    sendMessage(JSON.stringify({
      action: 'start_check',
      combos: comboLines,
      proxies: proxyLines,
      format,
      captchaMode
    }))
  }

  return (
    <div className="min-h-screen bg-[#0d1117] text-[#e6edf3] p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Panel - Checker Controls */}
          <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <span className="text-[#238636]">⚡</span> Checker
            </h2>
            {/* Format selector */}
            <div className="mb-4">
              <label className="block text-gray-400 text-sm mb-1">Format</label>
              <select 
                value={format} 
                onChange={(e) => setFormat(e.target.value)}
                className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-[#e6edf3]"
              >
                <option value="email:password">email:password</option>
                <option value="user:pass">user:pass</option>
                <option value="user:pass:extra">user:pass:extra</option>
              </select>
            </div>
            {/* Combo paste */}
            <div className="mb-4">
              <label className="block text-gray-400 text-sm mb-1">Combo List</label>
              <textarea
                value={combo}
                onChange={(e) => setCombo(e.target.value)}
                className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-[#e6edf3] h-40"
                placeholder="email:password&#10;email2:password2"
              />
            </div>
            {/* Proxies */}
            <div className="mb-4">
              <label className="block text-gray-400 text-sm mb-1">Proxies (optional)</label>
              <textarea
                value={proxies}
                onChange={(e) => setProxies(e.target.value)}
                className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-[#e6edf3] h-24"
                placeholder="user:pass@ip:port&#10;ip:port"
              />
            </div>
            {/* Captcha mode */}
            <div className="mb-4">
              <label className="block text-gray-400 text-sm mb-1">Captcha Mode</label>
              <div className="flex gap-2 flex-wrap">
                {['auto', 'file', 'api', 'capmonster'].map(mode => (
                  <button
                    key={mode}
                    onClick={() => setCaptchaMode(mode)}
                    className={`px-4 py-1 rounded-lg text-sm border ${
                      captchaMode === mode 
                        ? 'border-[#238636] bg-[#238636] text-white' 
                        : 'border-[#30363d] text-gray-400 hover:border-gray-500'
                    } transition`}
                  >
                    {mode.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
            {/* Start button */}
            <button
              onClick={startCheck}
              disabled={isChecking || !combo.trim()}
              className="w-full bg-[#238636] hover:bg-[#2ea043] text-white font-bold py-3 rounded-lg transition disabled:opacity-50"
            >
              {isChecking ? 'Checking...' : '▶ Start Check'}
            </button>
          </div>

          {/* Right Panel - Stats */}
          <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-6">
            <h2 className="text-xl font-bold mb-4">📊 Session Stats</h2>
            <div className="grid grid-cols-2 gap-4">
              <StatsCard label="Working" value={stats.working} color="#238636" downloadLink="/api/download/working" />
              <StatsCard label="Invalid" value={stats.invalid} color="#d29922" downloadLink="/api/download/invalid" />
              <StatsCard label="Banned" value={stats.banned} color="#da3633" downloadLink="/api/download/banned" />
              <StatsCard label="Errors" value={stats.errors} color="#8b949e" downloadLink="/api/download/errors" />
            </div>
            <div className="mt-6 text-center text-gray-500 text-sm">
              <span className="inline-block animate-pulse">🔄 Unlimited Retries</span>
            </div>
            {/* Progress / limit indicator */}
            <div className="mt-4 p-3 bg-[#0d1117] border border-[#30363d] rounded-lg">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Remaining Checks</span>
                <span className="text-[#238636]">{user?.check_limit - user?.checks_used || 0}</span>
              </div>
              <div className="w-full bg-[#0d1117] h-1.5 rounded-full mt-1">
                <div 
                  className="bg-[#238636] h-1.5 rounded-full transition-all"
                  style={{ width: `${((user?.checks_used || 0) / (user?.check_limit || 1)) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Results Tabs */}
        <div className="mt-6 bg-[#161b22] border border-[#30363d] rounded-xl p-6">
          <div className="flex gap-4 border-b border-[#30363d] pb-2">
            {['Working', 'Invalid', 'Banned', 'Retries'].map(tab => (
              <button key={tab} className="text-sm text-gray-400 hover:text-white px-3 py-1 border-b-2 border-transparent hover:border-[#238636] transition">
                {tab}
              </button>
            ))}
          </div>
          <div className="mt-4 text-gray-500 text-center py-8">
            Results will appear here after checking starts.
          </div>
        </div>
      </div>
    </div>
  )
}