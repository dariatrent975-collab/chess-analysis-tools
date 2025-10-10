import chess
import chess.pgn
import chess.engine

ENGINE_PATH = r"" #указать путь к движку
INPUT_PGN = r"" #указать путь к анализируемому файлу
OUTPUT_PGN = "mates_found.pgn"

MATE_IN = 2
DEPTH = 12


def cut_on_forced_mate(game, engine, mate_in=2, depth=10):
    results = []
    board = game.board()
    move_stack = []

    for move in game.mainline_moves():
        board.push(move)
        move_stack.append(move)

        print(f"Анализируем позицию после хода: {move.uci()}")

        for candidate in board.legal_moves:
            board.push(candidate)
            info = engine.analyse(board, chess.engine.Limit(depth=depth))
            score = info["score"].pov(board.turn)
            board.pop()

            if score.is_mate() and score.mate() == mate_in:
                print(f"Найден форсированный мат после хода {candidate.uci()}")

                short_game = chess.pgn.Game()
                node = short_game
                temp_board = chess.Board()

                for m in move_stack:
                    node = node.add_main_variation(m)
                    temp_board.push(m)

                results.append(short_game)
                break

    if not results:
        print("Форсированных матов в партии не найдено.")
    return results


def filter_pgn_mates(input_pgn, output_pgn, mate_in=2, depth=12):
    try:
        infile = open(input_pgn, encoding="utf-8")
    except FileNotFoundError:
        print(f"Файл не найден: {input_pgn}")
        return

    engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)

    with infile, open(output_pgn, "w", encoding="utf-8") as outfile:
        game_count = 0
        found_count = 0

        while True:
            game = chess.pgn.read_game(infile)
            if game is None:
                break

            game_count += 1
            print(f"\nОбрабатывается партия №{game_count}...")

            cuts = cut_on_forced_mate(game, engine, mate_in, depth)

            for cut in cuts:
                found_count += 1
                print("Сохраняем найденную позицию в файл")
                print(cut, file=outfile)

    engine.quit()
    print(f"\nНайдено {found_count} позиций с форсированным матом.")
    print(f"Результат сохранён в файл: {output_pgn}")


filter_pgn_mates(INPUT_PGN, OUTPUT_PGN, mate_in=MATE_IN, depth=DEPTH)
