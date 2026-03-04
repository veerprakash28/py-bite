# PyBite – Gesture-Controlled Vision Arcade Game

PyBite is a modular, production-style Python arcade game where you control a snake using real-time hand gestures. It leverages MediaPipe for high-performance hand tracking and Pygame for the rendering engine.

## 🚀 Status: Version 1.0 (First Draft) Complete

The project is fully functional and features:
- **Vision-Based Control**: Local finger-tilt detection (Tip vs MCP) for ultra-responsive steering.
- **Advanced Mechanics**: Screen wrapping, Phase Mode (invincibility), and Speed Boosting.
- **Premium UI**: Dedicated sidebar for camera feedback, gesture indicators, and score HUD.
- **Production Architecture**: Modular codebase separating Vision, Domain, and Application layers.

## 🎮 How to Play

### Gesture Controls
- **Steer**: Gently tilt your **index finger** up, down, left, or right relative to your palm.
- **Phase Mode (Ghost)**: **Pinch** your thumb and index finger together to pass through your own tail.
- **Speed Boost**: Make a **full fist** with your hand.
- **Restart**: Make a **full fist** on the Game Over screen.

## 🛠 Project Structure

- `app/`: Main application loop and Pygame rendering.
- `vision/`: MediaPipe tracker and gesture interpretation logic.
- `game/`: Domain logic (Snake, Board, Abilities, and Engine).
- `core/`: Shared event types and state management.

## 🧪 Setup and Execution

1. **Setup Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run PyBite**:
   ```bash
   python app/main.py
   ```

3. **Run Tests**:
   ```bash
   pytest tests/test_game_logic.py
   ```

---
Developed as a demonstration of real-time gesture interpretation and clean software architecture.
