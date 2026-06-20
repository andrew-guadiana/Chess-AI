# Chess AI

A chess engine built in Python using **Minimax** and **Alpha-Beta Pruning**, exposed through a FastAPI backend and playable through a React frontend.

The engine evaluates positions using material balance and piece-square tables, then searches for the strongest move within a configurable time limit using iterative deepening.

## Features

### Search

* Minimax search
* Alpha-Beta pruning
* Iterative deepening
* Time-limited search
* Quiescence search
* Move ordering
* Transposition table caching
* Transposition-table move ordering

### Evaluation

* Material evaluation
* Piece-square tables

  * Pawns
  * Knights
  * Bishops
  * Rooks
  * Kings

### Frontend

* Interactive chessboard
* Play as White against the engine
* Real-time communication with FastAPI backend
* Game reset functionality

## Search Techniques

### Minimax

The engine searches future positions by assuming both players play optimally.

### Alpha-Beta Pruning

Branches that cannot improve the final evaluation are skipped, significantly reducing the number of positions searched.

### Move Ordering

Moves are sorted so that strong candidate moves are searched first:

* Transposition table best move
* Captures
* Promotions

Better move ordering increases alpha-beta pruning effectiveness.

### Quiescence Search

When the normal search reaches depth 0, the engine continues exploring tactical moves such as captures and promotions to reduce the horizon effect.

### Iterative Deepening

The engine repeatedly searches deeper depths until the allotted time expires.

### Transposition Tables

Previously evaluated positions are cached using the board's transposition key, avoiding redundant calculations.

## Evaluation Function

Positions are scored using:

```text
Position Score =
Material
+ Piece-Square Bonuses
```

Piece values:

| Piece  | Value |
| ------ | ----- |
| Pawn   | 100   |
| Knight | 300   |
| Bishop | 330   |
| Rook   | 500   |
| Queen  | 900   |

The engine also applies piece-square table bonuses to reward strong piece placement.

## Potential Improvements

* [ ] Opening book
* [ ] King safety evaluation
* [ ] Endgame-specific evaluation
* [ ] Zobrist hashing implementation
* [ ] Better move ordering heuristics (killer moves/history heuristic)

## Tech Stack

### Backend

* Python
* FastAPI
* python-chess

### Frontend

* React
* TypeScript
* chess.js

## Running Locally

### Backend

```bash
pip install fastapi uvicorn python-chess

uvicorn main:app --reload
```

Server runs on:

```text
http://localhost:8000
```

### Frontend

```bash
npm install
npm run dev
```

Frontend runs on:

```text
http://localhost:5173
```

## API

### POST /ai-move

Request:

```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
}
```

Response:

```json
{
  "move": "e7e5",
  "fen": "rnbqkbnr/pppp1ppp/8/4p3/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 2"
}
```

## Example

Play against the engine in your browser:

1. Start the FastAPI backend.
2. Start the React frontend.
3. Open the application.
4. Play as White.
5. The engine responds as Black.

