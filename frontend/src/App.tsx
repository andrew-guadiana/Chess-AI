import { useRef, useMemo, useState } from "react"
import { Chess } from "chess.js"
import ChessBoard from "./components/ChessBoard"

const API_URL = "http://localhost:8000/ai-move"

function App() {
  const [game, setGame] = useState(() => new Chess())
  const [thinking, setThinking] = useState(false)

  // Used to ignore stale AI responses
  const requestIdRef = useRef(0)

  const status = useMemo(() => {
    if (game.isCheckmate()) return "Checkmate"
    if (game.isStalemate()) return "Stalemate"
    if (game.isDraw()) return "Draw"
    if (game.isGameOver()) return "Game Over"
    if (thinking) return "Black is thinking..."

    return game.turn() === "w"
      ? "White to move"
      : "Black to move"
  }, [game, thinking])

  async function makeAiMove(fen: string) {
    setThinking(true)

    const requestId = ++requestIdRef.current

    try {
      console.log("SEND", requestId, fen)

      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ fen }),
      })

      const data = await response.json()

      console.log("RECV", requestId, data)

      // Ignore stale responses
      if (requestId !== requestIdRef.current) {
        console.log("Ignoring stale response", requestId)
        return
      }

      if (!data.move) {
        return
      }

      setGame(new Chess(data.fen))
    } catch (error) {
      console.error("AI move failed:", error)
    } finally {
      setThinking(false)
    }
  }

  function handleMove(from: string, to: string) {
    console.log("USER MOVE", from, to)

    if (thinking) return false
    if (game.turn() !== "w") return false

    const next = new Chess(game.fen())

    const move = next.move({
      from,
      to,
      promotion: "q",
    })

    if (!move) return false

    setGame(next)

    setTimeout(() => {
      makeAiMove(next.fen())
    }, 100)

    return true
  }

  function resetGame() {
    // Invalidate all pending AI responses
    requestIdRef.current++

    setThinking(false)
    setGame(new Chess())
  }

  return (
    <div>
      <h1>{status}</h1>

      <main>
        <ChessBoard
          fen={game.fen()}
          onMove={handleMove}
        />
      </main>

      <button onClick={resetGame}>
        New Game
      </button>
    </div>
  )
}

export default App
