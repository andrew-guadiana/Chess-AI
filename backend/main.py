from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import chess
import time

app = FastAPI()
POS_INF = float("inf")
NEG_INF = float("-inf")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MoveRequest(BaseModel):
    fen: str

class SearchTimeout(Exception):
    pass

PIECE_VALUES = {
    chess.PAWN:    100,
    chess.KNIGHT:  300,
    chess.BISHOP:  330,
    chess.ROOK:    500,
    chess.QUEEN:   900,
    chess.KING:      0,
}

KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10,-20,-20, 10, 10,  5,
     5, -5,-10,  0,  0,-10, -5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5,  5, 10, 25, 25, 10,  5,  5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
     0,  0,  0,  0,  0,  0,  0,  0
]

BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

ROOK_TABLE = [
     0,  0,  5, 10, 10,  5,  0,  0,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     5, 10, 10, 10, 10, 10, 10,  5,
     0,  0,  5, 10, 10,  5,  0,  0
]

KING_TABLE = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20
]

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

def noisy_moves(board: chess.Board):
    moves = []

    for move in board.legal_moves:
        if board.is_capture(move) or move.promotion:
            moves.append(move)
            
    return sorted(moves, key=lambda move: (
        1000 if board.is_capture(move) else 0
        ) + (
            800 if move.promotion else 0
            ), reverse=True)

def quiescence(board: chess.Board, alpha: float, beta: float, maximizing: bool, end_time: float, depth=3) -> int:
    if time.perf_counter() >= end_time:
        raise SearchTimeout

    stand_pat = evaluate_board(board)

    if depth <= 0:
        return stand_pat


    if maximizing:
        if stand_pat >= beta:
            return stand_pat

        alpha = max(alpha, stand_pat)

    else:
        if stand_pat <= alpha:
            return stand_pat

        beta = min(beta, stand_pat)

    for move in noisy_moves(board):
        board.push(move)

        try:
            score = quiescence(board, alpha, beta, not maximizing, end_time, depth - 1)
        finally:
            board.pop()

        if maximizing:
            alpha = max(alpha, score)

            if alpha >= beta:
                break
        else:
            beta = min(beta, score)

            if alpha >= beta:
                break

    return alpha if maximizing else beta

    

def evaluate_board(board: chess.Board) -> int: 
    if board.is_checkmate():
        return -100000 if board.turn == chess.WHITE else 100000
    if board.is_stalemate() or board.is_insufficient_material(): #or board.can_claim_threefold_repetition() or board.can_claim_fifty_moves():
        return 0

    score = 0
    for square, piece in board.piece_map().items():
        value = PIECE_VALUES[piece.piece_type]
        pst_bonus = 0

        if   piece.piece_type == chess.PAWN:
            pst_bonus = PAWN_TABLE[square] if piece.color == chess.WHITE else PAWN_TABLE[chess.square_mirror(square)]
        elif piece.piece_type == chess.KNIGHT:
            pst_bonus = KNIGHT_TABLE[square] if piece.color == chess.WHITE else KNIGHT_TABLE[chess.square_mirror(square)]
        elif piece.piece_type == chess.BISHOP:
            pst_bonus = BISHOP_TABLE[square] if piece.color == chess.WHITE else BISHOP_TABLE[chess.square_mirror(square)]
        elif piece.piece_type == chess.ROOK:  
            pst_bonus = ROOK_TABLE[square] if piece.color == chess.WHITE else ROOK_TABLE[chess.square_mirror(square)]
        elif piece.piece_type == chess.KING:  
            pst_bonus = KING_TABLE[square] if piece.color == chess.WHITE else KING_TABLE[chess.square_mirror(square)]

        if piece.color == chess.WHITE:
            score += value + pst_bonus
        else:
            score -= value + pst_bonus

    return score
        

def alphabeta(board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool, end_time: float) -> int:
    if time.perf_counter() >= end_time:
        raise SearchTimeout

    if board.is_game_over():
        return evaluate_board(board)

    if depth == 0:
        return quiescence(board, alpha, beta, maximizing, end_time)

    if maximizing:
        best_score = NEG_INF

        for move in ordered_moves(board):
            print("testing ordered moves...")
            board.push(move)
            try:
                score = alphabeta(board, depth - 1, alpha, beta, False, end_time)
            finally:
                board.pop()
            print("Score;", move, score)

            best_score = max(best_score, score)
            alpha = max(alpha, best_score)

            if alpha >= beta:
                break

        return best_score

    else:
        best_score = POS_INF

        for move in ordered_moves(board):
            board.push(move)
            try:
                score = alphabeta(board, depth - 1, alpha, beta, True, end_time)
            finally:
                board.pop()

            best_score = min(best_score, score)
            beta = min(beta, best_score)

            if alpha >= beta:
                break
        
        return best_score

def find_best_move(board, time_limit=5.0):
    end_time = time.perf_counter() + time_limit

    legal_moves = list(board.legal_moves)
    best_move = legal_moves[0].uci()

    depth = 1

    try:
        while True:
            print("SEARCH DEPTH: ", depth)
            current_best_move = list(board.legal_moves)[0].uci()
            current_best_score = POS_INF

            for move in ordered_moves(board):
                board.push(move)
        
                try:
                    score = alphabeta(board=board, depth=depth, alpha=NEG_INF, beta=POS_INF, maximizing=True, end_time=end_time)
                finally:
                    board.pop()

                if score < current_best_score:
                    current_best_score = score
                    current_best_move = move.uci()


            best_move = current_best_move
            print("COMPLETED DEPTH: ", depth, current_best_move)
            depth += 1
    except SearchTimeout:
        print("TIMEOUT")
        print("LAST BEST = ", best_move)

    return best_move

@app.post("/ai-move")
def ai_move(req: MoveRequest):
    board = chess.Board(req.fen)


    if board.turn == chess.WHITE or board.is_game_over():
        print("returning because white or game is over")
        return {"move": None, "fen": board.fen()}

    best_move = find_best_move(board, time_limit=5.0)
    print("Best move: ", best_move)

    if best_move is None:
        return {"move": None, "fen": board.fen()}

    best_move = chess.Move.from_uci(best_move)
    if best_move not in board.legal_moves:
        return {"move": None, "fen": board.fen()}

    board.push(best_move)

    return {
        "move": best_move.uci(),
        "fen": board.fen(),
    }
