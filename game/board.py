import random
from typing import Tuple, List, Optional
from core.event_types import Point

class Board:
    """Handles the grid-based board logic and object placement."""
    
    def __init__(self, size: Tuple[int, int] = (20, 20)):
        self.width, self.height = size
        
    def get_random_empty_position(self, occupied_positions: List[Point]) -> Point:
        """Finds a random position on the grid not occupied by the snake."""
        all_positions = [
            Point(x, y) 
            for x in range(self.width) 
            for y in range(self.height)
        ]
        
        # Convert occupied to a set of tuples for faster lookup if needed, 
        # but for small grids a list is fine.
        empty_positions = [
            p for p in all_positions 
            if p not in occupied_positions
        ]
        
        if not empty_positions:
            return Point(-1, -1)  # Should not happen in normal gameplay
            
        return random.choice(empty_positions)
        
    def is_within_bounds(self, point: Point) -> bool:
        """Checks if a point is within the board limits."""
        return 0 <= point.x < self.width and 0 <= point.y < self.height
        
    def get_center(self) -> Point:
        """Helper to get the middle of the board for initial placement."""
        return Point(self.width // 2, self.height // 2)
