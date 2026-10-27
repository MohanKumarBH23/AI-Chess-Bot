"""
Impeccable Neo Kinpaku Theme for PyChess
Inspired by Paul Bakaus's Impeccable Design System (pbakaus/impeccable).
Replaces generic/vibecoded visuals with a refined, museum-grade Japanese
Kinpaku lacquerware & grandmaster tournament aesthetic.
"""

import pygame
import math

# =============================================================================
# COLOR TOKENS (Derived from Impeccable DESIGN.md Neo Kinpaku Specification)
# =============================================================================

# Lacquer Surfaces
LACQUER_BLACK   = (16, 17, 19)      # #101113 - deepest page/board ground
LACQUER_DEEP    = (10, 10, 12)      # #0A0A0C - recessed inset
RAISED_LACQUER  = (26, 28, 33)      # #1A1C21 - elevated panels & cards
RAISED_HOVER    = (36, 39, 47)      # #24272F - card interactive hover
GRAPHITE        = (44, 48, 56)      # #2C3038 - subtle borders
GRAPHITE_LIGHT  = (65, 70, 82)      # #414652 - active borders

# Brand Anchors & Metallics
KINPAKU_GOLD    = (226, 192, 102)   # #E2C066 - primary champagne gold leaf
KINPAKU_RICH    = (212, 175, 55)    # #D4AF37 - burnished rich gold accent
KINPAKU_GLINT   = (248, 236, 196)   # #F8ECC4 - highlight glint
KINPAKU_MUTED   = (168, 142, 75)    # #A88E4B - subdued antique gold
VERDIGRIS       = (74, 153, 158)    # #4A999E - oxidized patina teal accent
VERDIGRIS_PALE  = (112, 182, 186)   # #70B6BA - hover patina

# Typography & Text
CHAMPAGNE       = (242, 238, 228)   # #F2EEE4 - primary heading white
TEXT_WARM       = (224, 220, 212)   # #E0DCD4 - body text
TEXT_MUTED      = (154, 152, 144)   # #9A9890 - captions and rank/file notation
TEXT_FAINT      = (108, 106, 100)   # #6C6A64 - subdued labels / tick marks

# Semantic / State
VERMILION       = (214, 82, 70)     # #D65246 - check / warning / captures
VERMILION_BG    = (214, 82, 70, 75) # check square soft glow

# Chessboard Tiles (Grandmaster Lacquer & Warm Bone Edition)
BOARD_LIGHT     = (236, 231, 220)   # #ECE7DC - warm bone / ivory lacquer
BOARD_DARK      = (48, 52, 60)      # #30343C - smoky charcoal obsidian lacquer

# Notation Labels
NOTATION_LIGHT  = (130, 126, 118)   # file/rank text on light squares
NOTATION_DARK   = (160, 158, 150)   # file/rank text on dark squares


# =============================================================================
# THEME MANAGER & ASSET CACHE
# =============================================================================

