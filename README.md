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

## 🧪 How to Setup and Test

It is recommended to use a virtual environment to keep dependencies isolated.

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   ```

2. **Activate the environment:**
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the game:**
   ```bash
   python app/main.py
   ```

5. **Run tests:**
   ```bash
   pytest tests/test_game_logic.py
   ```

## 🎮 Coming Soon
- Hand tracking integration.
- Pygame rendering loop.
- Scoreboard and difficulty scaling.
