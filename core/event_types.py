from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, List, Tuple

class GameCommand(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    PHASE = auto()
    BOOST = auto()
    QUIT = auto()
    RESTART = auto()

class GameStatus(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()

@dataclass
class Point:
    x: int
    y: int

    def __composite_values__(self):
        return self.x, self.y

    def __iter__(self):
        yield self.x
        yield self.y

@dataclass
class GameState:
    """Represents the complete state of the game at any given time."""
    status: GameStatus = GameStatus.MENU
    score: int = 0
    high_score: int = 0
    difficulty: float = 1.0  # Multiplier for speed/difficulty
    
    # Snake position and body
    snake_head: Point = field(default_factory=lambda: Point(10, 10))
    snake_body: List[Point] = field(default_factory=lambda: [Point(10, 10), Point(10, 11), Point(10, 12)])
    snake_direction: GameCommand = GameCommand.UP
    
    # Abilities state
    phase_active: bool = False
    phase_cooldown: float = 0.0  # Remaining cooldown time in seconds
    boost_active: bool = False
    boost_meter: float = 100.0   # Current boost energy
    
    # Grid/Board state
    food_position: Optional[Point] = None
    board_size: Tuple[int, int] = (20, 20)
    
    def reset(self):
        self.status = GameStatus.PLAYING
        self.score = 0
        self.difficulty = 1.0
        self.snake_head = Point(10, 10)
        self.snake_body = [Point(10, 10), Point(10, 11), Point(10, 12)]
        self.snake_direction = GameCommand.UP
        self.phase_active = False
        self.phase_cooldown = 0.0
        self.boost_active = False
        self.boost_meter = 100.0
