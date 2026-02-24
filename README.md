# PyBite – Gesture-Controlled Vision Arcade Game

PyBite is a modular, production-style Python arcade game where you control a snake using hand gestures. It uses OpenCV and MediaPipe for vision tracking and Pygame for the game engine.

## 🚀 Current Status: Core Logic Implemented

The core game engine and domain logic are now implemented. This includes:
- **Grid-based movement** logic.
- **Snake mechanics** (growth, collision).
- **Abilities system** (Phase Mode and Speed Boost).
- **State Management** for game lifecycle.

## 🛠 Project Structure

- `app/`: Entry point and rendering loop (Next up).
- `core/`: State management and shared types.
- `game/`: Pure game logic (Snake, Board, Abilities, Engine).
- `vision/`: MediaPipe gesture detection (Coming soon).
- `tests/`: Unit tests for game mechanics.

## 🧪 How to Test

You can verify the game logic using `pytest`.

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run tests:**
   ```bash
   pytest tests/test_game_logic.py
   ```

## 🎮 Coming Soon
- Hand tracking integration.
- Pygame rendering loop.
- Scoreboard and difficulty scaling.
