import os
import chess
import chess.pgn
import chess.engine

BASE_DIR = os.path.dirname(__file__)
ENGINE_PATH = os.path.join(BASE_DIR, "stockfish", "stockfish-windows-x86-64-avx2.exe")
OUTPUT_PGN = os.path.join(BASE_DIR, "output_mates.pgn")

def cut_on_forced_mate(game, engine, mate_in=3, depth=20):
    results = []
    board = game.board()
    new_game = chess.pgn.Game()
    node = new_game

    for move in game.mainline_moves():
        board.push(move)
        node = node.add_main_variation(move)

        for candidate in board.legal_moves:
            board.push(candidate)
            info = engine.analyse(board, chess.engine.Limit(depth=depth))
            score = info["score"].pov(chess.WHITE)
            board.pop()

            if score.is_mate() and abs(score.mate()) == mate_in:
                results.append(new_game.copy())

    return results

def filter_pgn_mates(input_pgn, output_pgn_mate, mate_in=3, depth=20):
    engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)

    with open(input_pgn, encoding="utf-8") as infile, \
         open(output_pgn_mate, "w", encoding="utf-8") as outfile:

        while True:
            game = chess.pgn.read_game(infile)
            if game is None:
                break

            cuts = cut_on_forced_mate(game, engine, mate_in, depth)
            for cut in cuts:
                print(cut, file=outfile)

    engine.quit()

# --- Ввод от пользователя ---
input_file = input("Введите имя или путь к PGN-файлу: ").strip()
if not os.path.isabs(input_file):
    input_file = os.path.join(BASE_DIR, input_file)  # относительный путь из папки скрипта

filter_pgn_mates(input_file, OUTPUT_PGN, mate_in=3)
print(f"Результат сохранён в {OUTPUT_PGN}")
