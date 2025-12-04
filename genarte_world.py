# draw_lines_save_npy.py
import pygame
import sys
from pathlib import Path
import numpy as np

# --- Config ---
WIDTH, HEIGHT = 600, 400
BG_COLOR = (30, 30, 30)
LINE_COLOR = (255, 200, 0)
PREVIEW_COLOR = (200, 200, 200)
LINE_WIDTH = 3
SAVE_FILE = Path("lines.npy")   # NumPy binary file

# --- State ---
lines = []             # list of ((x1,y1), (x2,y2))
drawing = False
start_pos = None
current_pos = None

# Try to load existing lines if file exists
if SAVE_FILE.exists():
    try:
        arr = np.load(SAVE_FILE)
        # arr shape expected: (N, 2, 2) -> [[ [x1,y1], [x2,y2] ], ...]
        lines = [((int(a[0]), int(a[1])), (int(b[0]), int(b[1]))) for a, b in arr]
        print(f"Loaded {len(lines)} lines from {SAVE_FILE}")
    except Exception as e:
        print("Could not load existing lines:", e)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Draw lines — hold LMB to draw, ESC to quit, C to clear")

def save_lines_to_npy(path: Path, lines_list):
    """Save lines as a numpy array with shape (N,2,2) dtype=int32."""
    if not lines_list:
        # save an empty array with shape (0,2,2)
        np.save(path, np.zeros((0,2,2), dtype=np.int32))
        return
    arr = np.array([[[a[0], a[1]], [b[0], b[1]]] for a,b in lines_list], dtype=np.int32)
    np.save(path, arr)

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                running = False
            if e.key == pygame.K_c:   # clear lines (and file)
                lines.clear()
                if SAVE_FILE.exists():
                    SAVE_FILE.unlink()
                print("Cleared all lines and deleted save file (if it existed).")

        elif e.type == pygame.MOUSEBUTTONDOWN:
            # Start drawing on left mouse button
            if e.button == 1:
                drawing = True
                start_pos = e.pos
                current_pos = e.pos

        elif e.type == pygame.MOUSEMOTION:
            if drawing:
                current_pos = e.pos

        elif e.type == pygame.MOUSEBUTTONUP:
            # Finish drawing on left mouse button
            if e.button == 1 and drawing and start_pos is not None:
                end_pos = e.pos
                lines.append((start_pos, end_pos))
                # autosave
                try:
                    save_lines_to_npy(SAVE_FILE, lines)
                    print(f"Saved line {start_pos} -> {end_pos} (total lines: {len(lines)})")
                except Exception as err:
                    print("Error saving lines:", err)
                # reset drawing state
                drawing = False
                start_pos = None
                current_pos = None

    # Draw
    screen.fill(BG_COLOR)

    # draw all finished lines
    for a, b in lines:
        pygame.draw.line(screen, LINE_COLOR, a, b, LINE_WIDTH)

    # draw preview line while dragging
    if drawing and start_pos and current_pos:
        pygame.draw.line(screen, PREVIEW_COLOR, start_pos, current_pos, 1)

    pygame.display.flip()
    clock.tick(60)

# ensure final save before exit
try:
    save_lines_to_npy(SAVE_FILE, lines)
except Exception:
    pass

pygame.quit()
sys.exit()
