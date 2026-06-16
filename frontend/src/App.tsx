import { useEffect, useMemo, useState } from 'react'
import { Chess } from 'chess.js'
import ChessBoard from './components/ChessBoard'

const API_URL = "http://localhost:8000/ai-move"

function App() {
  const [game, setGame] = useState(() => new Chess());
  const [thinking, setThinking] = useState(false)

  const status = useMemo(() => {
    if (game.isCheckmate()) return "Checkmate"
    if (game.isStalemate()) return "Stalemate"
    if (game.isDraw()) return "Draw"
    if (game.isGameOver()) return "Game Over"
    if (thinking) return "Black is thinking..."
      return game.turn() === "w" ? "White to move" : "Black to move"
  }, [game, thinking]);

  async function makeAiMove(fen: string) {
    setThinking(true)

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          fen,
          depth: 2,
        }),
      })

      const data = await response.json()

      if (!data.move) {
        setThinking(false)
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
    setGame(new Chess())
  }

  return (
    <div>
    <h1> {status} </h1>
    <main>
    <ChessBoard fen={game.fen()} onMove={handleMove}/>
    </main>

    <button onClick={resetGame}>
    New Game
    </button>
    </div>


  )
}

export default App
