import sys
import os
import time

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
GRID_WIDTH = GRID_SIZE[0] * CELL_SIZE
GRID_HEIGHT = GRID_SIZE[1] * CELL_SIZE
SIDEBAR_WIDTH = 250
WINDOW_WIDTH = GRID_WIDTH + SIDEBAR_WIDTH
WINDOW_HEIGHT = GRID_HEIGHT + 100 
CAMERA_DISPLAY_WIDTH = 220

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
        self._ready_to_restart = False
        
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
            self._render_overlay_text("GAME OVER", "Wait 1s then Fist to Restart")
        elif state.status == GameStatus.MENU:
            self._render_overlay_text("PYBITE", "Show Hand to Start")
            
        # 6. Flash effect for PHASE mode
        if state.phase_active:
             flash = pygame.Surface((GRID_WIDTH, GRID_HEIGHT), pygame.SRCALPHA)
             flash.fill((138, 43, 226, 40)) # Translucent purple
             self.screen.blit(flash, (0,0))

    def _render_ui(self, state):
        # Background bar
        pygame.draw.rect(self.screen, COLOR_UI_BAR_BG, (0, GRID_HEIGHT, WINDOW_WIDTH, 100))
        
        # Score
        score_txt = self.font.render(f"S: {state.score}", True, COLOR_UI_TEXT)
        self.screen.blit(score_txt, (10, GRID_HEIGHT + 20))
        level_txt = self.font.render(f"L: {int((state.difficulty-1)*10)+1}", True, COLOR_UI_TEXT)
        self.screen.blit(level_txt, (10, GRID_HEIGHT + 55))
        
        # Phase Cooldown Meter
        cd_width = 150
        meter_x = WINDOW_WIDTH - 170
        pygame.draw.rect(self.screen, (30, 30, 30), (meter_x, GRID_HEIGHT + 20, cd_width, 20))
        if state.phase_cooldown <= 0:
            pygame.draw.rect(self.screen, COLOR_PHASE, (meter_x, GRID_HEIGHT + 20, cd_width, 20))
        else:
            progress = 1.0 - (state.phase_cooldown / 10.0)
            pygame.draw.rect(self.screen, (100, 100, 100), (meter_x, GRID_HEIGHT + 20, int(cd_width * progress), 20))
        self.screen.blit(self.font.render("PHASE", True, COLOR_UI_TEXT), (meter_x, GRID_HEIGHT + 45))

        # Boost Meter
        pygame.draw.rect(self.screen, (30, 30, 30), (meter_x, GRID_HEIGHT + 70, cd_width, 10))
        pygame.draw.rect(self.screen, COLOR_BOOST, (meter_x, GRID_HEIGHT + 70, int(cd_width * (state.boost_meter/100)), 10))

        # --- Gesture Indicators ---
        self._render_gesture_indicators()

    def _render_gesture_indicators(self):
        """Draws visual icons for detected gestures in the bottom panel."""
        panel_y = GRID_HEIGHT + 10
        start_x = 100
        spacing = 45
        
        # Show raw offsets for debugging direction issues
        if self.debug_gestures and "raw" in self.debug_gestures:
             raw = self.debug_gestures["raw"]
             off_txt = f"dx: {raw[0]:.2f} dy: {raw[1]:.2f}"
             off_surf = pygame.font.SysFont("Arial", 12).render(off_txt, True, (255, 255, 0))
             self.screen.blit(off_surf, (WINDOW_WIDTH // 2 - 30, GRID_HEIGHT + 80))

        gestures = [
            ("↑", "direction", "UP"),
            ("↓", "direction", "DOWN"),
            ("←", "direction", "LEFT"),
            ("→", "direction", "RIGHT"),
            ("P", "phase", True),
            ("B", "boost", True)
        ]
        
        for i, (label, key, active_val) in enumerate(gestures):
            is_active = self.debug_gestures.get(key) == active_val
            color = (255, 255, 255) if is_active else (80, 80, 100)
            bg_color = (0, 200, 0) if is_active else (40, 40, 60)
            
            rect = (start_x + i * spacing, panel_y, 40, 40)
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
            
            txt_surf = self.font.render(label, True, color)
            self.screen.blit(txt_surf, (rect[0] + 20 - txt_surf.get_width()//2, rect[1] + 20 - txt_surf.get_height()//2))
            
            # Label below icons
            hint_map = {"UP": "Dir", "DOWN": " ", "LEFT": " ", "RIGHT": " ", "phase": "PHASE", "boost": "BST"}
            hint = hint_map.get(active_val if key == "direction" else key, "")
            if hint:
                hint_surf = pygame.font.SysFont("Arial", 12).render(hint, True, COLOR_UI_TEXT)
                self.screen.blit(hint_surf, (rect[0] + 20 - hint_surf.get_width()//2, rect[1] + 45))

    def _render_camera_overlay(self):
        frame = self.camera.read()
        sidebar_x = GRID_WIDTH + (SIDEBAR_WIDTH - CAMERA_DISPLAY_WIDTH) // 2
        
        # Draw Sidebar background for contrast
        pygame.draw.rect(self.screen, (10, 10, 20), (GRID_WIDTH, 0, SIDEBAR_WIDTH, GRID_HEIGHT))
        pygame.draw.line(self.screen, (50, 50, 70), (GRID_WIDTH, 0), (GRID_WIDTH, GRID_HEIGHT), 2)

        if frame is not None:
            # Draw landmarks for visual feedback
            self.tracker.draw_landmarks(frame)
            
            # Resize for sidebar
            frame_small = cv2.resize(frame, (CAMERA_DISPLAY_WIDTH, int(CAMERA_DISPLAY_WIDTH * 0.75)))

            # Convert BGR to RGB for Pygame
            frame_rgb = cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
            self.screen.blit(frame_surface, (sidebar_x, 20))
            
            # Draw gesture status text in sidebar
            if self.debug_gestures:
                dir_txt = f"Direction: {self.debug_gestures.get('direction') or 'None'}"
                boost_txt = f"Boost: {'ACTIVE' if self.debug_gestures.get('boost') else 'Off'}"
                
                dir_surf = self.font.render(dir_txt, True, (0, 255, 0))
                bst_surf = self.font.render(boost_txt, True, (0, 191, 255))
                
                self.screen.blit(dir_surf, (sidebar_x, 190))
                self.screen.blit(bst_surf, (sidebar_x, 220))
                
        # Instructions legend
        legend_y = 280
        legend_items = [
            ("Index vs Wrist", "Move Snake"),
            ("Pinch", "PHASE Mode"),
            ("Fist", "Speed Boost"),
            ("Fist (Over)", "Restart Game")
        ]
        for i, (act, res) in enumerate(legend_items):
            pygame.draw.circle(self.screen, (0, 255, 0), (sidebar_x + 10, legend_y + i*45 + 10), 4)
            a_surf = pygame.font.SysFont("Arial", 14, bold=True).render(act, True, (255,255,255))
            r_surf = pygame.font.SysFont("Arial", 14).render(res, True, (150,150,150))
            self.screen.blit(a_surf, (sidebar_x + 25, legend_y + i*45))
            self.screen.blit(r_surf, (sidebar_x + 25, legend_y + i*45 + 18))

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
            
            # Handle Menu/Restart with debounce and 1s safety delay
            if self.engine.state.status != GameStatus.PLAYING:
                # Add a cooldown so they don't instant-restart
                if not hasattr(self, "_game_over_time"):
                    self._game_over_time = time.time()
                
                # User must release the fist/R key and then press it again after 1s
                if not commands.get("boost") and not pygame.key.get_pressed()[pygame.K_r]:
                    self._ready_to_restart = True
                    
                if self._ready_to_restart and (time.time() - self._game_over_time > 1.5):
                    if commands.get("boost") or pygame.key.get_pressed()[pygame.K_r]:
                        print("Restarting game via gesture/key...")
                        self.engine.reset()
                        self._ready_to_restart = False
                        delattr(self, "_game_over_time")
            else:
                if hasattr(self, "_game_over_time"):
                    delattr(self, "_game_over_time")

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