class ThemeManager:
    """Manages pre-rendered fonts, smooth-scaled sprites, and UI rendering."""

    def __init__(self):
        self.initialized = False
        self.piece_cache = {}
        self.fonts = {}
        self.highlight_cache = {}

    def init(self):
        """Initialize fonts and pre-render piece textures after pygame.display is set."""
        if self.initialized:
            return

        # Typography hierarchy (Georgia serif for brand; Segoe UI for interface)
        try:
            self.fonts['title'] = pygame.font.SysFont('georgia', 44, bold=True)
            self.fonts['heading'] = pygame.font.SysFont('georgia', 24, bold=True)
            self.fonts['card_title'] = pygame.font.SysFont('georgia', 18, bold=True)
        except Exception:
            self.fonts['title'] = pygame.font.Font('freesansbold.ttf', 44)
            self.fonts['heading'] = pygame.font.Font('freesansbold.ttf', 24)
            self.fonts['card_title'] = pygame.font.Font('freesansbold.ttf', 18)

        try:
            self.fonts['eyebrow'] = pygame.font.SysFont('segoeui', 11, bold=True)
            self.fonts['body'] = pygame.font.SysFont('segoeui', 13)
            self.fonts['caption'] = pygame.font.SysFont('segoeui', 11)
            self.fonts['button'] = pygame.font.SysFont('segoeui', 14, bold=True)
            self.fonts['notation'] = pygame.font.SysFont('segoeui', 11, bold=True)
            self.fonts['badge'] = pygame.font.SysFont('segoeui', 10, bold=True)
        except Exception:
            self.fonts['eyebrow'] = pygame.font.Font('freesansbold.ttf', 11)
            self.fonts['body'] = pygame.font.Font('freesansbold.ttf', 13)
            self.fonts['caption'] = pygame.font.Font('freesansbold.ttf', 11)
            self.fonts['button'] = pygame.font.Font('freesansbold.ttf', 14)
            self.fonts['notation'] = pygame.font.Font('freesansbold.ttf', 11)
            self.fonts['badge'] = pygame.font.Font('freesansbold.ttf', 10)

        # Cache piece images using bilinear anti-aliasing (smoothscale)
        pieces = ['BK', 'BQ', 'BR', 'BB', 'BN', 'BP',
                  'WK', 'WQ', 'WR', 'WB', 'WN', 'WP']
        for name in pieces:
            try:
                raw = pygame.image.load(f'./chessart/{name}.png').convert_alpha()
                # 90x90 fits comfortably centered in a 100x100 tile with 5px breathing margin
                self.piece_cache[name] = pygame.transform.smoothscale(raw, (90, 90))
                # 70x70 for promotion picker
                self.piece_cache[f'{name}_promo'] = pygame.transform.smoothscale(raw, (70, 70))
            except Exception as e:
                print(f"Warning: could not load piece {name}: {e}")

        # Pre-render selection highlight surface (translucent gold with 2px gold border)
        sel_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        sel_surf.fill((KINPAKU_GOLD[0], KINPAKU_GOLD[1], KINPAKU_GOLD[2], 65))
        pygame.draw.rect(sel_surf, KINPAKU_GOLD, [0, 0, 100, 100], width=2)
        self.highlight_cache['selected'] = sel_surf

        # Pre-render checked king highlight (soft vermilion wash + border)
        check_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        check_surf.fill((VERMILION[0], VERMILION[1], VERMILION[2], 85))
        pygame.draw.rect(check_surf, VERMILION, [0, 0, 100, 100], width=2)
        self.highlight_cache['check'] = check_surf

        # Pre-render valid move indicator (empty square: small gold disc)
        move_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.circle(move_surf, (KINPAKU_GOLD[0], KINPAKU_GOLD[1], KINPAKU_GOLD[2], 140), (50, 50), 13)
        self.highlight_cache['valid_move'] = move_surf

        # Pre-render capture indicator (enemy piece: subtle circular targeting ring)
        capture_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.circle(capture_surf, (KINPAKU_GOLD[0], KINPAKU_GOLD[1], KINPAKU_GOLD[2], 210), (50, 50), 44, width=3)
        self.highlight_cache['capture_target'] = capture_surf

        self.initialized = True

    # -------------------------------------------------------------------------
    # MENU SCREEN RENDERING
    # -------------------------------------------------------------------------

    def draw_menu(self, display, mouse_pos):
        """Renders the Impeccable Neo Kinpaku title and game mode selection screen."""
        self.init()
        display.fill(LACQUER_BLACK)

        # 1. Subtle gold hairline perimeter frame with Japanese corner ticks
        frame_rect = pygame.Rect(20, 20, 760, 760)
        pygame.draw.rect(display, GRAPHITE, frame_rect, width=1)

        # Corner tick accents (Kinpaku Gold)
        tick_len = 12
        corners = [(20, 20), (780, 20), (20, 780), (780, 780)]
        for cx, cy in corners:
            dx = 1 if cx == 20 else -1
            dy = 1 if cy == 20 else -1
            pygame.draw.line(display, KINPAKU_GOLD, (cx, cy), (cx + dx * tick_len, cy), 2)
            pygame.draw.line(display, KINPAKU_GOLD, (cx, cy), (cx, cy + dy * tick_len), 2)

        # 2. Header & Brand Lockup
        # Eyebrow tag
        eyebrow_text = "CHESS ENGINE  •  ALPHA-BETA SEARCH  •  DEPTH 3"
        eyebrow_surf = self.fonts['eyebrow'].render(eyebrow_text, True, KINPAKU_GOLD)
        display.blit(eyebrow_surf, (400 - eyebrow_surf.get_width() // 2, 70))

        # Main Wordmark
        title_surf = self.fonts['title'].render("P Y C H E S S", True, CHAMPAGNE)
        display.blit(title_surf, (400 - title_surf.get_width() // 2, 95))

        # Gold decorative divider
        pygame.draw.line(display, KINPAKU_MUTED, (320, 160), (480, 160), 1)
        pygame.draw.circle(display, KINPAKU_GOLD, (400, 160), 2)

        # Subtitle
        sub_text = "Autonomous Adversarial Minimax with Material & Mobility Evaluation"
        sub_surf = self.fonts['body'].render(sub_text, True, TEXT_MUTED)
        display.blit(sub_surf, (400 - sub_surf.get_width() // 2, 175))

        # 3. Game Mode Cards
        # Card 1: Player vs AI
        card_ai_rect = pygame.Rect(95, 260, 285, 230)
        is_ai_hover = card_ai_rect.collidepoint(mouse_pos)
        self._draw_mode_card(
            display,
            rect=card_ai_rect,
            is_hover=is_ai_hover,
            badge="SINGLE PLAYER",
            title="Player vs AI",
            desc="Test your tactical mastery against the autonomous Minimax engine with Alpha-Beta pruning.",
            accent_color=KINPAKU_GOLD,
            action_text="Launch Match →"
        )

        # Card 2: Two Player
        card_2p_rect = pygame.Rect(420, 260, 285, 230)
        is_2p_hover = card_2p_rect.collidepoint(mouse_pos)
        self._draw_mode_card(
            display,
            rect=card_2p_rect,
            is_hover=is_2p_hover,
            badge="TWO PLAYER",
            title="Pass & Play",
            desc="Over-the-board local match for two human contenders with full standard check/mate rules.",
            accent_color=VERDIGRIS,
            action_text="Launch Match →"
        )

        # 4. Engine Architecture Info Bar
        info_rect = pygame.Rect(95, 530, 610, 100)
        pygame.draw.rect(display, RAISED_LACQUER, info_rect, border_radius=6)
        pygame.draw.rect(display, GRAPHITE, info_rect, width=1, border_radius=6)

        spec_head = self.fonts['card_title'].render("Engine Specifications", True, CHAMPAGNE)
        display.blit(spec_head, (115, 545))

        specs = [
            "• Search: Recursive Minimax with Alpha-Beta Pruning",
            "• Evaluation: Piece Values + Mobility + Center Control",
            "• Rules: En Passant, Castling, Pawn Promotion, Pins, Check/Stalemate"
        ]
        for idx, spec in enumerate(specs):
            spec_surf = self.fonts['caption'].render(spec, True, TEXT_MUTED)
            display.blit(spec_surf, (115, 575 + idx * 17))

        # 5. Footer & Attribution
        author_surf = self.fonts['body'].render("Developed by Mohan", True, TEXT_WARM)
        display.blit(author_surf, (400 - author_surf.get_width() // 2, 690))

        credit_surf = self.fonts['caption'].render("Styled with the Impeccable Neo Kinpaku Design System", True, TEXT_FAINT)
        display.blit(credit_surf, (400 - credit_surf.get_width() // 2, 715))

    def _draw_mode_card(self, display, rect, is_hover, badge, title, desc, accent_color, action_text):
        """Renders an interactive mode selection card with micro-interaction hover."""
        bg_color = RAISED_HOVER if is_hover else RAISED_LACQUER
        border_color = accent_color if is_hover else GRAPHITE
        border_width = 2 if is_hover else 1

        pygame.draw.rect(display, bg_color, rect, border_radius=8)
        pygame.draw.rect(display, border_color, rect, width=border_width, border_radius=8)

        # Badge pill
        if is_hover:
            badge_bg = accent_color
            badge_text_color = LACQUER_BLACK
        else:
            badge_bg = (38, 42, 50)
            badge_text_color = accent_color

        badge_rect = pygame.Rect(rect.x + 18, rect.y + 18, 98, 22)
        pygame.draw.rect(display, badge_bg, badge_rect, border_radius=4)
        badge_surf = self.fonts['badge'].render(badge, True, badge_text_color)
        display.blit(badge_surf, (badge_rect.x + (badge_rect.width - badge_surf.get_width()) // 2,
                                  badge_rect.y + (badge_rect.height - badge_surf.get_height()) // 2))

        # Card Title
        title_surf = self.fonts['heading'].render(title, True, CHAMPAGNE if not is_hover else KINPAKU_GLINT)
        display.blit(title_surf, (rect.x + 18, rect.y + 48))

        # Card Description (wrapped)
        desc_lines = self._wrap_text(desc, self.fonts['body'], rect.width - 36)
        for i, line in enumerate(desc_lines):
            line_surf = self.fonts['body'].render(line, True, TEXT_MUTED)
            display.blit(line_surf, (rect.x + 18, rect.y + 88 + i * 20))

        # Bottom action link
        action_surf = self.fonts['button'].render(action_text, True, accent_color if is_hover else TEXT_WARM)
        display.blit(action_surf, (rect.x + 18, rect.bottom - 34))

    # -------------------------------------------------------------------------
    # CHESSBOARD & IN-GAME PIECE RENDERING
    # -------------------------------------------------------------------------

    def draw_board(self, display, game_tiles, selected_sq=None, valid_moves=None, check_sq=None, last_move=None, is_thinking=False):
        """
        Renders the full 800x800 chessboard with grandmaster rank/file notation,
        warm lacquer tiles, piece sprites, and smooth highlights.
        """
        self.init()

        # 1. Draw tiles and edge notation
        for row in range(8):
            for col in range(8):
                x = col * 100
                y = row * 100
                is_light = ((row + col) % 2 == 0)
                tile_color = BOARD_LIGHT if is_light else BOARD_DARK
                pygame.draw.rect(display, tile_color, [x, y, 100, 100])

                # Grandmaster notation:
                # Rank numbers (1-8) along column 0 (left edge)
                if col == 0:
                    rank_num = str(8 - row)
                    color = NOTATION_LIGHT if is_light else NOTATION_DARK
                    num_surf = self.fonts['notation'].render(rank_num, True, color)
                    display.blit(num_surf, (x + 5, y + 4))

                # File letters (a-h) along row 7 (bottom edge)
                if row == 7:
                    file_letter = chr(ord('a') + col)
                    color = NOTATION_LIGHT if is_light else NOTATION_DARK
                    letter_surf = self.fonts['notation'].render(file_letter, True, color)
                    display.blit(letter_surf, (x + 85, y + 80))

        # 2. Last move highlight (subtle patina wash on from and to squares)
        if last_move:
            for sq in last_move:
                lx = sq[1] * 100
                ly = sq[0] * 100
                last_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
                last_surf.fill((VERDIGRIS[0], VERDIGRIS[1], VERDIGRIS[2], 50))
                display.blit(last_surf, (lx, ly))

        # 3. Selected Square Highlight
        if selected_sq is not None:
            sx = selected_sq[1] * 100
            sy = selected_sq[0] * 100
            display.blit(self.highlight_cache['selected'], (sx, sy))

        # 4. King In Check Highlight
        if check_sq is not None:
            cx = check_sq[1] * 100
            cy = check_sq[0] * 100
            display.blit(self.highlight_cache['check'], (cx, cy))

        # 5. Valid Move Destination Highlights
        if valid_moves:
            for move in valid_moves:
                # move format is [dest_row, dest_col]
                mr, mc = move[0], move[1]
                mx = mc * 100
                my = mr * 100

                target_piece = game_tiles[mr][mc].pieceonTile
                if target_piece.tostring() != '-':
                    # Capture square: draw targeting outer ring
                    display.blit(self.highlight_cache['capture_target'], (mx, my))
                else:
                    # Empty square: draw subtle center disc
                    display.blit(self.highlight_cache['valid_move'], (mx, my))

        # 6. Render Pieces
        for row in range(8):
            for col in range(8):
                piece = game_tiles[row][col].pieceonTile
                piece_code = piece.tostring()
                if piece_code != '-':
                    key = piece.alliance[0].upper() + piece_code.upper()
                    img = self.piece_cache.get(key)
                    if img:
                        # Center 90x90 piece in 100x100 tile at offset (5, 5)
                        display.blit(img, (col * 100 + 5, row * 100 + 5))

        # 7. Engine Thinking Pill HUD
        if is_thinking:
            pill_rect = pygame.Rect(280, 14, 240, 32)
            pill_surf = pygame.Surface((240, 32), pygame.SRCALPHA)
            pill_surf.fill((LACQUER_BLACK[0], LACQUER_BLACK[1], LACQUER_BLACK[2], 230))
            display.blit(pill_surf, (280, 14))
            pygame.draw.rect(display, KINPAKU_GOLD, pill_rect, width=1, border_radius=16)
            pygame.draw.circle(display, KINPAKU_GOLD, (304, 30), 4)
            thinking_txt = self.fonts['eyebrow'].render("ENGINE EVALUATING...", True, KINPAKU_GOLD)
            display.blit(thinking_txt, (318, 22))

    # -------------------------------------------------------------------------
    # PROMOTION MODAL RENDERING
    # -------------------------------------------------------------------------

    def draw_promotion_modal(self, display, alliance, anchor_x, anchor_y, mouse_pos):
        """Renders an elegant themed promotion choice box over the board."""
        self.init()

        # Modal box 200x200
        box_x = max(0, min(600, anchor_x))
        box_y = max(0, min(600, anchor_y))
        box_rect = pygame.Rect(box_x, box_y, 200, 200)

        # Translucent backdrop card
        overlay = pygame.Surface((200, 200), pygame.SRCALPHA)
        overlay.fill((RAISED_LACQUER[0], RAISED_LACQUER[1], RAISED_LACQUER[2], 245))
        display.blit(overlay, (box_x, box_y))
        pygame.draw.rect(display, KINPAKU_GOLD, box_rect, width=2, border_radius=4)

        # Pieces to offer
        prefix = 'W' if alliance == 'White' else 'B'
        pieces = ['Q', 'R', 'N', 'B']
        positions = [
            (box_x, box_y),
            (box_x + 100, box_y),
            (box_x, box_y + 100),
            (box_x + 100, box_y + 100)
        ]

        for idx, (p_code, (px, py)) in enumerate(zip(pieces, positions)):
            tile_rect = pygame.Rect(px, py, 100, 100)
            if tile_rect.collidepoint(mouse_pos):
                hover_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
                hover_surf.fill((KINPAKU_GOLD[0], KINPAKU_GOLD[1], KINPAKU_GOLD[2], 40))
                display.blit(hover_surf, (px, py))

            key = f"{prefix}{p_code}_promo"
            img = self.piece_cache.get(key)
            if img:
                display.blit(img, (px + 15, py + 15))

    # -------------------------------------------------------------------------
    # GAME OVER MODAL RENDERING
    # -------------------------------------------------------------------------

    def draw_game_over(self, display, result_type, mouse_pos):
        """
        Renders an elegant, non-intrusive Game Over modal directly over the final board state.
        result_type: 'end1' (Black won by checkmate), 'end2' (White won by checkmate), 'end3' (Stalemate)
        """
        self.init()

        # Darkened translucent backdrop
        dark_overlay = pygame.Surface((800, 800), pygame.SRCALPHA)
        dark_overlay.fill((LACQUER_BLACK[0], LACQUER_BLACK[1], LACQUER_BLACK[2], 215))
        display.blit(dark_overlay, (0, 0))

        # Dialog Box
        dialog = pygame.Rect(190, 230, 420, 310)
        pygame.draw.rect(display, RAISED_LACQUER, dialog, border_radius=10)
        pygame.draw.rect(display, KINPAKU_GOLD, dialog, width=2, border_radius=10)

        # Title and message based on result
        if result_type == 'end1':
            badge_text = "CHECKMATE"
            headline = "Black Victorious"
            desc = "The Black pieces have delivered definitive checkmate."
            accent = VERMILION
        elif result_type == 'end2':
            badge_text = "CHECKMATE"
            headline = "White Victorious"
            desc = "The White pieces have delivered definitive checkmate."
            accent = KINPAKU_GOLD
        else:
            badge_text = "STALEMATE"
            headline = "Peaceful Settlement"
            desc = "No legal moves remain and king is not in check. Draw."
            accent = VERDIGRIS

        # Result badge
        badge_surf = self.fonts['eyebrow'].render(badge_text, True, accent)
        display.blit(badge_surf, (400 - badge_surf.get_width() // 2, 265))

        # Main headline
        head_surf = self.fonts['title'].render(headline, True, CHAMPAGNE)
        display.blit(head_surf, (400 - head_surf.get_width() // 2, 290))

        # Divider
        pygame.draw.line(display, GRAPHITE, (240, 355), (560, 355), 1)

        # Description
        desc_surf = self.fonts['body'].render(desc, True, TEXT_MUTED)
        display.blit(desc_surf, (400 - desc_surf.get_width() // 2, 375))

        # Action Buttons
        # Button 1: Rematch / Play Again
        btn_rematch = pygame.Rect(230, 440, 160, 46)
        is_rematch_hover = btn_rematch.collidepoint(mouse_pos)
        rematch_bg = KINPAKU_RICH if is_rematch_hover else KINPAKU_GOLD
        pygame.draw.rect(display, rematch_bg, btn_rematch, border_radius=6)
        btn1_txt = self.fonts['button'].render("Play Again", True, LACQUER_BLACK)
        display.blit(btn1_txt, (btn_rematch.centerx - btn1_txt.get_width() // 2,
                                btn_rematch.centery - btn1_txt.get_height() // 2))

        # Button 2: Main Menu
        btn_menu = pygame.Rect(410, 440, 160, 46)
        is_menu_hover = btn_menu.collidepoint(mouse_pos)
        menu_bg = RAISED_HOVER if is_menu_hover else GRAPHITE
        pygame.draw.rect(display, menu_bg, btn_menu, border_radius=6)
        pygame.draw.rect(display, GRAPHITE_LIGHT, btn_menu, width=1, border_radius=6)
        btn2_txt = self.fonts['button'].render("Main Menu", True, CHAMPAGNE)
        display.blit(btn2_txt, (btn_menu.centerx - btn2_txt.get_width() // 2,
                                btn_menu.centery - btn2_txt.get_height() // 2))

        return btn_rematch, btn_menu

    # -------------------------------------------------------------------------
    # UTILITIES
    # -------------------------------------------------------------------------

    @staticmethod
    def _wrap_text(text, font, max_width):
        """Wraps words to fit inside max_width."""
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines


# Global Singleton
theme = ThemeManager()
