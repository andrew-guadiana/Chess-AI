import { Chessboard } from "react-chessboard";

type ChessBoardProps = {
  fen: string;
  onMove: (from: string, to: string) => boolean
}

export default function ChessBoard({ fen, onMove }: ChessBoardProps) {
  const chessboardOptions = {
    position: fen,
    onPieceDrop: ({
      sourceSquare,
      targetSquare,
    }: {
      sourceSquare: string
      targetSquare: string | null
    }) => {
      if (!targetSquare) return false
        return onMove(sourceSquare, targetSquare)
    },
    id: "chessboard",
  }

  return (
    <Chessboard options={chessboardOptions}/>
  )
}
