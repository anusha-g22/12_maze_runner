import pygame
import time
import json
import math
from pathlib import Path
from game.maze import generate_maze, shortest_path, CELL
from game.player import Player

FPS = 60
BG = (240, 235, 220)
WALL_COLOR = (40, 40, 60)
EXIT_COLOR = (80, 200, 80)
MENU_SIZE = (600, 580)

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(MENU_SIZE)
        pygame.display.set_caption("Maze Runner")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 22)
        self.big_font = pygame.font.SysFont("monospace", 36, bold=True)
        self.difficulties = {"Easy": (10, 8), "Medium": (15, 13), "Hard": (20, 18)}
        self.selected_difficulty = None
        self.awaiting_difficulty = True
        self.leaderboard_file = Path(__file__).resolve().parent.parent / "leaderboard.json"
        self.leaderboard = self._load_leaderboard()

    def _start_difficulty(self, name):
        self.selected_difficulty = name
        self.cols, self.rows = self.difficulties[name]
        self.width = self.cols * CELL
        self.maze_height = self.rows * CELL
        self.height = self.maze_height + 60
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.awaiting_difficulty = False
        self.reset()

    def _load_leaderboard(self):
        if not self.leaderboard_file.exists():
            self.leaderboard_file.write_text("[]\n", encoding="utf-8")
            return []
        try:
            content = self.leaderboard_file.read_text(encoding="utf-8")
            entries = json.loads(content) if content.strip() else []
        except (OSError, json.JSONDecodeError):
            return []

        if not isinstance(entries, list):
            return []
        times = [float(value) for value in entries
                 if isinstance(value, (int, float)) and not isinstance(value, bool)
                 and math.isfinite(value) and value >= 0]
        times = sorted(times)[:5]
        self.leaderboard_file.write_text(
            json.dumps(times, indent=2) + "\n", encoding="utf-8"
        )
        return times

    def _record_completion(self, elapsed):
        self.leaderboard = sorted(self.leaderboard + [float(elapsed)])[:5]
        self.leaderboard_file.write_text(
            json.dumps(self.leaderboard, indent=2) + "\n", encoding="utf-8"
        )

    def reset(self):
        self.walls = generate_maze(self.cols, self.rows)
        self.player = Player(0, 0)
        self.exit_rect = pygame.Rect((self.cols-1)*CELL+5, (self.rows-1)*CELL+5, CELL-10, CELL-10)
        self.start_time = time.time()
        self.elapsed = 0
        self.won = False
        self.show_hint = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if self.awaiting_difficulty and event.type == pygame.KEYDOWN:
                difficulty_keys = {
                    pygame.K_1: "Easy",
                    pygame.K_2: "Medium",
                    pygame.K_3: "Hard",
                }
                if event.key in difficulty_keys:
                    self._start_difficulty(difficulty_keys[event.key])
                continue
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                self.show_hint = not self.show_hint
        return True

    def update(self):
        if self.awaiting_difficulty or self.won:
            return
        keys = pygame.key.get_pressed()
        self.player.move(keys, self.walls, self.rows, self.cols)
        self.elapsed = time.time() - self.start_time
        if self.player.rect.colliderect(self.exit_rect):
            self.elapsed = time.time() - self.start_time
            self.won = True
            self._record_completion(self.elapsed)

    def draw_maze(self):
        wall_w = 3
        for r in range(self.rows):
            for c in range(self.cols):
                x, y = c*CELL, r*CELL
                w = self.walls[r][c]
                if w[0]: pygame.draw.line(self.screen, WALL_COLOR, (x,y), (x+CELL,y), wall_w)
                if w[1]: pygame.draw.line(self.screen, WALL_COLOR, (x,y+CELL), (x+CELL,y+CELL), wall_w)
                if w[2]: pygame.draw.line(self.screen, WALL_COLOR, (x+CELL,y), (x+CELL,y+CELL), wall_w)
                if w[3]: pygame.draw.line(self.screen, WALL_COLOR, (x,y), (x,y+CELL), wall_w)

    def draw_fog(self):
        player_col = self.player.rect.centerx // CELL
        player_row = self.player.rect.centery // CELL
        fog = pygame.Surface((self.width, self.maze_height), pygame.SRCALPHA)
        fog.fill((8, 10, 20, 235))
        for r in range(self.rows):
            for c in range(self.cols):
                if (r - player_row) ** 2 + (c - player_col) ** 2 <= 3 ** 2:
                    visible_cell = pygame.Rect(c * CELL, r * CELL, CELL, CELL)
                    fog.fill((0, 0, 0, 0), visible_cell)
        self.screen.blit(fog, (0, 0))

    def draw(self):
        self.screen.fill(BG)
        if self.awaiting_difficulty:
            title = self.big_font.render("Select Difficulty", True, WALL_COLOR)
            self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 110))
            for index, (name, (cols, rows)) in enumerate(self.difficulties.items(), start=1):
                option = self.font.render(f"{index}. {name}  ({cols} x {rows})", True, WALL_COLOR)
                self.screen.blit(option, (self.screen.get_width()//2 - option.get_width()//2, 210 + (index - 1) * 55))
            hint = self.font.render("Press 1, 2, or 3 to start", True, (80, 80, 80))
            self.screen.blit(hint, (self.screen.get_width()//2 - hint.get_width()//2, 410))
            pygame.display.flip()
            return
        if self.show_hint:
            player_col, player_row = self.player.rect.centerx // CELL, self.player.rect.centery // CELL
            goal = (self.rows - 1, self.cols - 1)
            path = shortest_path(self.walls, (player_row, player_col), goal)
            for r, c in path:
                path_rect = pygame.Rect(c * CELL + 7, r * CELL + 7, CELL - 14, CELL - 14)
                pygame.draw.rect(self.screen, (245, 205, 70), path_rect, border_radius=4)
        self.draw_maze()
        pygame.draw.rect(self.screen, EXIT_COLOR, self.exit_rect, border_radius=4)
        ex_label = self.font.render("EXIT", True, (20,80,20))
        self.screen.blit(ex_label, (self.exit_rect.x+2, self.exit_rect.y+4))
        self.draw_fog()
        self.player.draw(self.screen)

        hud = pygame.Rect(0, self.maze_height, self.width, 60)
        pygame.draw.rect(self.screen, (30,30,50), hud)
        time_surf = self.font.render(f"Time: {self.elapsed:.1f}s   R = New Maze", True, (200,200,200))
        self.screen.blit(time_surf, (10, self.maze_height+18))

        if self.won:
            overlay = pygame.Surface((self.width, self.maze_height), pygame.SRCALPHA)
            overlay.fill((0,0,0,120))
            self.screen.blit(overlay, (0,0))
            msg = self.big_font.render(f"Solved in {self.elapsed:.1f}s!", True, (80,240,80))
            heading = self.font.render("Best Times", True, (240,220,120))
            rows = [
                self.font.render(f"{index + 1}. {completion_time:.1f}s", True, (230,230,230))
                for index, completion_time in enumerate(self.leaderboard)
            ]
            sub = self.font.render("Press R for a new maze", True, (200,200,200))
            row_gap = 3
            content_height = (
                msg.get_height() + 8 + heading.get_height() + 4
                + sum(row.get_height() for row in rows)
                + row_gap * max(0, len(rows) - 1) + 8 + sub.get_height()
            )
            y = max(8, (self.maze_height - content_height) // 2)
            self.screen.blit(msg, (self.width//2 - msg.get_width()//2, y))
            y += msg.get_height() + 8
            self.screen.blit(heading, (self.width//2 - heading.get_width()//2, y))
            y += heading.get_height() + 4
            for index, row in enumerate(rows):
                self.screen.blit(row, (self.width//2 - row.get_width()//2, y))
                y += row.get_height()
                if index < len(rows) - 1:
                    y += row_gap
            y += 8
            self.screen.blit(sub, (self.width//2 - sub.get_width()//2, y))
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
