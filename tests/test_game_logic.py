import pytest
from core.event_types import Point, GameCommand, GameStatus
from game.snake import Snake
from game.board import Board
from game.engine import GameEngine

def test_snake_movement():
    start_pos = Point(10, 10)
    snake = Snake(start_pos)
    
    # Initial move UP
    snake.set_direction(GameCommand.UP)
    snake.move()
    assert snake.head.y == 9
    assert snake.body[0].y == 9
    assert len(snake.body) == 3

def test_snake_growth():
    snake = Snake(Point(10, 10))
    initial_length = len(snake.body)
    
    snake.grow()
    snake.move()
    assert len(snake.body) == initial_length + 1

def test_collision_detection():
    board = Board(size=(20, 20))
    assert board.is_within_bounds(Point(10, 10)) == True
    assert board.is_within_bounds(Point(25, 10)) == False

def test_engine_game_over_wall():
    engine = GameEngine(board_size=(10, 10))
    engine.reset()
    engine.state.status = GameStatus.PLAYING
    
    # Force snake to the edge
    engine.snake.head = Point(0, 0)
    engine.snake.set_direction(GameCommand.LEFT)
    
    # Should collide with wall on next move
    engine._do_move()
    assert engine.state.status == GameStatus.GAME_OVER

def test_phase_ability():
    engine = GameEngine(board_size=(20, 20))
    engine.reset()
    
    # Activate phase
    engine.process_command({"phase": True})
    assert engine.state.phase_active == True
    
    # Verify it allows self-collision
    # (Setting body to a loop)
    engine.snake.body = [Point(10, 10), Point(10, 11), Point(11, 11), Point(11, 10), Point(10, 10)]
    engine.snake.head = Point(10, 10)
    
    assert engine.snake.check_collision_with_self(phase_active=True) == False
    assert engine.snake.check_collision_with_self(phase_active=False) == True
