import { useEffect, useMemo, useState } from 'react'
import { Chess } from 'chess.js'
import ChessBoard from './components/ChessBoard'

function App() {
  const [game, setGame] = useState(() => new Chess());

  const status = useMemo(() => {
    if (game.isCheckmate()) return "Checkmate"
    if (game.isStalemate()) return "Stalemate"
    if (game.isDraw()) return "Draw"
    if (game.isGameOver()) return "Game Over"
      return game.turn() === "w" ? "White to move" : "Black to move"
  }, [game]);

  function handleMove(from: string, to: string) {
    const next = new Chess(game.fen())

    const move = next.move({
      from, 
      to,
      promotion: "q",
    })

    if (!move) return false
    setGame(next)
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
