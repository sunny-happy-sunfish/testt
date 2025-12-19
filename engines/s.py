#!usr/bin/env python3

import chess
import sys
import time
import random
import math

def evaluate_board(board):
    score = 0
    for piece in board.piece_map().values():
        if piece.color == chess.WHITE:
            score += {"p": 10, "n": 30, "b": 30, "r": 50, "q": 90, "k": 900}[piece.symbol().lower()]
        else:
            score -= {"p": 10, "n": 30, "b": 30, "r": 50, "q": 90, "k": 900}[piece.symbol().lower()]
    return score


def minimax(board, depth, alpha, beta, maximizing_player, start_time, time_limit):
    if time_limit is not None and time.time() - start_time > time_limit:
        return evaluate_board(board), None

    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    best_move = None
    if maximizing_player:
        max_eval = -math.inf
        for move in board.legal_moves:
            board.push(move)
            eval, _ = minimax(board, depth - 1, alpha, beta, False, start_time, time_limit)
            board.pop()
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = math.inf
        for move in board.legal_moves:
            board.push(move)
            eval, _ = minimax(board, depth - 1, alpha, beta, True, start_time, time_limit)
            board.pop()
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

def uci_engine():
    board = chess.Board()
    while True:
        line = sys.stdin.readline().strip()
        if line == 'uci':
            print("id name StrawberryChess v1.0")
            print("id author MK")
            print("uciok")
        elif line == 'isready':
            print("readyok")
        elif line == 'ucinewgame':
            board.reset()
        elif line.startswith('position fen') or line.startswith('position startpos'):
            parts = line.split()
            if parts[1] == 'startpos':
                board.reset()
                moves_index = 3
            else:
                fen = " ".join(parts[2:8])
                board.set_fen(fen)
                moves_index = 8

            if len(parts) > moves_index and parts[moves_index] == 'moves':
                for move_uci in parts[moves_index+1:]:
                    move = chess.Move.from_uci(move_uci)
                    board.push(move)
        elif line.startswith('go'):
            parts = line.split()
            depth = 3
            time_limit = None
            if 'depth' in parts:
                depth = int(parts[parts.index('depth') + 1])
            if 'movetime' in parts:
                time_limit_ms = int(parts[parts.index('movetime') + 1])
                time_limit = time_limit_ms / 1000.0

            start_time = time.time()
            _, best_move = minimax(board.copy(), depth, -math.inf, math.inf, board.turn == chess.WHITE, start_time, time_limit)
            if best_move:
                print(f"bestmove {best_move.uci()}")
            else:
                legal_moves = list(board.legal_moves)
                if legal_moves:
                    random_move = random.choice(legal_moves)
                    print(f"bestmove {random_move.uci()}")
        elif line == 'quit':
            break

if __name__ == "__main__":
    uci_engine()
