import { useState, useEffect } from 'react'

export default function StatsCard({ label, value, color, downloadLink }) {
  const [count, setCount] = useState(0)

  useEffect(() => {
    let start = 0
    const duration = 800
    const steps = 40
    const increment = value / steps
    const timer = setInterval(() => {
      start += increment
      if (start >= value) {
        setCount(value)
        clearInterval(timer)
      } else {
        setCount(Math.floor(start))
      }
    }, duration / steps)
    return () => clearInterval(timer)
  }, [value])

  return (
    <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4 hover:border-[#238636] transition-all duration-300">
      <div className="text-3xl font-bold" style={{ color }}>{count}</div>
      <div className="text-gray-400 text-sm uppercase tracking-wider mt-1">{label}</div>
      {downloadLink && (
        <a href={downloadLink} className="mt-2 inline-block text-xs text-[#238636] hover:text-[#2ea043] transition">
          ↓ Download
        </a>
      )}
    </div>
  )
}