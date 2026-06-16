from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import chess

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

def ordered_moves(board: chess.Board):
    moves = list(board.legal_moves)

    def move_score(move):
        score = 0

        if board.is_capture(move):
            score += 1000

            captured = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)

            if captured and attacker:
                score += PIECE_VALUES[captured.piece_type] - PIECE_VALUES[attacker.piece_type] // 10

        if move.promotion:
            score += 800
        
        return score
    return sorted(moves, key=move_score, reverse=True)

def evaluate_board(board: chess.Board) -> int: 
    if board.is_checkmate():
        return -100000 if board.turn == chess.WHITE else 100000
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
        

def alphabeta(board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool) -> int:
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing:
        best_score = float("-inf")

        for move in ordered_moves(board):
            board.push(move)
            score = alphabeta(board, depth - 1, alpha, beta, False)
            board.pop()

            best_score = max(best_score, score)
            alpha = max(alpha, best_score)

            if alpha >= beta:
                break

        return best_score

    else:
        best_score = float("inf")

        for move in ordered_moves(board):
            board.push(move)
            score = alphabeta(board, depth - 1, alpha, beta, True)

            board.pop()

            best_score = min(best_score, score)
            beta = min(beta, best_score)

            if alpha >= beta:
                break
        
        return best_score


@app.post("/ai-move")
def ai_move(req: MoveRequest):
    board = chess.Board(req.fen)

    if board.is_game_over():
        return {"move": None, "fen": board.fen()}

    best_move = None
    best_score = float("inf")

    for move in ordered_moves(board):
        board.push(move)
        
        score = alphabeta(board=board, depth=3, alpha=float("-inf"), beta=float("inf"), maximizing=True)
        board.pop()

        if score < best_score:
            best_score = score
            best_move = move

    board.push(best_move)

    return {
        "move": best_move.uci(),
        "fen": board.fen(),
    }
