
import pygame
from pygame import Rect, Surface
import time

CELL = 36
PADDING = 16

COLORS = {
    "bg": (30, 30, 34),
    "grid": (60, 60, 66),
    "wall": (90, 90, 100),
    "alpha": (70, 170, 255),
    "bravo": (255, 110, 90),
    "flag": (255, 215, 0),
    "text": (230, 230, 235),
    "alpha_base": (60, 120, 255),
    "bravo_base": (255, 80, 60),
    "scout": (90, 200, 120),
    "attacker": (255, 170, 60),
    "defender": (160, 120, 255),
}

def draw_grid(screen, rows, cols, offset_x, offset_y):
    w = cols * CELL
    h = rows * CELL
    for r in range(rows + 1):
        y = offset_y + r * CELL
        pygame.draw.line(screen, COLORS["grid"], (offset_x, y), (offset_x + w, y), 1)
    for c in range(cols + 1):
        x = offset_x + c * CELL
        pygame.draw.line(screen, COLORS["grid"], (x, offset_y), (x, offset_y + h), 1)

def draw_text(screen, font, text, x, y):
    s = font.render(text, True, COLORS["text"])
    screen.blit(s, (x, y))

def draw_world(screen, arena, font, turn, trails, heat_counts, show_heat=True, show_trails=3):
    screen.fill(COLORS["bg"])
    rows, cols = arena.rows, arena.cols
    HEADER_H = 72  # reserved header pixels to prevent overlap with grid
    ox, oy = PADDING, PADDING + HEADER_H

    # Header background bar
    header_w = cols * CELL
    header_surf = Surface((header_w, HEADER_H), pygame.SRCALPHA)
    header_surf.fill((0, 0, 0, 80))  # subtle translucent overlay
    screen.blit(header_surf, (PADDING, PADDING))

    if show_heat:
        max_count = max((v for row in heat_counts for v in row), default=1)
        if max_count < 1:
            max_count = 1
        for r in range(rows):
            for c in range(cols):
                v = heat_counts[r][c]
                if v:
                    alpha = min(160, int(255 * (v / max_count) * 0.6))
                    if alpha > 10:
                        surf = Surface((CELL, CELL), pygame.SRCALPHA)
                        surf.fill((255, 255, 255, alpha))
                        screen.blit(surf, (ox + c * CELL, oy + r * CELL))

    draw_grid(screen, rows, cols, ox, oy)

    for r in range(rows):
        for c in range(cols):
            ch = arena.grid[r][c]
            cell_rect = Rect(ox + c * CELL, oy + r * CELL, CELL, CELL)
            if ch == "#":
                pygame.draw.rect(screen, COLORS["wall"], cell_rect)
            elif ch == "A":
                pygame.draw.rect(screen, COLORS["alpha_base"], cell_rect, 2)
            elif ch == "B":
                pygame.draw.rect(screen, COLORS["bravo_base"], cell_rect, 2)

    for team, flag in arena.flags.items():
        fr, fc = flag.position
        cx = ox + fc * CELL + CELL // 2
        cy = oy + fr * CELL + CELL // 2
        pygame.draw.circle(screen, COLORS["flag"], (cx, cy), CELL // 4)

# --- Draw agent trails (fading "crumbs") ---
    if show_trails > 0:
        for agent in arena.agents:
            pts = trails.get(agent.state.name, [])
            if len(pts) < 2:
                continue
            # color by team
            color = COLORS["alpha"] if agent.state.team == "Team Alpha" else COLORS["bravo"]
            # convert to pixel coordinates
            pixel_pts = [(ox + c * CELL + CELL // 2, oy + r * CELL + CELL // 2) for (r, c) in pts]
            sample = pixel_pts[-show_trails:]
            n = len(sample)
            # draw small fading dots; older points are more transparent
            for i, (x, y) in enumerate(sample):
                t = (i + 1) / n  # 0..1
                alpha = int(255 * t)
                dot = Surface((CELL, CELL), pygame.SRCALPHA)
                pygame.draw.circle(dot, (*color, alpha), (CELL // 2, CELL // 2), max(2, CELL // 10))
                screen.blit(dot, (x - CELL // 2, y - CELL // 2))

    for agent in arena.agents:
        r, c = agent.state.position
        cx = ox + c * CELL + CELL // 2
        cy = oy + r * CELL + CELL // 2
        fill = COLORS.get(agent.state.role, (200,200,200))
        ring = COLORS["alpha"] if agent.state.team == "Team Alpha" else COLORS["bravo"]
        pygame.draw.circle(screen, ring, (cx, cy), CELL // 3 + 2)
        pygame.draw.circle(screen, fill, (cx, cy), CELL // 3)
        role_letter = {"scout": "S", "attacker": "T", "defender": "D"}.get(agent.state.role, "?")
        role_surf = font.render(role_letter, True, (0, 0, 0))
        rs = role_surf.get_rect(center=(cx, cy))
        screen.blit(role_surf, rs)

    scores = arena.scoreboard.snapshot()
    score_str = f"Turn {turn} | Scores: Alpha {scores.get('Team Alpha',0)}  –  Bravo {scores.get('Team Bravo',0)}"
    draw_text(screen, font, score_str, PADDING, PADDING + 8)

    evt = getattr(arena, "_last_event", None)
    if evt:
        if evt.get("type") == "tag":
            txt = f"⚔️  {evt['agent']} tagged {evt.get('target','?')} (t{evt['tick']})"
        elif evt.get("type") == "pickup_flag":
            txt = f"🏁  {evt['agent']} picked up the flag (t{evt['tick']})"
        elif evt.get("type") == "capture":
            txt = f"🎉  {evt['agent']} captured for {evt.get('team')} (t{evt['tick']})"
        else:
            txt = f"Event @ t{evt.get('tick','?')}"
        draw_text(screen, font, txt, PADDING, PADDING + 34)

    draw_text(screen, font, "Space: Pause/Resume   N: Step   H: Toggle Heatmap   T: Cycle Trail Length   C: Clear Trails", PADDING, oy + rows*CELL + 10)

def run_pygame_loop(arena, step_callback, max_turns=200, delay=0.15):
    rows, cols = arena.rows, arena.cols
    w = cols * CELL + PADDING * 2
    h = rows * CELL + PADDING * 2 + 90
    pygame.init()
    screen = pygame.display.set_mode((w, h))
    pygame.display.set_caption("Multi-Agent CTF — Renderer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)

    running = True
    paused = False
    show_heat = True
    show_trails = 3
    turn = 0
    trails = {}
    heat_counts = [[0 for _ in range(cols)] for _ in range(rows)]

    while running and turn < max_turns:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_n:
                    if paused:
                        turn += 1
                        step_callback(turn)
                elif event.key == pygame.K_h:
                    show_heat = not show_heat
                elif event.key == pygame.K_t:
                    show_trails = (show_trails + 1) % 4
                elif event.key == pygame.K_c:
                    trails.clear()
                    for r in range(rows):
                        for c in range(cols):
                            heat_counts[r][c] = 0

        if not paused:
            turn += 1
            step_callback(turn)

        for a in arena.agents:
            r, c = a.state.position
            trails.setdefault(a.state.name, []).append((r, c))
            if len(trails[a.state.name]) > 50:
                trails[a.state.name].pop(0)
            if 0 <= r < rows and 0 <= c < cols:
                heat_counts[r][c] += 1

        draw_world(screen, arena, font, turn, trails, heat_counts, show_heat=show_heat, show_trails=show_trails)
        pygame.display.flip()
        clock.tick(60)
        time.sleep(delay if not paused else 0.02)

    pygame.quit()
