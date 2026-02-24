import math
import logging
from typing import List, Dict, Any, Optional

# Set up logger
logger = logging.getLogger("pybite.vision")
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class GestureInterpreter:
    """Interprets hand landmarks into game-specific commands."""
    
    def __init__(self, pinch_threshold: float = 0.02):
        self.pinch_threshold = pinch_threshold
        self._last_direction = None
        
    def get_command(self, landmarks: List[tuple]) -> Dict[str, Any]:
        """
        Analyzes landmarks and returns a command dictionary.
        Landmark indices:
        0: Wrist, 5: Index MCP, 8: Index Tip, 4: Thumb Tip
        """
        if not landmarks:
            return {
                "direction": None,
                "phase": False,
                "boost": False,
                "raw": (0.0, 0.0)
            }
            
        # Use Index MCP (base of index finger) as local origin for direction
        index_mcp = landmarks[5]
        index_tip = landmarks[8]
        thumb_tip = landmarks[4]
        
        # 1. Direction Detection (Relative to Index MCP)
        dx = index_tip[0] - index_mcp[0]
        dy = index_tip[1] - index_mcp[1]

        command = {
            "direction": None,
            "phase": False,
            "boost": False,
            "raw": (dx, dy)
        }
        
        # Pure sensitivity: One axis must be larger than a small deadzone
        # Use a stable threshold (0.03) to filter noise without requiring large moves
        DEADZONE = 0.03
        
        if abs(dx) > DEADZONE or abs(dy) > DEADZONE:
            if abs(dx) > abs(dy):
                command["direction"] = "LEFT" if dx < 0 else "RIGHT"
            else:
                command["direction"] = "UP" if dy < 0 else "DOWN"
                
        # Log direction changes
        if command["direction"] and command["direction"] != self._last_direction:
             logger.info(f"DIRECTION: {command['direction']} (dx={dx:.2e}, dy={dy:.2e})")
             self._last_direction = command["direction"]
                
        # 2. Pinch Detection (Thumb Tip to Index Tip)
        dist = math.sqrt(
            (thumb_tip[0] - index_tip[0])**2 + 
            (thumb_tip[1] - index_tip[1])**2
        )
        
        if dist < self.pinch_threshold:
            command["phase"] = True
            logger.info(f"PHASE ACTIVATED: pinch distance {dist:.4f}")
            
        # 3. Fist Detection (Speed Boost/Restart)
        # Require all 4 main fingers (Index, Middle, Ring, Pinky) to be folded
        # This prevents accidental boosts while steering with the index.
        weighted_tips = [8, 12, 16, 20]
        weighted_mcp = [5, 9, 13, 17]
        
        fingers_folded = True
        wrist = landmarks[0]
        
        for tip_idx, mcp_idx in zip(weighted_tips, weighted_mcp):
            tip = landmarks[tip_idx]
            mcp = landmarks[mcp_idx]
            
            # Distance from tip to wrist vs MCP to wrist
            d_tip = math.sqrt((tip[0]-wrist[0])**2 + (tip[1]-wrist[1])**2)
            d_mcp = math.sqrt((mcp[0]-wrist[0])**2 + (mcp[1]-wrist[1])**2)
            
            # If any tip is further from the wrist than its base MCP, it's not a fist
            if d_tip > d_mcp * 1.1: 
                fingers_folded = False
                break
                
        command["boost"] = fingers_folded
        
        return command
