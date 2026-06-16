from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import chess
import math
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MoveRequest(BaseModel):
    fen: str

PIECE_VALUES = {
    chess.PAWN:    100,
    chess.KNIGHT:  300,
    chess.BISHOP:  330,
    chess.ROOK:    500,
    chess.QUEEN:   900,
    chess.KING:      0,
}

def evaluate_board(board: chess.Board) -> int:
    if board.is_checkmate():
        return -10000 if board.turn == chess.WHITE else 10000
    if board.is_stalemate():
        return 0

    score = 0
    for piece in board.piece_map().values():
        value = PIECE_VALUES[piece.piece_type]

        if piece.color == chess.WHITE:
            score += value
        else:
            score -= value

    return score

@app.post("/ai-move")
def ai_move(req: MoveRequest):
    board = chess.Board(req.fen)

    if board.is_game_over():
        return {"move": None, "fen": board.fen()}

    legal_moves = list(board.legal_moves)

    best_move = None
    best_score = float("inf")

    for move in legal_moves:
        board.push(move)
        score = evaluate_board(board)
        board.pop()

        if score < best_score:
            best_score = score
            best_move = move

    board.push(best_move)

    return {
        "move": move.uci(),
        "fen": board.fen(),
    }
