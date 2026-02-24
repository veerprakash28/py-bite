import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import cv2
import numpy as np
from typing import Dict, Any

from game.engine import GameEngine
from vision.camera import Camera
from vision.hand_tracker import HandTracker
from vision.gesture_interpreter import GestureInterpreter
from core.event_types import GameStatus, GameCommand

# --- Configuration ---
CELL_SIZE = 30
GRID_SIZE = (20, 20)
WINDOW_WIDTH = GRID_SIZE[0] * CELL_SIZE
WINDOW_HEIGHT = GRID_SIZE[1] * CELL_SIZE + 100 # Extra space for UI
CAMERA_WINDOW_WIDTH = 200 # Small overlay for camera

# Colors
COLOR_BG = (20, 20, 30)
COLOR_SNAKE = (0, 255, 127)
COLOR_SNAKE_HEAD = (255, 255, 255)
COLOR_PHASE = (138, 43, 226) # Purple for phase mode
COLOR_FOOD = (255, 69, 0)
COLOR_UI_TEXT = (200, 200, 200)
COLOR_UI_BAR_BG = (50, 50, 70)
COLOR_BOOST = (0, 191, 255)

class PyBiteApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("PyBite – Gesture Controlled Arcade")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.font_big = pygame.font.SysFont("Arial", 48, bold=True)
        
        # Game & Vision
        self.engine = GameEngine(board_size=GRID_SIZE)
        self.camera = Camera().start()
        self.tracker = HandTracker()
        self.interpreter = GestureInterpreter()
        
        self.running = True
        self.debug_gestures = {}
        
    def _handle_keyboard_fallback(self) -> Dict[str, Any]:
        """Allows keyboard control for testing."""
        keys = pygame.key.get_pressed()
        cmd = {"direction": None, "phase": False, "boost": False}
        
        if keys[pygame.K_UP]: cmd["direction"] = "UP"
        elif keys[pygame.K_DOWN]: cmd["direction"] = "DOWN"
        elif keys[pygame.K_LEFT]: cmd["direction"] = "LEFT"
        elif keys[pygame.K_RIGHT]: cmd["direction"] = "RIGHT"
        
        if keys[pygame.K_SPACE]: cmd["phase"] = True
        if keys[pygame.K_LSHIFT]: cmd["boost"] = True
        if keys[pygame.K_r]: cmd["restart"] = True
            
        return cmd

    def _render_game(self, state):
        self.screen.fill(COLOR_BG)
        
        # 1. Draw Food
        if state.food_position:
            food_rect = (
                state.food_position.x * CELL_SIZE,
                state.food_position.y * CELL_SIZE,
                CELL_SIZE, CELL_SIZE
            )
            pygame.draw.circle(
                self.screen, COLOR_FOOD, 
                (food_rect[0] + CELL_SIZE//2, food_rect[1] + CELL_SIZE//2), 
                CELL_SIZE//2 - 2
            )
        
        # 2. Draw Snake
        snake_color = COLOR_PHASE if state.phase_active else COLOR_SNAKE
        for i, segment in enumerate(state.snake_body):
            rect = (segment.x * CELL_SIZE, segment.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = COLOR_SNAKE_HEAD if i == 0 else snake_color
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            # Inner detail for segments
            pygame.draw.rect(self.screen, (0,0,0), rect, 1, border_radius=5)
            
        # 3. Draw UI
        self._render_ui(state)
        
        # 4. Draw Camera Feedback Overlay
        self._render_camera_overlay()
        
        # 5. Handle States
        if state.status == GameStatus.GAME_OVER:
            self._render_overlay_text("GAME OVER", "Press 'R' or Fist to Restart")
        elif state.status == GameStatus.MENU:
            self._render_overlay_text("PYBITE", "Show Hand to Start")

    def _render_ui(self, state):
        # Background bar
        pygame.draw.rect(self.screen, COLOR_UI_BAR_BG, (0, WINDOW_HEIGHT-100, WINDOW_WIDTH, 100))
        
        # Score
        score_txt = self.font.render(f"Score: {state.score}  |  Level: {int((state.difficulty-1)*10)+1}", True, COLOR_UI_TEXT)
        self.screen.blit(score_txt, (20, WINDOW_HEIGHT-80))
        
        # Phase Cooldown Meter
        cd_width = 150
        pygame.draw.rect(self.screen, (30, 30, 30), (WINDOW_WIDTH - 170, WINDOW_HEIGHT-80, cd_width, 20))
        if state.phase_cooldown <= 0:
            pygame.draw.rect(self.screen, COLOR_PHASE, (WINDOW_WIDTH - 170, WINDOW_HEIGHT-80, cd_width, 20))
        else:
            # Show progress
            progress = 1.0 - (state.phase_cooldown / 10.0)
            pygame.draw.rect(self.screen, (100, 100, 100), (WINDOW_WIDTH - 170, WINDOW_HEIGHT-80, int(cd_width * progress), 20))
        self.screen.blit(self.font.render("PHASE", True, COLOR_UI_TEXT), (WINDOW_WIDTH - 170, WINDOW_HEIGHT - 55))

        # Boost Meter
        pygame.draw.rect(self.screen, (30, 30, 30), (WINDOW_WIDTH - 170, WINDOW_HEIGHT-30, cd_width, 10))
        pygame.draw.rect(self.screen, COLOR_BOOST, (WINDOW_WIDTH - 170, WINDOW_HEIGHT-30, int(cd_width * (state.boost_meter/100)), 10))

    def _render_camera_overlay(self):
        frame = self.camera.read()
        if frame is not None:
            # Draw landmarks for visual feedback
            self.tracker.draw_landmarks(frame)
            
            # Resize for overlay
            frame_small = cv2.resize(frame, (CAMERA_WINDOW_WIDTH, int(CAMERA_WINDOW_WIDTH * 0.75)))
            # Convert BGR to RGB for Pygame
            frame_rgb = cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
            self.screen.blit(frame_surface, (WINDOW_WIDTH - CAMERA_WINDOW_WIDTH - 10, 10))
            
            # Draw gesture status text
            if self.debug_gestures:
                txt = f"Dir: {self.debug_gestures.get('direction')} Boost: {self.debug_gestures.get('boost')}"
                debug_surface = self.font.render(txt, True, (0, 255, 0))
                self.screen.blit(debug_surface, (WINDOW_WIDTH - CAMERA_WINDOW_WIDTH - 10, 160))

    def _render_overlay_text(self, title: str, subtitle: str):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0,0))
        
        title_surf = self.font_big.render(title, True, (255, 255, 255))
        sub_surf = self.font.render(subtitle, True, (200, 200, 200))
        
        self.screen.blit(title_surf, (WINDOW_WIDTH//2 - title_surf.get_width()//2, WINDOW_HEIGHT//3))
        self.screen.blit(sub_surf, (WINDOW_WIDTH//2 - sub_surf.get_width()//2, WINDOW_HEIGHT//3 + 70))

    def run(self):
        self.engine.reset()
        
        while self.running:
            # 1. Input Processing
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            # 2. Vision Processing
            frame = self.camera.read()
            landmarks = []
            if frame is not None:
                self.tracker.find_hands(frame)
                landmarks = self.tracker.get_landmarks()
            
            commands = self.interpreter.get_command(landmarks)
            self.debug_gestures = commands
            
            # Handle Menu/Restart specifically
            if self.engine.state.status != GameStatus.PLAYING:
                if commands.get("boost") or pygame.key.get_pressed()[pygame.K_r]:
                    self.engine.reset()

            # Merge with keyboard fallback
            kb_commands = self._handle_keyboard_fallback()
            for key, val in kb_commands.items():
                if val: commands[key] = val
            
            # 3. Game Engine Update
            self.engine.process_command(commands)
            self.engine.update()
            
            # 4. Rendering
            self._render_game(self.engine.state)
            pygame.display.flip()
            
            self.clock.tick(30)
            
        self.camera.stop()
        pygame.quit()

if __name__ == "__main__":
    app = PyBiteApp()
    app.run()
