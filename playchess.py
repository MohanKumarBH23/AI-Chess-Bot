"""
PyChess — Neo Kinpaku Grandmaster Edition
An autonomous Chess AI featuring Minimax search with Alpha-Beta pruning,
heuristic piece-square evaluation, and an Impeccable Neo Kinpaku design theme.

Author: Mohan
Design Framework: Impeccable Neo Kinpaku (pbakaus/impeccable)
"""

import pygame
import math
import copy
from board.chessboard import board
from board.move import move
from pieces.nullpiece import nullpiece
from pieces.queen import queen
from pieces.rook import rook
from pieces.knight import knight
from pieces.bishop import bishop
from player.AI import AI
from ui_theme import theme, KINPAKU_GOLD, VERDIGRIS, CHAMPAGNE, TEXT_MUTED

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def updateposition(x, y):
    """Converts (row, col) to 1D index (0..63)."""
    return x * 8 + y

def get_king_pos(gametiles, alliance):
    """Returns the (row, col) coordinate of the king of the given alliance."""
    target = 'k' if alliance == 'White' else 'K'
    for r in range(8):
        for c in range(8):
            if gametiles[r][c].pieceonTile.tostring() == target:
                return (r, c)
    return None

def find_check_sq(chess_board, move_engine):
    """Returns the square of the king currently under check, or None."""
    tiles = chess_board.gameTiles
    if move_engine.checkw(tiles)[0] == 'checked':
        return get_king_pos(tiles, 'White')
    if move_engine.checkb(tiles)[0] == 'checked':
        return get_king_pos(tiles, 'Black')
    return None


# =============================================================================
# MAIN MENU LOOP
# =============================================================================

def run_menu(display, clock):
    """
    Displays the Impeccable Neo Kinpaku title and mode selection screen.
    Returns 'ai', '2 player', or 'quit'.
    """
    card_ai_rect = pygame.Rect(95, 260, 285, 230)
    card_2p_rect = pygame.Rect(420, 260, 285, 230)

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if card_ai_rect.collidepoint(mouse_pos):
                    return 'ai'
                if card_2p_rect.collidepoint(mouse_pos):
                    return '2 player'

        theme.draw_menu(display, mouse_pos)
        pygame.display.update()
        clock.tick(60)


# =============================================================================
# MATCH GAME LOOP (AI & TWO-PLAYER)
# =============================================================================

