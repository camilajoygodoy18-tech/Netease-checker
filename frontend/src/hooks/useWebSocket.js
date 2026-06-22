import { useState, useEffect, useRef } from 'react'

export default function useWebSocket(userId) {
  const [lastMessage, setLastMessage] = useState(null)
  const wsRef = useRef(null)

  useEffect(() => {
    if (!userId) return
    const ws = new WebSocket(`wss://${window.location.host}/api/ws/${userId}`)
    ws.onmessage = (event) => setLastMessage(event.data)
    wsRef.current = ws
    return () => ws.close()
  }, [userId])

  const sendMessage = (message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(message)
    }
  }

  return { lastMessage, sendMessage }
}