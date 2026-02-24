import time
from typing import Dict, Any
from core.event_types import GameState, GameStatus, GameCommand, Point
from core.state_manager import StateManager
from game.board import Board
from game.snake import Snake
from game.abilities import PhaseAbility, BoostAbility

class GameEngine:
    """Orchestrates game logic updates based on commands."""
    
    def __init__(self, board_size: tuple = (20, 20)):
        self.state_manager = StateManager()
        self.board = Board(size=board_size)
        
        # Initialize GameState with board size
        self.state = self.state_manager.get_current_state()
        self.state.board_size = board_size
        
        self.snake = None
        self.phase_ability = PhaseAbility()
        self.boost_ability = BoostAbility()
        
        self.last_update_time = time.time()
        self.move_timer = 0.0
        self.base_move_delay = 0.3  # Seconds between moves at difficulty 1.0
        
    def reset(self):
        self.state_manager.start_game()
        self.snake = Snake(self.board.get_center())
        self.state.food_position = self.board.get_random_empty_position(self.snake.get_positions())
        self.last_update_time = time.time()
        
    def process_command(self, commands: Dict[str, Any]):
        """
        Interprets a command dictionary from vision or keyboard.
        Expected format: {"direction": "UP"|..., "phase": bool, "boost": bool}
        """
        if self.state.status != GameStatus.PLAYING:
            if commands.get("restart"):
                self.reset()
            return

        # Direction mapping
        dir_cmd = commands.get("direction")
        if dir_cmd:
            if isinstance(dir_cmd, str):
                try:
                    self.snake.set_direction(GameCommand[dir_cmd])
                except KeyError:
                    pass
            elif isinstance(dir_cmd, GameCommand):
                self.snake.set_direction(dir_cmd)
                
        # Abilities
        if commands.get("phase"):
            self.phase_ability.activate()
            
        self.state.boost_active = bool(commands.get("boost"))
        
    def update(self):
        """Main update logic called every frame."""
        if self.state.status != GameStatus.PLAYING:
            return
            
        now = time.time()
        dt = now - self.last_update_time
        self.last_update_time = now
        
        # Update abilities
        self.boost_ability.update(dt, self.state.boost_active)
        self.state.phase_active = self.phase_ability.is_active
        self.state.phase_cooldown = self.phase_ability.cooldown_remaining
        self.state.boost_meter = self.boost_ability.energy
        
        # Calculate movement timing
        speed_multiplier = self.state.difficulty
        if self.state.boost_active and self.boost_ability.is_active:
            speed_multiplier *= 2.0
            
        current_move_delay = self.base_move_delay / speed_multiplier
        self.move_timer += dt
        
        if self.move_timer >= current_move_delay:
            self.move_timer -= current_move_delay
            self._do_move()
            
    def _do_move(self):
        """Performs a single movement step."""
        self.snake.move()
        head = self.snake.head
        
        # 1. Check Wall Collision
        if not self.board.is_within_bounds(head):
            self.state_manager.end_game()
            return
            
        # 2. Check Self Collision
        if self.snake.check_collision_with_self(self.state.phase_active):
            self.state_manager.end_game()
            return
            
        # 3. Check Food Consumption
        if head.x == self.state.food_position.x and head.y == self.state.food_position.y:
            self.snake.grow()
            self.state_manager.update_score(10)
            self.state.food_position = self.board.get_random_empty_position(self.snake.get_positions())
            
        # Sync simple fields to state for UI view
        self.state.snake_head = head
        self.state.snake_body = list(self.snake.body)
        self.state.snake_direction = self.snake.direction