def run_game(display, clock, game_mode):
    """
    Unified, robust match engine supporting both human vs human and human vs AI.
    Returns the game outcome: 'end1' (Black checkmates), 'end2' (White checkmates),
    'end3' (Stalemate), or 'quit'.
    """
    chess_board = board()
    chess_board.createboard()
    move_engine = move()
    ai_engine = AI()

    turn = 0
    moves = []
    enpassant = []
    promote = []
    promotion = False

    selected_sq = None
    last_move = None
    from_x, from_y = 0, 0

    while True:
        mouse_pos = pygame.mouse.get_pos()

        # ---------------------------------------------------------------------
        # 1. Checkmate & Stalemate Detection
        # ---------------------------------------------------------------------
        # White turn (turn % 2 == 0)
        if turn % 2 == 0 and len(moves) == 0 and not promotion:
            if move_engine.checkw(chess_board.gameTiles)[0] == 'checked':
                evasions = move_engine.movesifcheckedw(chess_board.gameTiles)
                if len(evasions) == 0:
                    return 'end1'  # Black won by checkmate
            else:
                # Test for stalemate
                has_legal = False
                for r in range(8):
                    for c in range(8):
                        piece = chess_board.gameTiles[r][c].pieceonTile
                        if piece.alliance == 'White':
                            pmoves = piece.legalmoveb(chess_board.gameTiles)
                            if pmoves and len(move_engine.pinnedw(chess_board.gameTiles, pmoves, r, c)) > 0:
                                has_legal = True
                                break
                    if has_legal:
                        break
                if not has_legal:
                    return 'end3'  # Stalemate

        # Black turn (turn % 2 == 1)
        if turn % 2 == 1 and len(moves) == 0 and not promotion:
            if move_engine.checkb(chess_board.gameTiles)[0] == 'checked':
                evasions = move_engine.movesifcheckedb(chess_board.gameTiles)
                if len(evasions) == 0:
                    return 'end2'  # White won by checkmate
            else:
                # Test for stalemate
                has_legal = False
                for r in range(8):
                    for c in range(8):
                        piece = chess_board.gameTiles[r][c].pieceonTile
                        if piece.alliance == 'Black':
                            pmoves = piece.legalmoveb(chess_board.gameTiles)
                            if pmoves and len(move_engine.pinnedb(chess_board.gameTiles, pmoves, r, c)) > 0:
                                has_legal = True
                                break
                    if has_legal:
                        break
                if not has_legal:
                    return 'end3'  # Stalemate

        # ---------------------------------------------------------------------
        # 2. Autonomous AI Turn
        # ---------------------------------------------------------------------
        if game_mode == 'ai' and turn % 2 == 1 and not promotion:
            # Render "Engine Thinking..." HUD badge and refresh screen
            check_sq = find_check_sq(chess_board, move_engine)
            theme.draw_board(display, chess_board.gameTiles, None, None, check_sq, last_move, is_thinking=True)
            pygame.display.update()

            # Execute minimax evaluation
            turn += 1
            board_clone = copy.deepcopy(chess_board.gameTiles)
            y, x, fx, fy = ai_engine.evaluate(board_clone)
            m, n = fy, fx  # dest_col, dest_row

            # Move logic for AI
            piece = chess_board.gameTiles[y][x].pieceonTile
            if piece.tostring() in ['K', 'R', 'k', 'r']:
                piece.moved = True

            # Castling by Black AI
            if piece.tostring() == 'K' and m == x + 2:
                chess_board.gameTiles[y][x + 1].pieceonTile = chess_board.gameTiles[y][x + 3].pieceonTile
                chess_board.gameTiles[y][x + 1].pieceonTile.position = updateposition(y, x + 1)
                chess_board.gameTiles[y][x + 3].pieceonTile = nullpiece()
            elif piece.tostring() == 'K' and m == x - 2:
                chess_board.gameTiles[y][x - 1].pieceonTile = chess_board.gameTiles[y][0].pieceonTile
                chess_board.gameTiles[y][x - 1].pieceonTile.position = updateposition(y, x - 1)
                chess_board.gameTiles[y][0].pieceonTile = nullpiece()

            # Clear old en passant
            if len(enpassant) != 0:
                chess_board.gameTiles[enpassant[0]][enpassant[1]].pieceonTile.enpassant = False
                enpassant = []

            # En passant capture by AI
            if piece.tostring() == 'P' and y + 1 == n and x + 1 == m and chess_board.gameTiles[n][m].pieceonTile.tostring() == '-':
                chess_board.gameTiles[y][x + 1].pieceonTile = nullpiece()
            if piece.tostring() == 'P' and y + 1 == n and x - 1 == m and chess_board.gameTiles[n][m].pieceonTile.tostring() == '-':
                chess_board.gameTiles[y][x - 1].pieceonTile = nullpiece()

            # En passant vulnerability creation
            if piece.tostring() == 'P' and n == y + 2:
                piece.enpassant = True
                enpassant = [n, m]

            # Promotion for AI
            if piece.tostring() == 'P' and y + 1 == n and y == 6:
                chess_board.gameTiles[y][x].pieceonTile = nullpiece()
                chess_board.gameTiles[n][m].pieceonTile = queen('Black', updateposition(n, m))
            else:
                chess_board.gameTiles[n][m].pieceonTile = chess_board.gameTiles[y][x].pieceonTile
                chess_board.gameTiles[y][x].pieceonTile = nullpiece()
                chess_board.gameTiles[n][m].pieceonTile.position = updateposition(n, m)

            last_move = ((y, x), (n, m))
            selected_sq = None
            moves = []
            continue

        # ---------------------------------------------------------------------
        # 3. User Input & Event Handling
        # ---------------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                coord = pygame.mouse.get_pos()
                click_col = math.floor(coord[0] / 100)
                click_row = math.floor(coord[1] / 100)

                # A) Handling Pawn Promotion Choice Selection
                if len(promote) != 0:
                    promo_alliance = chess_board.gameTiles[promote[5][0]][promote[5][1]].pieceonTile.alliance
                    for i in range(len(promote)):
                        if i == 4:
                            turn -= 1
                            break
                        if promote[i][0] == click_row and promote[i][1] == click_col:
                            target_r = promote[4][1]
                            target_c = promote[4][0]
                            pos = updateposition(target_r, target_c)
                            if i == 0:
                                new_piece = queen(promo_alliance, pos)
                            elif i == 1:
                                new_piece = rook(promo_alliance, pos)
                            elif i == 2:
                                new_piece = knight(promo_alliance, pos)
                            elif i == 3:
                                new_piece = bishop(promo_alliance, pos)

                            chess_board.gameTiles[target_r][target_c].pieceonTile = new_piece
                            chess_board.gameTiles[promote[5][0]][promote[5][1]].pieceonTile = nullpiece()
                            break

                    promote = []
                    promotion = False
                    moves = []
                    selected_sq = None
                    break

                # B) Handling White in Check Move Selection
                if move_engine.checkw(chess_board.gameTiles)[0] == 'checked' and len(moves) == 0 and turn % 2 == 0:
                    evasions = move_engine.movesifcheckedw(chess_board.gameTiles)
                    for move_cand in evasions:
                        if move_cand[1] == click_col and move_cand[0] == click_row:
                            moves.append([move_cand[2], move_cand[3]])
                            from_x = move_cand[1]
                            from_y = move_cand[0]
                            selected_sq = (from_y, from_x)
                    break

                # C) Handling Black in Check Move Selection (Two-Player Mode)
                if move_engine.checkb(chess_board.gameTiles)[0] == 'checked' and len(moves) == 0 and turn % 2 == 1:
                    evasions = move_engine.movesifcheckedb(chess_board.gameTiles)
                    for move_cand in evasions:
                        if move_cand[1] == click_col and move_cand[0] == click_row:
                            moves.append([move_cand[2], move_cand[3]])
                            from_x = move_cand[1]
                            from_y = move_cand[0]
                            selected_sq = (from_y, from_x)
                    break

                # D) Executing a Destination Move (Second Click)
                if len(moves) != 0:
                    move_executed = False
                    for dest in moves:
                        if dest[0] == click_row and dest[1] == click_col:
                            move_executed = True
                            turn += 1
                            dest_r, dest_c = click_row, click_col
                            moving_piece = chess_board.gameTiles[from_y][from_x].pieceonTile

                            # Track moved flag for castling
                            if moving_piece.tostring() in ['K', 'R', 'k', 'r']:
                                moving_piece.moved = True

                            # White Castling Execution
                            if moving_piece.tostring() == 'k' and dest_c == from_x + 2:
                                chess_board.gameTiles[from_y][from_x + 1].pieceonTile = chess_board.gameTiles[from_y][from_x + 3].pieceonTile
                                chess_board.gameTiles[from_y][from_x + 1].pieceonTile.position = updateposition(from_y, from_x + 1)
                                chess_board.gameTiles[from_y][from_x + 3].pieceonTile = nullpiece()
                            elif moving_piece.tostring() == 'k' and dest_c == from_x - 2:
                                chess_board.gameTiles[from_y][from_x - 1].pieceonTile = chess_board.gameTiles[from_y][0].pieceonTile
                                chess_board.gameTiles[from_y][from_x - 1].pieceonTile.position = updateposition(from_y, from_x - 1)
                                chess_board.gameTiles[from_y][0].pieceonTile = nullpiece()

                            # Black Castling Execution (Two-Player)
                            if moving_piece.tostring() == 'K' and dest_c == from_x + 2:
                                chess_board.gameTiles[from_y][from_x + 1].pieceonTile = chess_board.gameTiles[from_y][from_x + 3].pieceonTile
                                chess_board.gameTiles[from_y][from_x + 1].pieceonTile.position = updateposition(from_y, from_x + 1)
                                chess_board.gameTiles[from_y][from_x + 3].pieceonTile = nullpiece()
                            elif moving_piece.tostring() == 'K' and dest_c == from_x - 2:
                                chess_board.gameTiles[from_y][from_x - 1].pieceonTile = chess_board.gameTiles[from_y][0].pieceonTile
                                chess_board.gameTiles[from_y][from_x - 1].pieceonTile.position = updateposition(from_y, from_x - 1)
                                chess_board.gameTiles[from_y][0].pieceonTile = nullpiece()

                            # En Passant Cleanup
                            if len(enpassant) != 0:
                                chess_board.gameTiles[enpassant[0]][enpassant[1]].pieceonTile.enpassant = False
                                enpassant = []

                            # En Passant Captures
                            if moving_piece.tostring() == 'p' and from_y - 1 == dest_r and from_x + 1 == dest_c and chess_board.gameTiles[dest_r][dest_c].pieceonTile.tostring() == '-':
                                chess_board.gameTiles[from_y][from_x + 1].pieceonTile = nullpiece()
                            if moving_piece.tostring() == 'p' and from_y - 1 == dest_r and from_x - 1 == dest_c and chess_board.gameTiles[dest_r][dest_c].pieceonTile.tostring() == '-':
                                chess_board.gameTiles[from_y][from_x - 1].pieceonTile = nullpiece()
                            if moving_piece.tostring() == 'P' and from_y + 1 == dest_r and from_x + 1 == dest_c and chess_board.gameTiles[dest_r][dest_c].pieceonTile.tostring() == '-':
                                chess_board.gameTiles[from_y][from_x + 1].pieceonTile = nullpiece()
                            if moving_piece.tostring() == 'P' and from_y + 1 == dest_r and from_x - 1 == dest_c and chess_board.gameTiles[dest_r][dest_c].pieceonTile.tostring() == '-':
                                chess_board.gameTiles[from_y][from_x - 1].pieceonTile = nullpiece()

                            # Double Pawn Push En Passant Flag
                            if moving_piece.tostring() == 'p' and dest_r == from_y - 2:
                                moving_piece.enpassant = True
                                enpassant = [dest_r, dest_c]
                            if moving_piece.tostring() == 'P' and dest_r == from_y + 2:
                                moving_piece.enpassant = True
                                enpassant = [dest_r, dest_c]

                            # Promotion Triggers
                            if moving_piece.tostring() == 'p' and from_y - 1 == dest_r and from_y == 1:
                                promotion = True
                            if moving_piece.tostring() == 'P' and from_y + 1 == dest_r and from_y == 6:
                                promotion = True

                            # Normal move execution
                            if not promotion:
                                chess_board.gameTiles[dest_r][dest_c].pieceonTile = moving_piece
                                chess_board.gameTiles[from_y][from_x].pieceonTile = nullpiece()
                                chess_board.gameTiles[dest_r][dest_c].pieceonTile.position = updateposition(dest_r, dest_c)
                                last_move = ((from_y, from_x), (dest_r, dest_c))
                                moves = []
                                selected_sq = None
                            else:
                                # Setup promotion choices
                                if moving_piece.tostring() == 'P':
                                    anchor_c = max(0, min(6, from_x))
                                    promote = [[from_y + 1, anchor_c], [from_y + 1, anchor_c + 1],
                                               [from_y + 2, anchor_c], [from_y + 2, anchor_c + 1],
                                               [dest_c, dest_r], [from_y, from_x]]
                                else:
                                    anchor_c = max(0, min(6, from_x))
                                    promote = [[from_y - 1, anchor_c], [from_y - 1, anchor_c + 1],
                                               [from_y - 2, anchor_c], [from_y - 2, anchor_c + 1],
                                               [dest_c, dest_r], [from_y, from_x]]
                                last_move = ((from_y, from_x), (dest_r, dest_c))
                                moves = []
                            break

                    if move_executed:
                        break

                # E) Selecting a Piece (First Click)
                moves = []
                selected_sq = None
                clicked_tile = chess_board.gameTiles[click_row][click_col].pieceonTile
                active_alliance = 'White' if (turn % 2 == 0) else 'Black'

                if clicked_tile.alliance == active_alliance:
                    raw_moves = clicked_tile.legalmoveb(chess_board.gameTiles)
                    if raw_moves is not None:
                        # King castling options
                        if clicked_tile.tostring() == 'k':
                            castles = move_engine.castlingw(chess_board.gameTiles)
                            if castles:
                                for side in castles:
                                    if side == 'ks':
                                        raw_moves.append([7, 6])
                                    elif side == 'qs':
                                        raw_moves.append([7, 2])
                        elif clicked_tile.tostring() == 'K':
                            castles = move_engine.castlingb(chess_board.gameTiles)
                            if castles:
                                for side in castles:
                                    if side == 'ks':
                                        raw_moves.append([0, 6])
                                    elif side == 'qs':
                                        raw_moves.append([0, 2])

                        # Pawn en passant options
                        ep_check = move_engine.enpassantb(chess_board.gameTiles, click_row, click_col)
                        if ep_check:
                            if ep_check[1] == 'r':
                                dy = -1 if active_alliance == 'White' else 1
                                raw_moves.append([click_row + dy, click_col + 1])
                            elif ep_check[1] == 'l':
                                dy = -1 if active_alliance == 'White' else 1
                                raw_moves.append([click_row + dy, click_col - 1])

                        # Filter for pins / king checks
                        if active_alliance == 'White':
                            pinned_moves = move_engine.pinnedw(chess_board.gameTiles, raw_moves, click_row, click_col)
                        else:
                            pinned_moves = move_engine.pinnedb(chess_board.gameTiles, raw_moves, click_row, click_col)

                        if len(pinned_moves) > 0:
                            moves = pinned_moves
                            from_x = click_col
                            from_y = click_row
                            selected_sq = (from_y, from_x)

        # ---------------------------------------------------------------------
        # 4. Board & UI Presentation
        # ---------------------------------------------------------------------
        check_sq = find_check_sq(chess_board, move_engine)
        theme.draw_board(display, chess_board.gameTiles, selected_sq, moves, check_sq, last_move)

        # Draw promotion modal overlay if active
        if promotion and len(promote) != 0:
            promo_alliance = chess_board.gameTiles[promote[5][0]][promote[5][1]].pieceonTile.alliance
            px = promote[0][1] * 100
            py = min(promote[0][0], promote[2][0]) * 100
            theme.draw_promotion_modal(display, promo_alliance, px, py, mouse_pos)

        pygame.display.update()
        clock.tick(60)


