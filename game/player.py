import pygame
from game.maze import CELL

SPEED = 3

class Player:
    def __init__(self, r, c):
        self.r = r
        self.c = c
        x = c*CELL + CELL//2
        y = r*CELL + CELL//2
        self.rect = pygame.Rect(x-10, y-10, 20, 20)
        self.color = (60,120,220)

    def move(self, keys, walls, rows, cols):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = SPEED

        # Wall-aware movement (check cell boundaries)
        new_rect = self.rect.move(dx, 0)
        if not self._hits_wall(new_rect, walls, rows, cols, self.rect):
            self.rect = new_rect
        new_rect = self.rect.move(0, dy)
        if not self._hits_wall(new_rect, walls, rows, cols, self.rect):
            self.rect = new_rect

    def _hits_wall(self, rect, walls, rows, cols, previous_rect):
        # Keep the player inside the maze.
        for px, py in [(rect.left, rect.top),(rect.right-1,rect.top),(rect.left,rect.bottom-1),(rect.right-1,rect.bottom-1)]:
            cr = py // CELL
            cc = px // CELL
            if cr < 0 or cr >= rows or cc < 0 or cc >= cols:
                return True

        # Check the wall crossed by each part of the player's edge.
        if rect.left < previous_rect.left:
            old_col = previous_rect.left // CELL
            new_col = rect.left // CELL
            if new_col < old_col:
                for row in range(rect.top // CELL, (rect.bottom - 1) // CELL + 1):
                    if walls[row][old_col][3]:  # W
                        return True
        elif rect.right > previous_rect.right:
            old_col = (previous_rect.right - 1) // CELL
            new_col = (rect.right - 1) // CELL
            if new_col > old_col:
                for row in range(rect.top // CELL, (rect.bottom - 1) // CELL + 1):
                    if walls[row][old_col][2]:  # E
                        return True

        if rect.top < previous_rect.top:
            old_row = previous_rect.top // CELL
            new_row = rect.top // CELL
            if new_row < old_row:
                for col in range(rect.left // CELL, (rect.right - 1) // CELL + 1):
                    if walls[old_row][col][0]:  # N
                        return True
        elif rect.bottom > previous_rect.bottom:
            old_row = (previous_rect.bottom - 1) // CELL
            new_row = (rect.bottom - 1) // CELL
            if new_row > old_row:
                for col in range(rect.left // CELL, (rect.right - 1) // CELL + 1):
                    if walls[old_row][col][1]:  # S
                        return True
        return False

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)
