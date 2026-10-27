# PyChess — Minimax Autonomous AI & Neo Kinpaku Edition

**Author**: Mohan  
**Design Framework**: Impeccable Neo Kinpaku (inspired by [pbakaus/impeccable](https://github.com/pbakaus/impeccable))

---

## Technologies Used
- **Language**: Python 3.10+ (tested on Python 3.13)
- **GUI Engine**: Pygame (`pygame>=2.6.0`)
- **AI Algorithm**: Recursive Minimax with Alpha-Beta Pruning (Depth 3)
- **Design System**: Impeccable Neo Kinpaku

---

## Project Overview
PyChess is a high-performance desktop chess application engineered with strict separation between board state representation, FIDE-standard move validation, autonomous heuristic search, and an artisanal visual interface.

It features two game modes:
1. **Player vs AI**: An adversarial match against an autonomous Minimax AI evaluating material balance, piece mobility, and positional square control up to depth 3 with alpha-beta branch pruning.
2. **Pass & Play (2 Player)**: An over-the-board local match for two human contenders.

---

## Visual Design & Architecture (Impeccable Neo Kinpaku)
The interface adheres to the **Impeccable Neo Kinpaku** design language, eliminating generic AI design patterns to deliver a polished, resume-ready visual identity:
- **Palette**: Dark warm obsidian lacquer surfaces (`#101113`, `#1A1C21`), champagne gold leaf anchors (`#E2C066`, `#D4AF37`), and oxidized verdigris patina (`#4A999E`).
- **Grandmaster Board**: Warm bone / ivory lacquer light squares (`#ECE7DC`) against smoky charcoal obsidian dark squares (`#30343C`), with tournament DGT rank/file notation inlaid along the perimeter.
- **Haptic Visual Feedback**: Bilinear anti-aliased piece sprites, subtle gold selection aura, non-intrusive destination indicators (discs for quiet moves, target rings for captures), and a vermilion king-in-check indicator.
- **Interactive HUD & Modals**: An "Engine Evaluating..." pulse indicator during Minimax calculations, an in-place pawn promotion modal, and an overlay game-over dialog with rematch and menu options.

---

## Files Description

1. **`ui_theme.py`**: Centralized theme manager holding design tokens, typography scales, smooth-scaled sprite caches, and modular renderers (`draw_menu`, `draw_board`, `draw_promotion_modal`, `draw_game_over`).
2. **`playchess.py`**: Main application controller orchestrating the event loops, state transitions, human input, AI turns, and match rematches.
3. **`player/AI.py`**: The minimax search engine with alpha-beta pruning, depth-3 lookahead, and board evaluation heuristics.
4. **`board/`**:
   - `chessboard.py`: Board representation holding an 8x8 matrix of `Tile` instances.
   - `move.py`: Move validation, king checks, pinned piece evaluation, castling, and en passant detection.
   - `tile.py`: Individual board square abstraction.
5. **`pieces/`**: Modular class hierarchy (`king`, `queen`, `rook`, `bishop`, `knight`, `pawn`, `nullpiece`) computing legal rays and delta moves.
6. **`chessart/`**: Transparent vector piece art assets and markers.

---

## How to Run Locally

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch the game**:
   ```bash
   python playchess.py
   ```