# =============================================================================
# GAME OVER MODAL LOOP
# =============================================================================

def run_game_over(display, clock, result):
    """
    Renders an elegant modal over the final board state.
    Returns 'rematch', 'menu', or 'quit'.
    """
    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Button hit checks
                btn_rematch = pygame.Rect(230, 440, 160, 46)
                btn_menu = pygame.Rect(410, 440, 160, 46)
                if btn_rematch.collidepoint(mouse_pos):
                    return 'rematch'
                if btn_menu.collidepoint(mouse_pos):
                    return 'menu'

        theme.draw_game_over(display, result, mouse_pos)
        pygame.display.update()
        clock.tick(60)


# =============================================================================
# APPLICATION ENTRYPOINT
# =============================================================================

def main():
    pygame.init()
    gamedisplay = pygame.display.set_mode((800, 800))
    pygame.display.set_caption("PyChess — Neo Kinpaku Engine Edition")
    clock = pygame.time.Clock()

    while True:
        # 1. Main Menu
        selected_mode = run_menu(gamedisplay, clock)
        if selected_mode == 'quit':
            break

        # 2. Match loop with rematch support
        current_mode = selected_mode
        while True:
            outcome = run_game(gamedisplay, clock, current_mode)
            if outcome == 'quit':
                pygame.quit()
                return

            action = run_game_over(gamedisplay, clock, outcome)
            if action == 'rematch':
                continue
            elif action == 'menu':
                break
            elif action == 'quit':
                pygame.quit()
                return

    pygame.quit()


if __name__ == "__main__":
    main()
