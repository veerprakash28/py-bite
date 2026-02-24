from typing import List, Optional
from core.event_types import Point, GameCommand

class Snake:
    """Manages snake body, movement, and collision states."""
    
    def __init__(self, start_pos: Point, length: int = 3):
        self.head = start_pos
        # Initial body is segments below the head
        self.body = [Point(start_pos.x, start_pos.y + i) for i in range(length)]
        self.direction = GameCommand.UP
        self._next_direction = GameCommand.UP
        self.growing = False
        
    def set_direction(self, command: GameCommand):
        """Sets the next direction, preventing 180-degree turns."""
        opposites = {
            GameCommand.UP: GameCommand.DOWN,
            GameCommand.DOWN: GameCommand.UP,
            GameCommand.LEFT: GameCommand.RIGHT,
            GameCommand.RIGHT: GameCommand.LEFT
        }
        
        if command in opposites and command != opposites.get(self.direction):
            self._next_direction = command
            
    def move(self):
        """Updates snake body positions based on current direction."""
        self.direction = self._next_direction
        
        new_head = Point(self.head.x, self.head.y)
        if self.direction == GameCommand.UP:
            new_head.y -= 1
        elif self.direction == GameCommand.DOWN:
            new_head.y += 1
        elif self.direction == GameCommand.LEFT:
            new_head.x -= 1
        elif self.direction == GameCommand.RIGHT:
            new_head.x += 1
            
        self.head = new_head
        self.body.insert(0, new_head)
        
        if not self.growing:
            self.body.pop()
        else:
            self.growing = False
            
    def grow(self):
        """Signals the snake to grow on the next move."""
        self.growing = True
        
    def check_collision_with_self(self, phase_active: bool = False) -> bool:
        """Detects if the head overlaps with the rest of the body."""
        if phase_active:
            return False  # Ability allows passing through self
            
        # Check if head matches any body segment EXCEPT the first one (which IS the head)
        for segment in self.body[1:]:
            if self.head.x == segment.x and self.head.y == segment.y:
                return True
        return False
        
    def get_positions(self) -> List[Point]:
        """Returns all coordinates occupied by the snake."""
        return self.body
