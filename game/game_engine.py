import os
import pygame
import random
from .target import Target

# Game Engine

WHITE = (255, 255, 255)
RED = (220, 60, 60)


class GameEngine:
    def __init__(self, width, height):
        self.exit_requested = False
        self.width = width
        self.height = height

        self.margin = 60
        self.hud_height = 60

        self.round_seconds = 30
        self.difficulty = "Medium"

        self.hits = 0
        self.misses = 0
        self.score = 0

        self.font = pygame.font.SysFont("Arial", 26)
        self.game_over = False

        assets_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "assets"
        )

        self.hit_sound = pygame.mixer.Sound(
            os.path.join(assets_dir, "hit.wav")
        )

        self.miss_sound = pygame.mixer.Sound(
            os.path.join(assets_dir, "miss.wav")
        )

        self.timeout_sound = pygame.mixer.Sound(
            os.path.join(assets_dir, "timeout.wav")
        )

        self.round_end_sound = pygame.mixer.Sound(
            os.path.join(assets_dir, "round_end.wav")
        )

        self._start_round(self.difficulty)

    def _difficulty_settings(self):
        return {
            "Easy": (45, 15, 120),
            "Medium": (40, 12, 90),
            "Hard": (35, 10, 60),
        }[self.difficulty]

    def _start_round(self, difficulty):
        self.difficulty = difficulty

        base_radius, min_radius, lifespan_frames = self._difficulty_settings()

        self.hits = 0
        self.misses = 0
        self.score = 0

        self.time_left_frames = self.round_seconds * 60
        self.game_over = False
        self.exit_requested = False

        self.target = self._spawn_target(
            base_radius,
            min_radius,
            lifespan_frames
        )

    def _spawn_target(self, base_radius, min_radius, lifespan_frames):
        x = random.randint(
            self.margin,
            self.width - self.margin
        )
        y = random.randint(
            self.margin + self.hud_height,
            self.height - self.margin
        )

        return Target(
            x,
            y,
            base_radius=base_radius,
            min_radius=min_radius,
            lifespan_frames=lifespan_frames
        )

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self._start_round("Easy")
                elif event.key == pygame.K_2:
                    self._start_round("Medium")
                elif event.key == pygame.K_3:
                    self._start_round("Hard")
                elif event.key == pygame.K_4 or event.key == pygame.K_ESCAPE:
                    self.exit_requested = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_menu_click(event.pos)

            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_click(event.pos)

    def _handle_menu_click(self, pos):
        x, y = pos

        center_x = self.width // 2

        if center_x - 120 <= x <= center_x + 120:
            if self.height // 2 - 20 <= y <= self.height // 2 + 20:
                self._start_round("Easy")

            elif self.height // 2 + 30 <= y <= self.height // 2 + 70:
                self._start_round("Medium")

            elif self.height // 2 + 80 <= y <= self.height // 2 + 120:
                self._start_round("Hard")

            elif self.height // 2 + 130 <= y <= self.height // 2 + 170:
                self.exit_requested = True

    def _handle_click(self, pos):
        x, y = pos

        if self.target.contains_point(x, y):
            self.hits += 1
            self.score += 1
            self.hit_sound.play()

            self.target = self._spawn_target(
                *self._difficulty_settings()
            )
        else:
            self.misses += 1
            self.miss_sound.play()

    def handle_input(self):
        # Reserved for continuously-held-key input.
        pass

    def update(self):
        if self.game_over:
            return

        self.time_left_frames -= 1

        if self.time_left_frames <= 0:
            self.game_over = True
            self.round_end_sound.play()
            return

        self.target.update()

        if self.target.expired():
            self.misses += 1
            self.timeout_sound.play()

            self.target = self._spawn_target(
                *self._difficulty_settings()
            )

    def accuracy(self):
        total = self.hits + self.misses

        if total == 0:
            return 0.0

        return round(100 * self.hits / total, 1)

    def render(self, screen):
        if self.game_over:
            self._render_game_over(screen)
            return

        r = int(self.target.visual_radius())

        pygame.draw.circle(
            screen,
            RED,
            (self.target.x, self.target.y),
            r
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (self.target.x, self.target.y),
            r,
            2
        )

        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            WHITE
        )
        screen.blit(score_text, (10, 10))

        seconds_left = max(
            0,
            self.time_left_frames // 60
        )

        timer_text = self.font.render(
            f"Time: {seconds_left}s",
            True,
            WHITE
        )
        screen.blit(
            timer_text,
            (self.width - 140, 10)
        )

        acc_text = self.font.render(
            f"Accuracy: {self.accuracy()}%",
            True,
            WHITE
        )
        screen.blit(
            acc_text,
            (self.width // 2 - 90, 10)
        )

    def _render_game_over(self, screen):
        center_x = self.width // 2
        center_y = self.height // 2

        texts = [
            ("GAME OVER", center_y - 150),
            (f"Final Score: {self.score}", center_y - 110),
            (f"Accuracy: {self.accuracy()}%", center_y - 75),
            ("Choose Difficulty", center_y - 20),
            ("1. Easy", center_y + 10),
            ("2. Medium", center_y + 55),
            ("3. Hard", center_y + 100),
            ("4. Exit", center_y + 145),
        ]

        for text, y in texts:
            rendered = self.font.render(
                text,
                True,
                WHITE
            )

            screen.blit(
                rendered,
                rendered.get_rect(
                    center=(center_x, y)
                )
            )