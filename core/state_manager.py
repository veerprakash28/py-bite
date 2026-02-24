from core.event_types import GameStatus, GameState

class StateManager:
    """Manages high-level game states and state transitions."""
    
    def __init__(self):
        self.state = GameState()
        
    def start_game(self):
        """Transition from MENU or GAME_OVER to PLAYING."""
        self.state.reset()
        self.state.status = GameStatus.PLAYING
        
    def pause_toggle(self):
        """Toggle between PLAYING and PAUSED."""
        if self.state.status == GameStatus.PLAYING:
            self.state.status = GameStatus.PAUSED
        elif self.state.status == GameStatus.PAUSED:
            self.state.status = GameStatus.PLAYING
            
    def end_game(self):
        """Transition to GAME_OVER."""
        self.state.status = GameStatus.GAME_OVER
        if self.state.score > self.state.high_score:
            self.state.high_score = self.state.score
            
    def update_score(self, points: int):
        """Increase the current score and check difficulty scaling."""
        self.state.score += points
        # Difficulty scaling logic: increase difficulty every 50 points
        self.state.difficulty = 1.0 + (self.state.score // 50) * 0.1
        
    def get_current_state(self) -> GameState:
        """Returns the current game state."""
        return self.state
